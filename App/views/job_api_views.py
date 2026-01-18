"""
REST API Views (Django REST Framework)
All business logic is in services - views are thin API controllers

Author: JobStock Development Team
Date: December 22, 2025
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from drf_yasg.utils import swagger_auto_schema

from App.services.enhanced_job_service import job_service
from App.services.job_application_service import application_service
from App.services.job_board_integration_service import job_board_service
from App.serializers.job_serializers import (
    JobListSerializer, JobDetailSerializer, JobCreateUpdateSerializer,
    JobApplicationSerializer, JobApplicationCreateSerializer,
    JobSearchSerializer, JobBoardPublishSerializer,
    ApplicationStatusUpdateSerializer, BulkApplicationStatusSerializer
)
from App.api.response_mixin import APIResponseMixin
from App.services.search_config_loader import get_search_fields
from django.db.models import Q
import json


# ==================== JOB ENDPOINTS ====================

class JobAPI(APIResponseMixin, APIView):
    """
    List and search jobs
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['Job'], operation_summary='List and search jobs', operation_description='List and search jobs with filters.')
    def get(self, request):
        serializer = JobSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return self.api_response(
                status_code=400,
                message="Invalid parameters",
                error_details=serializer.errors,
                data=None
            )
        params = serializer.validated_data
        filters = {}
        for key in ['job_category', 'job_type', 'job_level', 'min_salary', 'max_salary', 'location', 'posted_within_days']:
            if key in params and params[key]:
                filters[key] = params[key]
        result = job_service.search_jobs(
            search_query=params.get('q'),
            filters=filters,
            page=params.get('page', 1),
            per_page=params.get('per_page', 20),
            order_by=params.get('order_by', '-created_at')
        )
        return self.api_response(
            status_code=200,
            message="Jobs fetched successfully",
            data=result
        )


class JobDetailAPI(APIResponseMixin, APIView):
    """
    Get job details
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['Job'], operation_summary='Get job details', operation_description='Get job details.')
    def get(self, request, job_id):
        result = job_service.get_job_details(job_id)
        if result['success']:
            return self.api_response(
                status_code=200,
                message="Job details fetched successfully",
                data=result
            )
        else:
            return self.api_response(
                status_code=404,
                message="Job not found",
                data=None
            )


class JobCreateAPI(APIResponseMixin, APIView):
    """
    Create job
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Job'], operation_summary='Create job', operation_description='Create a new job posting.')
    def post(self, request):
        serializer = JobCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return self.api_response(
                status_code=400,
                message="Invalid parameters",
                error_details=serializer.errors,
                data=None
            )
        boards = serializer.validated_data.pop('publish_to_boards', None)
        result = job_service.create_job_post(
            data=serializer.validated_data,
            user=request.user,
            publish_to_boards=boards
        )
        if result['success']:
            return self.api_response(
                status_code=201,
                message="Job created successfully",
                data=result
            )
        else:
            return self.api_response(
                status_code=400,
                message="Error creating job",
                data=result
            )


class JobUpdateAPI(APIResponseMixin, APIView):
    """
    Update job
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Job'], operation_summary='Update job', operation_description='Update a job posting.')
    def patch(self, request, job_id):
        serializer = JobCreateUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return self.api_response(
                status_code=400,
                message="Invalid parameters",
                error_details=serializer.errors,
                data=None
            )
        result = job_service.update_job_post(
            job_id=job_id,
            data=serializer.validated_data,
            user=request.user,
            sync_to_boards=True
        )
        if result['success']:
            return self.api_response(status_code=200, message="Job updated successfully", data=result)
        else:
            return self.api_response(status_code=400, message="Job update failed", error_details=result.get('errors'), data=None)

    @swagger_auto_schema(tags=['Job'], operation_summary='Update job', operation_description='Update a job posting.')
    def put(self, request, job_id):
        serializer = JobCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return self.api_response(
                status_code=400,
                message="Invalid parameters",
                error_details=serializer.errors,
                data=None
            )
        result = job_service.update_job_post(
            job_id=job_id,
            data=serializer.validated_data,
            user=request.user,
            sync_to_boards=True
        )
        if result['success']:
            return self.api_response(status_code=200, message="Job updated successfully", data=result)
        else:
            return self.api_response(status_code=400, message="Job update failed", error_details=result.get('errors'), data=None)


class JobDeleteAPI(APIResponseMixin, APIView):
    """
    Delete job
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Job'], operation_summary='Delete job', operation_description='Delete/deactivate a job posting.')
    def delete(self, request, job_id):
        soft_delete = request.query_params.get('soft', 'true').lower() == 'true'
        result = job_service.deactivate_job(
            job_id=job_id,
            user=request.user,
            remove_from_boards=True
        )
        if result['success']:
            return self.api_response(
                status_code=200,
                message="Job deleted successfully",
                data=result
            )
        else:
            return self.api_response(
                status_code=400,
                message="Error deleting job",
                data=result
            )


