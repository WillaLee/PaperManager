from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, JSONParser
from django.http import HttpResponse, FileResponse
from django.contrib.postgres.search import TrigramSimilarity
from django.conf import settings
import fitz
from rapidfuzz import process, fuzz
import os
import soundfile as sf
from kokoro_onnx import Kokoro

from .models import Paper, Summary, Label
from .serializers import PaperSerializer, SummarySerializer, LabelSerializer
from ChatBot.chatbot import Chatbot # Import chatbot'

class SummaryViewSet(viewsets.ModelViewSet):
    queryset = Summary.objects.all()
    serializer_class = SummarySerializer

class PaperViewSet(viewsets.ModelViewSet):
    queryset = Paper.objects.all()
    serializer_class = PaperSerializer
    parser_classes = (MultiPartParser, JSONParser,)

    def create(self, request):
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the uploaded file from request.FILES
        pdf_file = request.FILES['file']

        if not pdf_file.name.endswith('.pdf'):
            return Response({"error": "Uploaded file is not a PDF"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Initialize chatbot
            chatbot = Chatbot()
            
            # Add pdf to AnythingLLM workspace's RAG
            chatbot.add_paper_to_rag(pdf_file)

            # generate summary
            summary_content = chatbot.get_summary(pdf_file.name)
            # generate keywords
            key_words = chatbot.get_keywords(pdf_file.name)

            # Recommended label in the end of the summary
            summary_content += "\n\n\n"
            summary_content += "\nRecommended label:"
            summary_content += f"\n{', '.join(key_words)}"  # Converts list to string
            # create a paper object
            paper = Paper.objects.create(title=pdf_file.name, file=pdf_file, key_words=key_words)
            paper.update_summary(summary_content)
            paper.save()
            
            return Response({"paper_id": paper.id}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # function to update the paper
    def update(self, request, pk=None):
        paper = self.get_object()
        
        # update title
        if "title" in request.data:
            title = request.data.get("title")
            paper.title = title
            paper.save()

        return Response({"id": paper.id}, status=201)    
        
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

    # function for retrieving the labels of a paper
    @action(detail=True, methods=['get'], url_path='get-labels')
    def get_labels(self, request, pk=None):
        paper = self.get_object()
        labels = paper.labels
        if labels:
            serialized_labels = LabelSerializer(labels, many=True).data
            return Response({"labels": serialized_labels})
        return Response({"message": "No summary avaliable! Please try again."}, status=404)   

    # function to search for existing labels related to this paper)
    @action(detail=True, methods=['get'], url_path='related-labels')
    def fuzzy_search_labels(self, request, pk=None):
        paper = self.get_object()
        key_words = paper.key_words
        
        if not key_words:
            return Response({"error": "No keywords available"}, status=status.HTTP_404_NOT_FOUND)

        all_labels = list(Label.objects.values_list('name', flat=True))
        
        threshold = int(request.query_params.get("threshold", 70))
        
        matched_labels = set()
        for keyword in key_words:
            results = process.extract(
                keyword, 
                all_labels,
                scorer=fuzz.partial_ratio,
                score_cutoff=threshold
            )
            matched_labels.update([result[0] for result in results])

        labels = Label.objects.filter(name__in=matched_labels)
        
        return Response(LabelSerializer(labels, many=True).data)
    
    # Implement function to get keywords of this paper
    @action(detail=True, methods=['get'], url_path='get-keywords')
    def get_keywords(self, request, pk=None):
        try:
            paper = self.get_object()
            
            # Get raw keywords string from the paper
            keywords = paper.key_words
            
            # Process keywords into a clean list
            if not keywords:  # Handles None or empty string
                return Response([], status=status.HTTP_200_OK)
            
            return Response(keywords, status=status.HTTP_200_OK)
        
        except Paper.DoesNotExist:
            return Response(
                {"error": "Paper not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    #add a label to a paper
    @action(detail=True, methods=['put'], url_path='add-label')
    def add_label(self, request, pk=None):
        paper = self.get_object()
        label_name = request.data.get('name')
        
        if not label_name:
            return Response({"error": "label_name required"}, status=400)
            
        try:
            label = Label.objects.get(name=label_name)
            if not paper.labels.filter(name=label_name).exists():
                paper.labels.add(label)
                return Response(PaperSerializer(paper).data, status=200)
            return Response({"message": "Label already added"}, status=400)
        except Label.DoesNotExist:
            return Response({"error": "Label not found"}, status=404)

    #remove a label from a paper
    @action(detail=True, methods=['put'], url_path='remove-label')
    def remove_label(self, request, pk=None):
        paper = self.get_object()
        label_name = request.data.get('name')

        if not label_name:
            return Response({"error": "label_name required"}, status=400)

        try:
            label = Label.objects.get(name=label_name)
            if paper.labels.filter(name=label_name).exists():
                paper.labels.remove(label)
                return Response(PaperSerializer(paper).data, status=200)
            return Response({"message": "Label not found on this paper"}, status=400)
        except Label.DoesNotExist:
            return Response({"error": "Label not found"}, status=404)
    
    # convert summary into speech
    @action(detail=True, methods=['get'], url_path='summary-to-speech')
    def summary_to_speech(self, request, pk=None):
        paper = self.get_object()
        if not paper.summary:
            return Response({"error": "No summary provided! Please try again"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            model_path = os.path.join(settings.BASE_DIR, "kokoro-v1.0.onnx")
            voices_path = os.path.join(settings.BASE_DIR, "voices-v1.0.bin")

            kokoro = Kokoro(model_path, voices_path)
            samples, sample_rate = kokoro.create(
                paper.summary.content, voice="af_sarah", speed=1.0, lang="en-us"
            )
            output_file = "audio.wav"
            sf.write(output_file, samples, sample_rate)

            # Return the audio file as a response
            response = FileResponse(open(output_file, 'rb'), content_type='audio/wav')
            response['Content-Disposition'] = f'attachment; filename="{output_file}"'

            # Optionally, delete the file after sending
            os.remove(output_file)

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer