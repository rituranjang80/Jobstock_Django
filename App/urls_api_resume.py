"""
API URLs for Resume Upload functionality
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from App.views.api_resume_views import (
    api_upload_resumes,
    api_get_resumes,
    api_delete_resume,
    api_get_statistics,
    api_validate_files,
    rpo_resume_download
)
from App.api.dropdown_crud_router import DropdownGroupViewSet, DropdownMasterViewSet

router = DefaultRouter()
router.register(r'dropdowns/groups', DropdownGroupViewSet, basename='dropdown-group')
router.register(r'dropdowns/masters', DropdownMasterViewSet, basename='dropdown-master')

urlpatterns = [
    path('upload/', api_upload_resumes, name='api_upload_resumes'),
    path('list/', api_get_resumes, name='api_get_resumes'),
    path('<int:resume_id>/delete/', api_delete_resume, name='api_delete_resume'),
    path('statistics/', api_get_statistics, name='api_get_statistics'),
    path('validate/', api_validate_files, name='api_validate_files'),
    path('rpo-resume-download/<int:resume_id>/', rpo_resume_download, name='rpo_resume_download'),
    path('rpo/resume-list/', __import__('App.api.rpo_resume_list_api').api.rpo_resume_list_api.RPOResumeListAPI.as_view(), name='api_rpo_resume_list'),
    path('dropdown/', __import__('App.api.dropdown_router').api.dropdown_router.DropdownListAPI.as_view(), name='api_dropdown_list'),
    path('', include(router.urls)),
]
