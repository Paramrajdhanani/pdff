from rest_framework import serializers
from converter.models import Document, ConversionHistory

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'original_filename', 'file_size', 'created_at']

class ConversionHistorySerializer(serializers.ModelSerializer):
    input_file = DocumentSerializer(read_only=True)
    output_file = DocumentSerializer(read_only=True)

    class Meta:
        model = ConversionHistory
        fields = ['id', 'conversion_type', 'status', 'execution_time', 'input_file', 'output_file', 'created_at']