class MyJobsAPI(APIResponseMixin, APIView):
    """
    Get jobs posted by current user, with search and sort support
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Job'], operation_summary='Get my jobs', operation_description='Get jobs posted by current user, with search and sort.')
    def get(self, request):
        from App.models_extended import JobApplication
        from App.services.base_generic_service import ServiceResponse
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('page_size', 20))
        filters = {}
        if request.query_params.get('is_active'):
            filters['is_active'] = request.query_params.get('is_active') == 'true'
        # --- Search support ---
        search_query = request.query_params.get('search')
        search_fields = get_search_fields('my-jobs')
        search_q = Q()
        if search_query and search_fields:
            for field in search_fields:
                search_q |= Q(**{f"{field}__icontains": search_query})
        # --- Sort support ---
        sort_by = request.query_params.get('sortBy', 'created_at')
        sort_order = request.query_params.get('sortOrder', 'desc')
        order_by = f"{'-' if sort_order == 'desc' else ''}{sort_by}"
        # Queryset
        queryset = job_service.model.objects.select_related(*job_service.SELECT_RELATED).filter(posted_by=request.user)
        if filters:
            queryset = queryset.filter(**filters)
        if search_q:
            queryset = queryset.filter(search_q)
        total_jobs = queryset.count()
        active_jobs = queryset.filter(is_active=True).count()
        queryset = queryset.order_by(order_by)
        start = (page - 1) * per_page
        end = start + per_page
        jobs = queryset[start:end]
        job_list = []
        for job in jobs:
            job_data = job_service._serialize_job_detail(job)
            job_data['application_count'] = JobApplication.objects.filter(job_id=job.id).count()
            job_list.append(job_data)
        return self.api_response(
            status_code=200,
            message=f"Retrieved {total_jobs} jobs",
            data=ServiceResponse.paginated(
                data=job_list,
                page=page,
                per_page=per_page,
                total=total_jobs,
                summary={
                    'total_jobs': total_jobs,
                    'active_jobs': active_jobs,
                    'inactive_jobs': total_jobs - active_jobs
                },
                message=f"Retrieved {total_jobs} jobs"
            )
        )


class JobAnalyticsAPI(APIResponseMixin, APIView):
    """
    Get job analytics
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Job'], operation_summary='Get job analytics', operation_description='Get job analytics.')
    def get(self, request, job_id):
        result = job_service.get_job_analytics(job_id, request.user)
        if result['success']:
            return self.api_response(
                status_code=200,
                message="Job analytics fetched successfully",
                data=result
            )
        else:
            return self.api_response(
                status_code=404,
                message="Job not found",
                data=None
            )


# ==================== JOB BOARD INTEGRATION ENDPOINTS ====================

@swagger_auto_schema(method='post', tags=['Job'], operation_summary='Publish job to boards', operation_description='Publish a job to external job boards.')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def job_publish_to_boards_api(request):
    """
    POST /api/jobs/publish-to-boards/
    Publish a job to external job boards
    
    Body:
        - job_id: Job ID
        - boards: List of board names
    """
    serializer = JobBoardPublishSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    job_id = serializer.validated_data['job_id']
    boards = serializer.validated_data['boards']
    
    result = job_board_service.publish_to_multiple_boards(job_id, boards)
    
    return Response(result)


@swagger_auto_schema(method='post', tags=['Job'], operation_summary='Sync job to boards', operation_description='Sync job updates to all external boards.')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def job_sync_to_boards_api(request, job_id):
    """
    POST /api/jobs/{job_id}/sync-to-boards/
    Sync job updates to all external boards
    """
    result = job_board_service.sync_job_updates(job_id)
    return Response(result)


