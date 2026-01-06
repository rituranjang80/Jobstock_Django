"""
Resume Management API - Process Resumes
REST API for processing pending resumes with authentication and Swagger docs
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from App.services.resume_upload_service import ResumeUploadService

class RPOProcessResumesAPI(APIView):
    """
    API endpoint for processing pending resumes (POST)
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Process pending resumes (extract data, analyze, store in database)",
        tags=["resume_management"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'resume_ids': openapi.Schema(type=openapi.TYPE_STRING, description='Comma-separated resume IDs to process (optional, process all if blank)'),
                'job_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Job ID (optional)'),
            },
            required=[],
        ),
        responses={
            200: openapi.Response(
                description="Processing result",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "5 resumes processed, 1 failed.",
                        "data": {"processed": 5, "failed": 1, "failed_ids": [123]}
                    }
                }
            ),
            400: "Bad request"
        }
    )
    def post(self, request):
        user = request.user
        # Check RPO admin
        user_role = getattr(user.profile, 'role', 'unknown') if hasattr(user, 'profile') else 'unknown'
        is_rpo_admin = user_role == 'rpo_admin' or user.groups.filter(name='rpo_admin').exists()
        if not is_rpo_admin and not user.is_superuser:
            return Response({"success": False, "message": "Access denied. RPO Admin role required."}, status=status.HTTP_403_FORBIDDEN)


        resume_ids_val = request.data.get('resume_ids', '')
        resume_ids = None
        if resume_ids_val:
            # Accept int, list, or comma-separated string
            if isinstance(resume_ids_val, int):
                resume_ids = [resume_ids_val]
            elif isinstance(resume_ids_val, list):
                try:
                    resume_ids = [int(i) for i in resume_ids_val]
                except Exception:
                    return Response({"success": False, "message": "Invalid resume IDs format (list)"}, status=status.HTTP_400_BAD_REQUEST)
            elif isinstance(resume_ids_val, str):
                try:
                    resume_ids = [int(id.strip()) for id in resume_ids_val.split(',') if id.strip()]
                except Exception:
                    return Response({"success": False, "message": "Invalid resume IDs format (string)"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": False, "message": "Invalid resume IDs type"}, status=status.HTTP_400_BAD_REQUEST)

        job_id_val = request.data.get('job_id', None)
        job_id = None
        if job_id_val is not None and job_id_val != '':
            if isinstance(job_id_val, int):
                job_id = job_id_val
            elif isinstance(job_id_val, str):
                try:
                    job_id = int(job_id_val.strip())
                except Exception:
                    return Response({"success": False, "message": "Invalid Job ID format (string)"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success": False, "message": "Invalid Job ID type"}, status=status.HTTP_400_BAD_REQUEST)

        result = ResumeUploadService.process_pending_resumes(user, resume_ids, job_id)
        resp = {"success": result.success, "message": result.message}
        # Clean up data for serialization
        def serialize_resume_record(rec):
            if rec is None:
                return None
            # Return only selected fields
            return {
                "id": rec.id,
                "status": getattr(rec, 'status', None),
                "original_filename": getattr(rec, 'original_filename', None),
                "user_id": getattr(rec, 'user_id', None),
            }

        def clean_result_data(data):
            if not data:
                return data
            # If 'results' is a list of dicts, clean each
            if isinstance(data, dict) and 'results' in data and isinstance(data['results'], list):
                for item in data['results']:
                    if isinstance(item, dict) and 'resume_record' in item:
                        item['resume_record'] = serialize_resume_record(item['resume_record'])
            # If 'resume_record' is present at top level
            if isinstance(data, dict) and 'resume_record' in data:
                data['resume_record'] = serialize_resume_record(data['resume_record'])
            return data

        if hasattr(result, 'data') and result.data:
            resp["data"] = clean_result_data(result.data)
        if hasattr(result, 'error_details') and result.error_details:
            resp["error_details"] = result.error_details
        return Response(resp, status=status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST)
