"""
Resume Management API
REST API for RPO resume upload with authentication and Swagger docs
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from App.services.resume_upload_service import ResumeUploadService
from App.models import Job, DropdownMaster

class RPOResumeUploadAPI(APIView):
    """
    API endpoint for RPO Admin Resume Upload (GET: form info, POST: upload resumes)
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Get upload form info (job, resume sources, allowed extensions, etc)",
        tags=["resume_management"],
        responses={
            200: openapi.Response(
                description="Form info",
                examples={
                    "application/json": {
                        "job_id": 1,
                        "job_title": "Software Engineer",
                        "job_company": "Acme Corp",
                        "resume_sources": [
                            {"id": 1, "text": "Naukri"},
                            {"id": 2, "text": "LinkedIn"}
                        ],
                        "allowed_extensions": ".pdf, .docx",
                        "max_file_size_mb": 5
                    }
                }
            )
        }
    )
    def get(self, request):
        """
        Get upload form info (job, resume sources, allowed extensions, etc)
        """
        job_id = request.GET.get('jobid')
        job_title = None
        job_company = None
        if job_id:
            try:
                job_obj = Job.objects.get(pk=job_id)
                job_title = job_obj.title
                job_company = getattr(job_obj, 'company_name', None)
            except Job.DoesNotExist:
                job_title = None
                job_company = None
        # Resume sources
        from App.models import DropdownGroup
        try:
            resume_source_group = DropdownGroup.objects.get(text='ResumeSource', is_active=True)
            resume_sources = DropdownMaster.objects.filter(group=resume_source_group, is_active=True).order_by('sort_order', 'text')
            resume_sources_list = [{"id": r.id, "text": r.text} for r in resume_sources]
        except DropdownGroup.DoesNotExist:
            resume_sources_list = []
        # Allowed extensions and max file size
        allowed_extensions = ', '.join(ResumeUploadService.ALLOWED_EXTENSIONS)
        max_file_size_mb = ResumeUploadService.MAX_FILE_SIZE / (1024 * 1024)
        return Response({
            "job_id": job_id,
            "job_title": job_title,
            "job_company": job_company,
            "resume_sources": resume_sources_list,
            "allowed_extensions": allowed_extensions,
            "max_file_size_mb": max_file_size_mb
        })

    @swagger_auto_schema(
        operation_description="Upload one or more resumes for a job (RPO Admin only)",
        tags=["resume_management"],
        manual_parameters=[
            openapi.Parameter('resumes', openapi.IN_FORM, description="Resume files", type=openapi.TYPE_FILE, required=True, multiple=True),
            openapi.Parameter('jobid', openapi.IN_FORM, description="Job ID", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('resume_sources', openapi.IN_FORM, description="Resume Source ID", type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={
            200: openapi.Response(
                description="Upload result",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "3 resumes uploaded, 1 failed.",
                        "data": {"uploaded_count": 3, "failed_count": 1, "failed": [{"filename": "bad.pdf", "error": "Invalid file"}]}
                    }
                }
            ),
            400: "Bad request"
        }
    )
    def post(self, request):
        """
        Upload one or more resumes for a job (RPO Admin only)
        """
        user = request.user
        # Check RPO admin
        user_role = getattr(user.profile, 'role', 'unknown') if hasattr(user, 'profile') else 'unknown'
        is_rpo_admin = user_role == 'rpo_admin' or user.groups.filter(name='rpo_admin').exists()
        if not is_rpo_admin and not user.is_superuser:
            return Response({"success": False, "message": "Access denied. RPO Admin role required."}, status=status.HTTP_403_FORBIDDEN)

        files = request.FILES.getlist('resumes')
        job_id = request.data.get('jobid')
        resumesource_id = request.data.get('resume_sources')
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
            return Response({"success": False, "message": "Please select at least one resume file to upload"}, status=status.HTTP_400_BAD_REQUEST)
        result = ResumeUploadService.upload_resumes(files, user, job=job_obj, resumesource=resumesource_obj)
        resp = {"success": result.success, "message": result.message}
        if hasattr(result, 'data') and result.data:
            resp["data"] = result.data
        if hasattr(result, 'error_details') and result.error_details:
            resp["error_details"] = result.error_details
        return Response(resp, status=status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST)