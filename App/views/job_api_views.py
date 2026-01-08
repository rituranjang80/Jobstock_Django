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


# ==================== JOB ENDPOINTS ====================

@swagger_auto_schema(method='get', tags=['Job'], operation_summary='List and search jobs', operation_description='List and search jobs with filters.')
@api_view(['GET'])
@permission_classes([AllowAny])
def job_list_api(request):
    """
    GET /api/jobs/
    List and search jobs with filters
    
    Query Parameters:
        - q: Search query
        - job_category: Category ID
        - job_type: Job type value
        - job_level: Job level value
        - min_salary: Minimum salary
        - max_salary: Maximum salary
        - location: Location string
        - posted_within_days: Number of days
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
    """
    serializer = JobSearchSerializer(data=request.query_params)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    params = serializer.validated_data
    
    # Build filters
    filters = {}
    for key in ['job_category', 'job_type', 'job_level', 'min_salary', 
                'max_salary', 'location', 'posted_within_days']:
        if key in params and params[key]:
            filters[key] = params[key]
    
    # Call service
    result = job_service.search_jobs(
        search_query=params.get('q'),
        filters=filters,
        page=params.get('page', 1),
        per_page=params.get('per_page', 20),
        order_by=params.get('order_by', '-created_at')
    )
    
    return Response(result)


@swagger_auto_schema(method='get', tags=['Job'], operation_summary='Get job details', operation_description='Get job details.')
@api_view(['GET'])
@permission_classes([AllowAny])
def job_detail_api(request, job_id):
    """
    GET /api/jobs/{job_id}/
    Get job details
    """
    result = job_service.get_job_details(job_id)
    
    if result['success']:
        return Response(result)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method='post', tags=['Job'], operation_summary='Create job', operation_description='Create a new job posting.')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def job_create_api(request):
    """
    POST /api/jobs/
    Create a new job posting
    
    Body:
        - All job fields
        - publish_to_boards: List of boards (optional)
    """
    serializer = JobCreateUpdateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Extract board selection
    boards = serializer.validated_data.pop('publish_to_boards', None)
    
    # Create job via service
    result = job_service.create_job_post(
        data=serializer.validated_data,
        user=request.user,
        publish_to_boards=boards
    )
    
    if result['success']:
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(methods=['put', 'patch'], tags=['Job'], operation_summary='Update job', operation_description='Update a job posting.')
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def job_update_api(request, job_id):
    """
    PUT/PATCH /api/jobs/{job_id}/
    Update a job posting
    """
    serializer = JobCreateUpdateSerializer(data=request.data, partial=(request.method == 'PATCH'))
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Update via service
    result = job_service.update_job_post(
        job_id=job_id,
        data=serializer.validated_data,
        user=request.user,
        sync_to_boards=True
    )
    
    if result['success']:
        return Response(result)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='delete', tags=['Job'], operation_summary='Delete job', operation_description='Delete/deactivate a job posting.')
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def job_delete_api(request, job_id):
    """
    DELETE /api/jobs/{job_id}/
    Delete/deactivate a job posting
    """
    soft_delete = request.query_params.get('soft', 'true').lower() == 'true'
    
    result = job_service.deactivate_job(
        job_id=job_id,
        user=request.user,
        remove_from_boards=True
    )
    
    if result['success']:
        return Response(result)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', tags=['Job'], operation_summary='Get my jobs', operation_description='Get jobs posted by current user.')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_jobs_api(request):
    """
    GET /api/jobs/my-jobs/
    Get jobs posted by current user
    """
    page = int(request.query_params.get('page', 1))
    per_page = int(request.query_params.get('per_page', 20))
    
    filters = {}
    if request.query_params.get('is_active'):
        filters['is_active'] = request.query_params.get('is_active') == 'true'
    
    result = job_service.get_my_posted_jobs(
        user=request.user,
        filters=filters,
        page=page,
        per_page=per_page
    )
    
    return Response(result)


@swagger_auto_schema(method='get', tags=['Job'], operation_summary='Get job analytics', operation_description='Get job analytics.')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_analytics_api(request, job_id):
    """
    GET /api/jobs/{job_id}/analytics/
    Get job analytics
    """
    result = job_service.get_job_analytics(job_id, request.user)
    
    if result['success']:
        return Response(result)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)


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
