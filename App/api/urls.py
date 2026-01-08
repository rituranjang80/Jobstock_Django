from django.urls import path

from .resume_management import RPOResumeUploadAPI
from .process_resumes import RPOProcessResumesAPI

urlpatterns = [
    path('rpo/resume-upload/', RPOResumeUploadAPI.as_view(), name='rpo_resume_upload_api'),
    path('rpo/process-resumes/', RPOProcessResumesAPI.as_view(), name='rpo_process_resumes_api'),
]
