from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FileUpload, PaymentTransaction, ActivityLog



# core/serializers.py
class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['id', 'user', 'file', 'upload_time', 'status', 'word_count']
        read_only_fields = ['id', 'user', 'upload_time', 'status', 'word_count']
    
    def validate_file(self, value):
        # Check file extension
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ['.txt', '.docx']:
            raise serializers.ValidationError("Only .txt and .docx files are allowed.")
        
        # Check file size (limit to 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(f"File size exceeds 10MB limit.")
        
        return value
    
    def create(self, validated_data):
        # Get the file from validated data
        file_obj = validated_data['file']
        
        # Set the filename from the file object
        validated_data['filename'] = file_obj.name
        validated_data['user'] = self.context['request'].user
        
        return super().create(validated_data)
    
class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ['id', 'user', 'transaction_id', 'amount', 'status', 'gateway_response', 'timestamp']
        read_only_fields = ['id', 'user', 'timestamp']

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'action', 'metadata', 'timestamp']
        read_only_fields = ['id', 'user', 'timestamp']