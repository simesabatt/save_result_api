from django.urls import path
from .views import ImageAnalysisView, ExportImageAnalysisResultsCSVView

urlpatterns = [
    path('', ImageAnalysisView.as_view(), name='analyze-image'),
    path('export-csv/', ExportImageAnalysisResultsCSVView.as_view(), name='export-csv'),
]
