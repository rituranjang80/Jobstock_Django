# Employer Submit Job REST API (DRF)
# Implements create/update job for employers using service layer and standardized response format.
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from App.serializers.job_serializers import JobCreateUpdateSerializer
from App.services.job_service import JobService
from App.utils.response import ApiResponse

class EmployerSubmitJobAPI(APIView):
    """
    API endpoint for employer to upsert (create or update) a job posting.
    If 'job_id' is provided in the payload, updates the job; otherwise, creates a new job.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Job'],
        request_body=JobCreateUpdateSerializer,
        operation_summary='Upsert job',
        operation_description='Create or update a job posting as employer. If job_id is provided, updates; else creates.'
    )
    def post(self, request):
        job_id = request.data.get('job_id')
        is_update = job_id is not None
        serializer = JobCreateUpdateSerializer(data=request.data, partial=is_update)
        if not serializer.is_valid():
            raise ApiResponse.validation_error(errors=serializer.errors)
            resp = ApiResponse.error(message="Invalid data", error_details=serializer.errors)
            return Response(resp.to_dict(), status=resp.status_code)
        try:
            # All dropdowns are string values; pass as-is to service layer
            if is_update:
                job = JobService.update_job(job_id, serializer.validated_data, request.user)
                resp = ApiResponse.success(data={"id": job.id, "title": job.title}, message="Job updated")
            else:
                job = JobService.create_job(serializer.validated_data, request.user)
                resp = ApiResponse.created(data={"id": job.id, "title": job.title}, message="Job created")
            return Response(resp.to_dict(), status=resp.status_code)
        except Exception as e:
            action = "updating" if is_update else "creating"
            resp = ApiResponse.error(message=f"Error {action} job", error=str(e))
            return Response(resp.to_dict(), status=resp.status_code)