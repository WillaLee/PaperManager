from rest_framework import serializers
from .models import Summary, Label, Paper

class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ['id', 'content', 'latex_format']

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['name']

class PaperSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True)  # Nested labels serializer
    summary = SummarySerializer()  # Nested summary serializer

    class Meta:
        model = Paper
        fields = ['id', 'title', 'labels', 'summary', 'file']