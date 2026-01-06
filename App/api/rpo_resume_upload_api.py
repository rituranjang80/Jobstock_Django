
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, parsers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from App.services.resume_upload_service import ResumeUploadService
from App.models import Job, DropdownMaster

class RPOResumeUploadAPI(APIView):
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
            return Response({'success': False, 'message': 'Please select at least one resume file to upload'}, status=status.HTTP_400_BAD_REQUEST)
        result = ResumeUploadService.upload_resumes(files, request.user, job=job_obj, resumesource=resumesource_obj)
        if result.success:
            response = {'success': True, 'message': result.message, 'data': result.data}
            if result.data['failed_count'] > 0:
                response['warnings'] = result.data['failed']
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {'success': False, 'message': result.message}
            if hasattr(result, 'error_details') and result.error_details:
                response['errors'] = result.error_details.get('failed', [])
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
