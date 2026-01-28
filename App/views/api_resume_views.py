
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import os
from django.http import FileResponse

@swagger_auto_schema(method='get', tags=['rpo_admin'], operation_summary='Download resume (RPO Admin)', operation_description='Download a resume file. RPO Admins may download any resume; regular users may download their own.')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rpo_resume_download(request, resume_id):
    """
    Download a resume file by ID. RPO Admins may download any resume; regular users may download their own.
    """
    from App.models import ResumeProcessing
    user = request.user
    user_role = getattr(user, 'profile', None)
    user_role = user_role.role if user_role else 'unknown'
    is_rpo_admin = user_role == 'rpo_admin' or user.groups.filter(name='rpo_admin').exists()
    from App.utils.response import ApiResponse
    try:
        if is_rpo_admin or user.is_superuser:
            resume = ResumeProcessing.objects.get(id=resume_id)
        else:
            resume = ResumeProcessing.objects.get(id=resume_id, user=user)
    except ResumeProcessing.DoesNotExist:
        result = ApiResponse(success=False, message='Access denied or resume not found', status_code=404)
        return api_response(data=result.data, status_code=result.status_code, message=result.message)


# --- RPO Process Single Resume API (REST, Swagger tag: rpo_admin) ---
@swagger_auto_schema(method='post', tags=['rpo_admin'], operation_summary='Process single resume (RPO Admin)', operation_description='Trigger processing of a single resume by ID. RPO Admins may process any resume; regular users may process their own.')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rpo_process_single_resume_api(request, resume_id):
    """
    Trigger processing of a single resume by ID. RPO Admins may process any resume; regular users may process their own.
    """
    user = request.user
    user_role = getattr(user, 'profile', None)
    user_role = user_role.role if user_role else 'unknown'
    is_rpo_admin = user_role == 'rpo_admin' or user.groups.filter(name='rpo_admin').exists()
    from App.models import ResumeProcessing
    from App.utils.response import ApiResponse
    try:
        if is_rpo_admin or user.is_superuser:
            resume = ResumeProcessing.objects.get(id=resume_id)
        else:
            resume = ResumeProcessing.objects.get(id=resume_id, user=user)
    except ResumeProcessing.DoesNotExist:
        result = ApiResponse(success=False, message='Access denied or resume not found', status_code=404)
        return api_response(data=result.data, status_code=result.status_code, message=result.message)

    # Simulate processing logic (replace with actual processing logic as needed)
    # For now, just update status to 'processing' and return success
    resume.status = 'processing'
    resume.save(update_fields=['status'])

    data = {
        'id': resume.id,
        'status': resume.status,
        'message': 'Resume processing started.'
    }
    result = ApiResponse(success=True, message='Resume processing triggered', data=data)
    return api_response(data=result.data, status_code=result.status_code, message=result.message)
    #         user_role = getattr(user, 'profile', None)
    #         user_role = user_role.role if user_role else 'unknown'
    #         is_rpo_admin = user_role == 'rpo_admin' or user.groups.filter(name='rpo_admin').exists()
    #         try:
    #             if is_rpo_admin or user.is_superuser:
    #                 resume = ResumeProcessing.objects.get(id=resume_id)
    #             else:
    #                 resume = ResumeProcessing.objects.get(id=resume_id, user=user)
    #         except ResumeProcessing.DoesNotExist:
    #             result = ApiResponse(success=False, message='Access denied or resume not found', status_code=404)
    #             return api_response(data=result.data, status_code=result.status_code, message=result.message)

    #         # Simulate processing logic (replace with actual processing logic as needed)
    #         # For now, just update status to 'processing' and return success
    #         resume.status = 'processing'
    #         resume.save(update_fields=['status'])

    #         data = {
    #             'id': resume.id,
    #             'status': resume.status,
    #             'message': 'Resume processing started.'
    #         }
    #         result = ApiResponse(success=True, message='Resume processing triggered', data=data)
    #         return api_response(data=result.data, status_code=result.status_code, message=result.message)
    # rel = resume.resume_path or ''
    # rel = rel.lstrip('/\\')
    # absolute_path = os.path.join(settings.BASE_DIR, rel)
    # if not os.path.exists(absolute_path):
    #     result = ApiResponse(success=False, message='Resume file not found on disk', status_code=404)
    #     return api_response(data=result.data, status_code=result.status_code, message=result.message)
    # file_handle = open(absolute_path, 'rb')
    # response = FileResponse(file_handle)
    # response['Content-Disposition'] = f'attachment; filename="{resume.original_filename}"'
    # return response
