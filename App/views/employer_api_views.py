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
        # Map camelCase keys to snake_case for serializer compatibility
        def camel_to_snake(name):
            import re
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

        # Only map known fields to avoid accidental data loss
        key_map = {
            'jobCategory': 'job_category',
            'jobType': 'job_type',
            'jobLevel': 'job_level',
            'experience': 'experience_required',
            'qualification': 'qualification_required',
            'gender': 'gender_preference',
            'totalOpenings': 'total_openings',
            'jobFeeType': 'job_fee_type',
            'country': 'country',
            'city': 'state_city',
            'minSalary': 'min_salary',
            'maxSalary': 'max_salary',
            'permanentAddress': 'permanent_address',
            'temporaryAddress': 'temporary_address',
            'zipCode': 'zip_code',
            'videoUrl': 'video_url',
            'startDate': 'start_date',
            'deadline': 'deadline',
            'skills': 'skills',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'job_id': 'job_id',
            'title': 'title',
            'jobSummary': 'job_summary',
            'responsibilities': 'responsibilities',
            'qualifications': 'qualifications',
        }
        mapped_data = {}
        for k, v in request.data.items():
            mapped_data[key_map.get(k, camel_to_snake(k))] = v

        job_id = mapped_data.get('job_id')
        is_update = job_id is not None
        serializer = JobCreateUpdateSerializer(data=mapped_data, partial=is_update)
        if not serializer.is_valid():
            from rest_framework.exceptions import ValidationError
            raise ValidationError(serializer.errors)
        try:
            if is_update:
                job = JobService.update_job(job_id, serializer.validated_data, request.user)
                resp = ApiResponse.success(data={"id": job.id, "title": job.title}, message="Job updated")
            else:
                job = JobService.create_job(serializer.validated_data, request.user)
                resp = ApiResponse.created(data={"id": job.id, "title": job.title}, message="Job created")
            return Response(resp.to_dict(), status=resp.status_code)
        except Exception as e:
            raise e
            # action = "updating" if is_update else "creating"
            # resp = ApiResponse.error(message=f"Error {action} job", error=str(e))
            # return Response(resp.to_dict(), status=resp.status_code)