import os
from celery import shared_task
from django.conf import settings
from .models import FileUpload

@shared_task
def process_file_word_count_with_content(file_upload_id):
    try:
        file_upload = FileUpload.objects.get(id=file_upload_id)
        
        # Get the file path
        file_path = os.path.join(settings.MEDIA_ROOT, file_upload.file.name)
        
        # Check if file exists and is accessible
        if not os.path.exists(file_path):
            file_upload.status = 'failed'
            file_upload.error_message = 'File not found'
            file_upload.save()
            return
        
        # Process the file with proper error handling
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                word_count = len(content.split())
                
                file_upload.word_count = word_count
                file_upload.content = content
                file_upload.status = 'completed'
                file_upload.save()
        except PermissionError:
            file_upload.status = 'failed'
            file_upload.error_message = 'Permission denied when accessing file'
            file_upload.save()
        except Exception as e:
            file_upload.status = 'failed'
            file_upload.error_message = str(e)
            file_upload.save()
            
    except FileUpload.DoesNotExist:
        return