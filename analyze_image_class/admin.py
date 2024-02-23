from django.contrib import admin
from .models import ImageAnalysisResult

@admin.register(ImageAnalysisResult)
class ImageAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('image_path', 'success', 'message', 'class_id', 'confidence', 'request_timestamp', 'response_timestamp')
    list_filter = ('success', 'request_timestamp', 'response_timestamp')
    search_fields = ('image_path', 'message')