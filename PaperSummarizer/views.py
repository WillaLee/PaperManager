from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser
from django.http import HttpResponse
from django.contrib.postgres.search import TrigramSimilarity
import fitz


from .models import Paper, Summary, Label
from .serializers import PaperSerializer, SummarySerializer, LabelSerializer

class SummaryViewSet(viewsets.ModelViewSet):
    queryset = Summary.objects.all()
    serializer_class = SummarySerializer

class PaperViewSet(viewsets.ModelViewSet):
    queryset = Paper.objects.all()
    serializer_class = PaperSerializer
    parser_classes = (MultiPartParser, )

    def create(self, request):
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the uploaded file from request.FILES
        pdf_file = request.FILES['file']

        if not pdf_file.name.endswith('.pdf'):
            return Response({"error": "Uploaded file is not a PDF"}, status=status.HTTP_400_BAD_REQUEST)
        
        pdf_bytes = pdf_file.read()
        
        # create a paper object
        Paper.objects.create(title=pdf_file.name, file=pdf_file)
        
        try:
            # Process the PDF with PyMuPDF
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                extracted_text = ""
                for page in doc:
                    extracted_text += page.get_text()
            
            return Response({"text": extracted_text}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # function to retrieve papers by label name
    @action(detail=False, methods=['get'], url_path='retrieve-by-label-name/(?P<label_name>[^/.]+)')
    def retrieve_papers_by_label_name(self, request, label_name=None):
        try:
            label = Label.objects.get(name=label_name)
        except Label.DoesNotExist:
            return Response({"detail": "Label not found"}, status=404)

        # Filter papers by the associated label
        papers = Paper.objects.filter(label=label)

        # Serialize the papers
        serializer = PaperSerializer(papers, many=True)

        return Response(serializer.data)
    
    # function to add the summary of a paper as a string
    @action(detail=True, methods=['put'], url_path='add-summary')
    def add_summary(self, request, pk=None):
        if "summary" not in request.data:
            return Response({"error": "No summary provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        paper = self.get_object()
        summary_data = request.data.get("summary")

        if paper.summary:
            paper.summary.content = summary_data
            paper.summary.save()
        else:
            new_summary = Summary.objects.create(content=summary_data)
            paper.summary = new_summary
            paper.save()

        return Response({"message": "Successfully add summary."}, status=201)   

    # function for retrieving the summary of a paper as a string
    @action(detail=True, methods=['get'], url_path='get-summary')
    def get_summary(self, request, pk=None):
        paper = self.get_object()
        summary = paper.summary
        if summary:
            return Response({"summary": summary.content})
        return Response({"message": "No summary avaliable! Please try again."}, status=404)   
    
    # function for getting summary in LaTeX format
    @action(detail=True, methods=['get'], url_path='get-summary-latex')
    def get_summary_latex(self, request, pk=None):
        paper = self.get_object()
        summary = paper.summary
        
        if summary:
            latex_content = summary.get_or_update_latex_format() # This ensures that if latex_format doesn't exist, it will be generated
            response = HttpResponse(latex_content, content_type='application/x-tex')
            response['Content-Disposition'] = f'attachment; filename="summary_{paper.id}.tex"'
            return response
        
        return Response({"message": "No summary available. Please try again."}, status=404)

    
    # function to search for existing labels related to this paper)
    @action(detail=True, methods=['get'], url_path='related-labels')
    def fuzzy_search_labels(self, request, pk=None):
        paper = self.get_object()
        if not paper.key_words:
            return Response({"error": "No keywords available"}, status=404)

        search_terms = [t.strip() for t in paper.key_words.split(',') if t.strip()]
        threshold = float(request.query_params.get("threshold", 0.2))  # Default 0.2
        labels = Label.objects.annotate(
            similarity=TrigramSimilarity('name', Value(' '.join(search_terms)))
        ).filter(similarity__gt=threshold).order_by('-similarity')[:10]

        return Response(LabelSerializer(labels, many=True).data)
    
    # Implement function to get keywords of this paper
    @action(detail=True, methods=['get'], url_path='get-keywords')
    def get_keywords(self, request, pk=None):
        try:
            paper = self.get_object()
            
            # Get raw keywords string from the paper
            raw_keywords = paper.key_words
            
            # Process keywords into a clean list
            if not raw_keywords:  # Handles None or empty string
                return Response([], status=status.HTTP_200_OK)
                
            # Split, clean, and filter keywords
            processed_keywords = [
                kw.strip() 
                for kw in raw_keywords.split(',') 
                if kw.strip()  # Remove empty strings
            ]
            
            return Response(processed_keywords, status=status.HTTP_200_OK)
        
        except Paper.DoesNotExist:
            return Response(
                {"error": "Paper not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    #add a label to a paper
    @action(detail=True, methods=['put'], url_path='add-label')
    def add_label(self, request, pk=None):
        paper = self.get_object()
        label_id = request.data.get('label_id')
        
        if not label_id:
            return Response({"error": "label_id required"}, status=400)
            
        try:
            label = Label.objects.get(id=label_id)
            if not paper.labels.filter(id=label_id).exists():
                paper.labels.add(label)
                return Response(PaperSerializer(paper).data, status=200)
            return Response({"message": "Label already added"}, status=400)
        except Label.DoesNotExist:
            return Response({"error": "Label not found"}, status=404)

    #remove a label from a paper
    @action(detail=True, methods=['put'], url_path='remove-label')
    def remove_label(self, request, pk=None):
        paper = self.get_object()
        label_id = request.data.get('label_id')

        if not label_id:
            return Response({"error": "label_id required"}, status=400)

        try:
            label = Label.objects.get(id=label_id)
            if paper.labels.filter(id=label_id).exists():
                paper.labels.remove(label)
                return Response(PaperSerializer(paper).data, status=200)
            return Response({"message": "Label not found on this paper"}, status=400)
        except Label.DoesNotExist:
            return Response({"error": "Label not found"}, status=404)

        
class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer