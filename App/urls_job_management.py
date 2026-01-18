"""
URL Configuration for Job Management
Includes both MVT (template) and API routes
"""
from django.urls import path, include

# Import MVT views
from App.views.job_mvt_views import (
    job_list_view, job_detail_view, job_apply_view,
    employer_dashboard_view, job_post_create_view, job_post_edit_view,
    job_deactivate_view, job_reactivate_view,
    job_applications_view, application_detail_view, application_update_status_view,
    job_analytics_ajax, bulk_application_status_ajax
)

# Import API views
from App.views.job_api_views import (
    JobAPI, JobDetailAPI, JobCreateAPI, JobUpdateAPI, JobDeleteAPI,
    MyJobsAPI, JobAnalyticsAPI,
    job_publish_to_boards_api, job_sync_to_boards_api, job_fetch_external_applications_api,
    job_apply_api, job_applications_api, application_detail_api,
    application_update_status_api, applications_bulk_update_status_api,
    external_application_webhook
)

# MVT URLs (Django Templates)
mvt_patterns = [
    # Public job pages
    path('jobs/', job_list_view, name='job_list'),
    path('jobs/<int:job_id>/', job_detail_view, name='job_detail'),
    path('jobs/<int:job_id>/apply/', job_apply_view, name='job_apply'),
    
    # Employer dashboard
    path('employer/dashboard/', employer_dashboard_view, name='employer_dashboard'),
    path('employer/jobs/create/', job_post_create_view, name='job_create'),
    path('employer/jobs/<int:job_id>/edit/', job_post_edit_view, name='job_edit'),
    path('employer/jobs/<int:job_id>/deactivate/', job_deactivate_view, name='job_deactivate'),
    path('employer/jobs/<int:job_id>/reactivate/', job_reactivate_view, name='job_reactivate'),
    
    # Application management
    path('employer/jobs/<int:job_id>/applications/', job_applications_view, name='job_applications'),
    path('employer/applications/<int:application_id>/', application_detail_view, name='application_detail'),
    path('employer/applications/<int:application_id>/status/', application_update_status_view, name='update_application_status'),
    
    # AJAX endpoints
    path('ajax/jobs/<int:job_id>/analytics/', job_analytics_ajax, name='job_analytics_ajax'),
    path('ajax/applications/bulk-status/', bulk_application_status_ajax, name='bulk_application_status'),
]

# REST API URLs
api_patterns = [
    # Job endpoints
    path('jobs/', JobAPI.as_view(), name='api_job_list'),
    path('jobs/<int:job_id>/', JobDetailAPI.as_view(), name='api_job_detail'),
    path('jobs/create/', JobCreateAPI.as_view(), name='api_job_create'),
    path('jobs/<int:job_id>/update/', JobUpdateAPI.as_view(), name='api_job_update'),
    path('jobs/<int:job_id>/delete/', JobDeleteAPI.as_view(), name='api_job_delete'),
    path('jobs/my-jobs/', MyJobsAPI.as_view(), name='api_my_jobs'),
    path('jobs/<int:job_id>/analytics/', JobAnalyticsAPI.as_view(), name='api_job_analytics'),
    
    # Job board integration
    path('jobs/publish-to-boards/', job_publish_to_boards_api, name='api_publish_to_boards'),
    path('jobs/<int:job_id>/sync-to-boards/', job_sync_to_boards_api, name='api_sync_to_boards'),
    path('jobs/<int:job_id>/fetch-external-applications/', job_fetch_external_applications_api, name='api_fetch_external_apps'),
    
    # Application endpoints
    path('jobs/apply/', job_apply_api, name='api_job_apply'),
    path('jobs/<int:job_id>/applications/', job_applications_api, name='api_job_applications'),
    path('applications/<int:application_id>/', application_detail_api, name='api_application_detail'),
    path('applications/<int:application_id>/status/', application_update_status_api, name='api_update_application_status'),
    path('applications/bulk-update-status/', applications_bulk_update_status_api, name='api_bulk_update_status'),
    
    # Webhooks
    path('webhooks/applications/<str:board>/', external_application_webhook, name='webhook_external_application'),
]

# Combine all patterns
urlpatterns = [
    # MVT routes (no prefix)
    path('', include(mvt_patterns)),
    
    # API routes (with /api/ prefix)
    path('api/', include(api_patterns)),
]