"""
Resume Upload REST API Views
All logic handled by ResumeUploadService
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from App.services.resume_upload_service import ResumeUploadService


@login_required
@require_http_methods(["POST"])
def api_upload_resumes(request):
    """
    API endpoint to upload multiple resumes
    
    POST /api/resumes/upload/
    Body: multipart/form-data with 'resumes' field containing files
    
    Response:
    {
        "success": true,
        "message": "Uploaded 3 of 3 resumes successfully",
        "data": {
            "successful": [...],
            "failed": [...],
            "total": 3,
            "success_count": 3,
            "failed_count": 0
        }
    }
    """
    files = request.FILES.getlist('resumes')
    
    # Use service to handle upload
    result = ResumeUploadService.upload_resumes(files, request.user)
    return api_response(data=result.data, status_code=200 if result.success else 400, message=result.message)


@login_required
@require_http_methods(["GET"])
def api_get_resumes(request):
    """
    API endpoint to get user's uploaded resumes
    
    GET /api/resumes/list/?limit=20&offset=0
    
    Response:
    {
        "success": true,
        "message": "Retrieved 10 resumes",
        "data": {
            "resumes": [...],
            "total": 50,
            "limit": 20,
            "offset": 0
        }
    }
    """
    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))
    
    # Use service to get resumes
    result = ResumeUploadService.get_user_resumes(request.user, limit=limit, offset=offset)
    return api_response(data=result.data, status_code=200 if result.success else 400, message=result.message)


@login_required
@require_http_methods(["DELETE", "POST"])
def api_delete_resume(request, resume_id):
    """
    API endpoint to delete a resume
    
    DELETE /api/resumes/<id>/delete/
    POST /api/resumes/<id>/delete/ (for form compatibility)
    
    Response:
    {
        "success": true,
        "message": "Resume 'filename.pdf' deleted successfully"
    }
    """
    # Use service to delete resume
    result = ResumeUploadService.delete_resume(resume_id, request.user)
    return api_response(data=result.data, status_code=200 if result.success else 400, message=result.message)


@login_required
@require_http_methods(["GET"])
def api_get_statistics(request):
    """
    API endpoint to get upload statistics
    
    GET /api/resumes/statistics/
    
    Response:
    {
        "success": true,
        "message": "Statistics retrieved successfully",
        "data": {
            "total_uploads": 50,
            "pending": 10,
            "processing": 5,
            "completed": 30,
            "failed": 5,
            "total_size_mb": 125.5,
            "recent_uploads": [...]
        }
    }
    """
    # Use service to get statistics
    result = ResumeUploadService.get_upload_statistics(request.user)
    return api_response(data=result.data, status_code=200 if result.success else 400, message=result.message)


@login_required
@require_http_methods(["POST"])
def api_validate_files(request):
    """
    API endpoint to validate files before upload (client-side validation)
    
    POST /api/resumes/validate/
    Body: multipart/form-data with 'files' field
    
    Response:
    {
        "success": true,
        "data": {
            "valid_files": [...],
            "invalid_files": [...]
        }
    }
    """
    files = request.FILES.getlist('files')
    
    valid_files = []
    invalid_files = []
    
    for file in files:
        validation = ResumeUploadService.validate_file(file)
        
        if validation['valid']:
            valid_files.append({
                'filename': file.name,
                'size': file.size
            })
        else:
            invalid_files.append({
                'filename': file.name,
                'error': validation['error']
            })
    
    from App.utils.response import ApiResponse
    result = ApiResponse.success(
        data={
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'valid_count': len(valid_files),
            'invalid_count': len(invalid_files)
        },
        message=f"Validated {len(files)} files"
    )
    return api_response(data=result.data, status_code=200 if result.success else 400, message=result.message)
def api_response(data=None, status_code=200, message="Success"):
    """
    Unified API response for all endpoints in this module.
    """
    from rest_framework.response import Response
    return Response({
        "data": data,
        "status_code": status_code,
        "message": message
    }, status=status_code)


# --- RPO Resume View API (REST, Swagger tag: rpo_admin) ---
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from App.models import ResumeProcessing
from App.utils.response import ApiResponse

@swagger_auto_schema(method='get', tags=['rpo_admin'], operation_summary='View resume details (RPO Admin)', operation_description='Retrieve details of a resume by ID. RPO Admins may view any resume; regular users may view their own.')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rpo_resume_view_api(request, resume_id):
    """
    Retrieve details of a resume by ID. RPO Admins may view any resume; regular users may view their own.
    """
    user = request.user
    user_role = getattr(user, 'profile', None)
    user_role = user_role.role if user_role else 'unknown'
    is_rpo_admin = user_role == 'rpo_admin' or user.groups.filter(name='rpo_admin').exists()
    try:
        if is_rpo_admin or user.is_superuser:
            resume = ResumeProcessing.objects.get(id=resume_id)
        else:
            resume = ResumeProcessing.objects.get(id=resume_id, user=user)
    except ResumeProcessing.DoesNotExist:
        result = ApiResponse(success=False, message='Access denied or resume not found', status_code=404)
        return api_response(data=result.data, status_code=result.status_code, message=result.message)

    # Prepare response data (customize as needed)
    data = {
        'id': resume.id,
        'user_id': resume.user_id,
        'original_filename': resume.original_filename,
        'file_size': resume.file_size,
        'file_extension': resume.file_extension,
        'status': resume.status,
        'created_at': resume.created_at,
        'updated_at': resume.updated_at,
        'candidate_name': resume.candidate_name,
        'extracted_email': resume.extracted_email,
        'extracted_phone': resume.extracted_phone,
        'years_of_experience': resume.years_of_experience,
        'sentiment_score': resume.sentiment_score,
        'word_count': resume.word_count,
        'error_message': resume.error_message,
        'resume_json': resume.resume_json,
    }
    result = ApiResponse(success=True, message='Resume details retrieved', data=data)
    return api_response(data=result.data, status_code=result.status_code, message=result.message)
# --- Resume Matching: Match Details API (REST, Swagger tag: rpo_admin) ---
@swagger_auto_schema(method='get', tags=['rpo_admin'], operation_summary='View match details (RPO Admin)', operation_description='Retrieve details of a resume-job match by match_id. RPO Admins may view any match; regular users may view their own.')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_match_details_api(request, match_id):
    """
    Retrieve details of a resume-job match by match_id. RPO Admins may view any match; regular users may view their own.
    """
    user = request.user
    user_role = getattr(user, 'profile', None)
    user_role = user_role.role if user_role else 'unknown'
    is_rpo_admin = user_role == 'rpo_admin' or user.groups.filter(name='rpo_admin').exists()
    from App.utils.response import ApiResponse
    # Import the model for match details (assume ResumeJobMatch or similar)
    try:
        from App.models import ResumeJobMatch
    except ImportError:
        result = ApiResponse(success=False, message='ResumeJobMatch model not found', status_code=500)
        return api_response(data=result.data, status_code=result.status_code, message=result.message)
    try:
        if is_rpo_admin or user.is_superuser:
            match = ResumeJobMatch.objects.get(id=match_id)
        else:
            match = ResumeJobMatch.objects.get(id=match_id, user=user)
    except ResumeJobMatch.DoesNotExist:
        result = ApiResponse(success=False, message='Access denied or match not found', status_code=404)
        return api_response(data=result.data, status_code=result.status_code, message=result.message)

    # Prepare response data to match the MVT context
    # Serialize match object (basic fields)
    match_data = {
        'id': match.id,
        'resume_id': getattr(match, 'resume_id', None),
        'job_id': getattr(match, 'job_id', None),
        'score': getattr(match, 'score', None),
        'status': getattr(match, 'status', None),
        'created_at': getattr(match, 'created_at', None),
        'updated_at': getattr(match, 'updated_at', None),
        # Add more fields as needed
    }
    # Add detailed_analysis (should be a dict)
    context = {
        'match': match_data,
        'detailed_analysis': getattr(match, 'detailed_analysis', {}) or {}
    }
    result = ApiResponse(success=True, message='Match details retrieved', data=context)
    return api_response(data=result.data, status_code=result.status_code, message=result.message)
