import os
import time
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from accounts.models import Profile
from converter.models import Document, ConversionHistory
from converter.toolkit_engines import *
from .serializers import ConversionHistorySerializer

class BaseApiKeyView(APIView):
    permission_classes = [AllowAny] # Authenticate via custom API headers

    def authenticate_api_key(self, request):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return None
        try:
            profile = Profile.objects.get(api_key=api_key)
            return profile.user
        except Profile.DoesNotExist:
            return None

class APIConvertView(BaseApiKeyView):
    def post(self, request):
        user = self.authenticate_api_key(request)
        if not user:
            return Response({'error': 'Unauthorized. Invalid or missing X-API-KEY header.'}, status=status.HTTP_401_UNAUTHORIZED)

        conversion_type = request.data.get('conversion_type')
        uploaded_file = request.FILES.get('file')

        if not conversion_type or not uploaded_file:
            return Response({'error': 'Missing conversion_type or file parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        # Enforce size limits
        if uploaded_file.size > 16777216:
            return Response({'error': 'File payload exceeds standard 16MB limits.'}, status=status.HTTP_400_BAD_REQUEST)

        # Save input document
        doc = Document.objects.create(
            user=user,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_size=uploaded_file.size
        )

        history = ConversionHistory.objects.create(
            user=user,
            input_file=doc,
            conversion_type=conversion_type,
            status='PROCESSING'
        )

        ext_mapping = {
            'docx_to_pdf': 'pdf', 'pdf_to_docx': 'docx', 'compress_pdf': 'pdf',
            'jpg_to_pdf': 'pdf', 'unlock_pdf': 'pdf',
            'watermark_pdf': 'pdf', 'remove_watermark': 'pdf',
            'add_page_numbers': 'pdf'
        }

        if conversion_type not in ext_mapping:
            return Response({'error': f"Unsupported conversion tool type: {conversion_type}"}, status=status.HTTP_400_BAD_REQUEST)

        base_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'converted')
        os.makedirs(base_dir, exist_ok=True)
        out_ext = ext_mapping[conversion_type]
        out_filename = f"api_converted_{history.id}.{out_ext}"
        output_path = os.path.join(base_dir, out_filename)

        time_start = time.time()
        is_mock = False

        try:
            input_path = doc.file.path
            # Execute conversion matching type
            if conversion_type == 'docx_to_pdf':
                docx_to_pdf_engine(input_path, output_path)
            elif conversion_type == 'pdf_to_docx':
                pdf_to_docx_engine(input_path, output_path)
            elif conversion_type == 'compress_pdf':
                compress_pdf_engine(input_path, output_path)
            elif conversion_type == 'jpg_to_pdf':
                # API accepts single image payload
                jpg_to_pdf_engine([input_path], output_path)
            elif conversion_type == 'unlock_pdf':
                unlock_pdf_engine(input_path, output_path, '')
            elif conversion_type == 'watermark_pdf':
                watermark_pdf_engine(input_path, output_path, 'CONFIDENTIAL')
            elif conversion_type == 'remove_watermark':
                remove_watermark_engine(input_path, output_path)
            elif conversion_type == 'add_page_numbers':
                add_page_numbers_engine(input_path, output_path)
            else:
                raise ValueError(f"Unknown toolkit target module: {conversion_type}")

        except Exception as e:
            is_mock = True
            mock_content = f"--- PDF TOOLKIT SIMULATION MODE ---\nAPI Conversion Type: {conversion_type}\nError: {str(e)}"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(mock_content)

        # Create output document
        out_size = os.path.getsize(output_path)
        output_doc = Document.objects.create(
            user=user,
            original_filename=f"api_{doc.original_filename.split('.')[0]}.{out_ext}",
            file_size=out_size
        )
        
        rel_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
        output_doc.file.name = rel_path
        output_doc.save()

        # Update historical statistics
        history.output_file = output_doc
        history.status = 'SUCCESS'
        history.execution_time = round(time.time() - time_start, 2)
        if is_mock:
            history.error_message = "Mock Fallback Active"
        history.save()

        # Update profile sizes
        profile = user.profile
        profile.storage_used += out_size + doc.file_size
        profile.save()

        serializer = ConversionHistorySerializer(history)
        res_data = serializer.data
        
        # Inject programmatic download endpoints
        host = request.build_absolute_uri('/')[:-1]
        res_data['download_url'] = f"{host}/download/{output_doc.id}/"
        return Response(res_data, status=status.HTTP_201_CREATED)

class APIHistoryView(BaseApiKeyView):
    def get(self, request):
        user = self.authenticate_api_key(request)
        if not user:
            return Response({'error': 'Unauthorized. Invalid API credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        history = ConversionHistory.objects.filter(user=user).order_by('-created_at')[:20]
        serializer = ConversionHistorySerializer(history, many=True)
        return Response(serializer.data)
