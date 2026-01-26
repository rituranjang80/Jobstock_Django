"""
API URLs for Resume Upload functionality
"""
from django.urls import path
from App.views.api_resume_views import (
    api_upload_resumes,
    api_get_resumes,
    api_delete_resume,
    api_get_statistics,
    api_validate_files
    , api_rpo_resume_download
)

urlpatterns = [
    path('upload/', api_upload_resumes, name='api_upload_resumes'),
    path('list/', api_get_resumes, name='api_get_resumes'),
    path('<int:resume_id>/delete/', api_delete_resume, name='api_delete_resume'),
    path('statistics/', api_get_statistics, name='api_get_statistics'),
    path('validate/', api_validate_files, name='api_validate_files'),
    path('download/<int:resume_id>/', api_rpo_resume_download, name='api_rpo_resume_download'),
]
