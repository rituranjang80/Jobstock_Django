
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, parsers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from App.services.resume_upload_service import ResumeUploadService
from App.models import Job, DropdownMaster
from App.api.response_mixin import APIResponseMixin

class RPOResumeUploadAPI(APIResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @swagger_auto_schema(
        operation_description="Upload one or more resumes for a job and resume source.",
        tags=["rpo_admin"],
        manual_parameters=[
            openapi.Parameter(
                name='resumes',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description='Resume files',
                required=True,
                multiple=True
            ),
            openapi.Parameter(
                name='jobid',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description='Job ID',
                required=False
            ),
            openapi.Parameter(
                name='resume_sources',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description='Resume Source ID',
                required=False
            ),
        ],
        responses={200: openapi.Response('Upload result', openapi.Schema(type=openapi.TYPE_OBJECT))}
    )
    @method_decorator(login_required)
    def post(self, request):
        files = request.FILES.getlist('resumes')
        job_id = request.POST.get('jobid')
        resumesource_id = request.POST.get('resume_sources')
        job_obj = None
        resumesource_obj = None
        if job_id:
            try:
                job_obj = Job.objects.get(pk=job_id)
            except Job.DoesNotExist:
                job_obj = None
        if resumesource_id:
            try:
                resumesource_obj = DropdownMaster.objects.get(pk=resumesource_id)
            except DropdownMaster.DoesNotExist:
                resumesource_obj = None
        if not files:
            return self.api_response(
                status_code=400,
                message='Please select at least one resume file to upload',
                data=None
            )
        result = ResumeUploadService.upload_resumes(files, request.user, job=job_obj, resumesource=resumesource_obj)
        if result.success:
            data = result.data
            warnings = data['failed'] if data and data.get('failed_count', 0) > 0 else None
            return self.api_response(
                status_code=200,
                message=result.message,
                data=data,
                error_details=None,
                more_error_details=warnings
            )
        else:
            errors = result.error_details.get('failed', []) if hasattr(result, 'error_details') and result.error_details else None
            return self.api_response(
                status_code=400,
                message=result.message,
                data=None,
                error_details=errors,
                more_error_details=None
            )