@swagger_auto_schema(method='get', tags=['Job'], operation_summary='Fetch external applications', operation_description='Fetch applications from external job boards.')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_fetch_external_applications_api(request, job_id):
    """
    GET /api/jobs/{job_id}/fetch-external-applications/
    Fetch applications from external job boards
    """
    board = request.query_params.get('board')  # Optional specific board
    
    result = job_board_service.fetch_applications(job_id, board)
    return Response(result)


# ==================== APPLICATION ENDPOINTS ====================

@swagger_auto_schema(method='post', tags=['Job'], operation_summary='Apply for job', operation_description='Submit a job application.')
@api_view(['POST'])
@permission_classes([AllowAny])
def job_apply_api(request):
    """
    POST /api/jobs/apply/
    Submit a job application
    
    Body:
        - job_id: Job ID
        - applicant_name: Full name
        - applicant_email: Email
        - applicant_phone: Phone (optional)
        - cover_letter: Cover letter (optional)
        - resume: File upload
    """
    serializer = JobApplicationCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Prepare applicant data
    applicant_data = {
        'name': data['applicant_name'],
        'email': data['applicant_email'],
        'phone': data.get('applicant_phone'),
        'cover_letter': data.get('cover_letter'),
    }
    
    # Add user if authenticated
    if request.user.is_authenticated:
        applicant_data['user'] = request.user
    
    # Submit application
    result = application_service.submit_application(
        job_id=data['job_id'],
        applicant_data=applicant_data,
        resume_file=data['resume'],
        source='direct'
    )
    
    if result['success']:
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', tags=['Job'], operation_summary='Get job applications', operation_description='Get applications for a job.')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_applications_api(request, job_id):
    """
    GET /api/jobs/{job_id}/applications/
    Get applications for a job
    """
    page = int(request.query_params.get('page', 1))
    per_page = int(request.query_params.get('per_page', 20))
    
    filters = {}
    if request.query_params.get('status'):
        filters['status'] = request.query_params.get('status')
    if request.query_params.get('source'):
        filters['source'] = request.query_params.get('source')
    
    result = application_service.get_job_applications(
        job_id=job_id,
        user=request.user,
        filters=filters,
        page=page,
        per_page=per_page
    )
    
    if result['success']:
        return Response(result)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method='get', tags=['Job'], operation_summary='Get application details', operation_description='Get application details.')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def application_detail_api(request, application_id):
    """
    GET /api/applications/{application_id}/
    Get application details
    """
    result = application_service.get_application_details(
        application_id=application_id,
        user=request.user
    )
    
    if result['success']:
        return Response(result)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method='patch', tags=['Job'], operation_summary='Update application status', operation_description='Update application status.')
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def application_update_status_api(request, application_id):
    """
    PATCH /api/applications/{application_id}/status/
    Update application status
    
    Body:
        - status: New status
        - notes: Optional notes
    """
    serializer = ApplicationStatusUpdateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    result = application_service.update_application_status(
        application_id=application_id,
        status=serializer.validated_data['status'],
        user=request.user,
        notes=serializer.validated_data.get('notes')
    )
    
    if result['success']:
        return Response(result)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post', tags=['Job'], operation_summary='Bulk update application status', operation_description='Bulk update application statuses.')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def applications_bulk_update_status_api(request):
    """
    POST /api/applications/bulk-update-status/
    Bulk update application statuses
    
    Body:
        - application_ids: List of IDs
        - status: New status
    """
    serializer = BulkApplicationStatusSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    result = application_service.bulk_update_status(
        application_ids=serializer.validated_data['application_ids'],
        status=serializer.validated_data['status'],
        user=request.user
    )
    
    return Response(result)


# ==================== WEBHOOK ENDPOINT ====================

@swagger_auto_schema(method='post', tags=['Job'], operation_summary='External application webhook', operation_description='Receive application from external job board.')
@api_view(['POST'])
@permission_classes([AllowAny])  # Secure this with API key validation in production
def external_application_webhook(request, board):
    """
    POST /api/webhooks/applications/{board}/
    Receive application from external job board
    
    This endpoint receives applications from Indeed, ZipRecruiter, LinkedIn, JobElephant
    """
    # TODO: Validate webhook signature/API key
    
    job_external_id = request.data.get('job_id')
    application_data = request.data.get('application', request.data)
    
    result = application_service.receive_external_application(
        job_external_id=job_external_id,
        board=board,
        application_data=application_data
    )
    
    return Response(result)
