from django.urls import path
from App.views.employer_api_views import EmployerSubmitJobAPI

urlpatterns = [
    path('employer/submit-job/', EmployerSubmitJobAPI.as_view(), name='employer_submit_job_api'),
    path('employer/submit-job/<int:job_id>/', EmployerSubmitJobAPI.as_view(), name='employer_update_job_api'),
]
