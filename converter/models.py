from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField() # in bytes
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.original_filename} ({self.file_size} bytes)"

class ConversionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversions')
    input_file = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, related_name='input_conversions')
    output_file = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, related_name='output_conversions')
    conversion_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='PENDING') # PENDING, PROCESSING, SUCCESS, FAILED
    execution_time = models.FloatField(default=0.0) # in seconds
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.conversion_type} ({self.status})"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - Read: {self.is_read}"
