from django.urls import path
from .resume_management import RPOResumeUploadAPI

urlpatterns = [
    path('rpo/resume-upload/', RPOResumeUploadAPI.as_view(), name='rpo_resume_upload_api'),
]
