from django.db import models

class ImageAnalysisResult(models.Model):
    image_path = models.CharField(max_length=255)
    success = models.BooleanField(default=False)
    message = models.CharField(max_length=255, null=True, blank=True)
    class_id = models.IntegerField(null=True, blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    request_timestamp = models.DateTimeField(auto_now_add=True)
    response_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.image_path} - Success: {self.success}"
    
    class Meta:
        verbose_name = "画像分析結果"
        verbose_name_plural = "画像分析結果"
        ordering = ['-request_timestamp']
