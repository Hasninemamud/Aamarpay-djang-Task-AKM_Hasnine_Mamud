import os
from celery import shared_task
from docx import Document
from .models import FileUpload, ActivityLog

# core/tasks.py
@shared_task
def process_file_word_count_with_content(file_upload_id):
    try:
        file_upload = FileUpload.objects.get(id=file_upload_id)
        filename = file_upload.file.name
        file_ext = os.path.splitext(filename)[1].lower()

        word_count = 0

        if file_ext == '.txt':
            with open(file_upload.file.path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            word_count = len(content.split())

        elif file_ext == '.docx':
            doc = Document(file_upload.file.path)
            word_count = sum(len(para.text.split()) for para in doc.paragraphs)
        else:
            file_upload.status = 'failed'
            file_upload.save()
            ActivityLog.objects.create(
                user=file_upload.user,
                action='file_processing_failed',
                metadata={'file_id': file_upload.id, 'filename': filename, 'error': 'Unsupported file format'}
            )
            return

        file_upload.word_count = word_count
        file_upload.status = 'completed'
        file_upload.save()

        ActivityLog.objects.create(
            user=file_upload.user,
            action='file_processed',
            metadata={'file_id': file_upload.id, 'filename': filename, 'word_count': word_count}
        )

    except Exception as e:
        if 'file_upload' in locals():
            file_upload.status = 'failed'
            file_upload.save()
            ActivityLog.objects.create(
                user=file_upload.user,
                action='file_processing_failed',
                metadata={'file_id': file_upload.id,}
            )
