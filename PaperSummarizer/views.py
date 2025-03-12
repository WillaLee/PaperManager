from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.http import HttpResponse, JsonResponse
import fitz

from .models import Summary, Paper, Label
from .serializers import SummarySerializer, PaperSerializer, LabelSerializer

class SummaryViewSet(viewsets.ModelViewSet):
    queryset = Summary.objects.all()
    serializer_class = SummarySerializer

class PaperViewSet(viewsets.ModelViewSet):
    queryset = Paper.objects.all()
    serializer_class = PaperSerializer

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

    # function for retrieving the summary of a paper as a string
    @action(detail=True, methods=['get'], url_path='get-summary')
    def get_summary(self, request, pk=None):
        # TODO: Implement the logic to retrieve the summary of a paper
        summary = Summary.objects.first()  # Just an example
        return Response({"summary": "Summary of the paper."})
    
    # function for getting summary in LaTeX format
    @action(detail=True, methods=['get'], url_path='get-summary-latex')
    def get_summary_latex(self, request, pk=None):
        try:
            # Retrieve the paper by ID
            paper = self.get_object()  # Fetch paper using the pk

            # Assuming Paper model has a relationship with Summary
            summary = paper.summary  # Retrieve the summary related to this paper

            # Check if summary exists and return its LaTeX format
            if summary and summary.latex_format:
                response = HttpResponse(summary.latex_format, content_type='application/x-tex')
                response['Content-Disposition'] = f'attachment; filename="summary_{paper.id}.tex"'
                return response
            else:
                return Response({"message": "No summary available. Please try again."}, status=404)
        
        except Paper.DoesNotExist:
            return Response({"message": "Paper not found."}, status=404)
    
    # function to search for existing labels related to this paper
    @action(detail=True, methods=['post'], url_path='search-labels')
    def fuzzy_search_labels_by_keywords(self, request, pk=None):
        try:
            # Fetch the paper using the paper ID (pk is the paper ID)
            paper = self.get_object()

            # Get the key_words from the paper model
            key_words = paper.key_words

            # Perform fuzzy search for labels related to these key words
            # TODO: Implement fuzzy search logic
            # For now, assume that we're just returning some labels with a dummy filter
            labels = Label.objects.filter(name__icontains="sample")  # Dummy filter to show structure

            # Serialize the labels to return as response
            label_serializer = LabelSerializer(labels, many=True)
            return Response(label_serializer.data, status=status.HTTP_200_OK)
        
        except Paper.DoesNotExist:
            return Response({"error": "Paper not found"}, status=status.HTTP_404_NOT_FOUND)
        
    # TODO: implement the function to add a label to a paper
    @action(detail=True, methods=['post'], url_path='add-label')
    def add_label(self, request, pk=None):
        try:
            # Get the paper object by primary key (pk)
            paper = self.get_object()

            # Extract label ID from the request
            label_id = request.data.get('label_id')

            # Find the label by ID
            label = Label.objects.get(id=label_id)

            # Add the label to the paper's label list
            paper.label.add(label)

            # Return response with updated paper data
            paper_serializer = PaperSerializer(paper)
            return Response(paper_serializer.data, status=status.HTTP_200_OK)

        except Paper.DoesNotExist:
            return Response({"error": "Paper not found"}, status=status.HTTP_404_NOT_FOUND)
        except Label.DoesNotExist:
            return Response({"error": "Label not found"}, status=status.HTTP_404_NOT_FOUND)

    # TODO: implement the function to to remove a label from a paper
    @action(detail=True, methods=['post'], url_path='remove-label')
    def remove_label(self, request, pk=None):
        try:
            # Get the paper object by primary key (pk)
            paper = self.get_object()

            # Extract label ID from the request
            label_id = request.data.get('label_id')

            # Find the label by ID
            label = Label.objects.get(id=label_id)

            # Remove the label from the paper's label list
            paper.label.remove(label)

            # Return response with updated paper data
            paper_serializer = PaperSerializer(paper)
            return Response(paper_serializer.data, status=status.HTTP_200_OK)

        except Paper.DoesNotExist:
            return Response({"error": "Paper not found"}, status=status.HTTP_404_NOT_FOUND)
        except Label.DoesNotExist:
            return Response({"error": "Label not found"}, status=status.HTTP_404_NOT_FOUND)

class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer

# function to accept a PDF and return the text
@api_view(['POST'])
def upload_and_extract_text(request):
    # TODO: Implement the logic to accept a PDF and return the text
    return Response({"Text": "Text of the paper."})