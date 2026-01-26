"""
Resume Upload REST API Views
All logic handled by ResumeUploadService
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from App.services.resume_upload_service import ResumeUploadService
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
import os
from django.http import FileResponse


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
    
    return JsonResponse(result.to_dict(), status=result.status_code)


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
    
    return JsonResponse(result.to_dict(), status=result.status_code)


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
    
    return JsonResponse(result.to_dict(), status=result.status_code)


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
    
    return JsonResponse(result.to_dict(), status=result.status_code)


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
    
    return JsonResponse(result.to_dict())


@swagger_auto_schema(method='get', tags=['rpo_admin'], operation_summary='Download resume (RPO Admin)', operation_description='Download a resume file. RPO Admins may download any resume; regular users may download their own.')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_rpo_resume_download(request, resume_id):
    """
    GET /api/resumes/download/<id>/
    Download a resume file. Returns streaming file response.
    """
    from App.models import ResumeProcessing

    # Determine rpo admin role
    user_role = getattr(request.user, 'profile', None)
    user_role = user_role.role if user_role else 'unknown'
    is_rpo_admin = user_role == 'rpo_admin' or request.user.groups.filter(name='rpo_admin').exists()

    if not is_rpo_admin and not request.user.is_superuser:
        # regular users may only download their own resumes
        try:
            resume = ResumeProcessing.objects.get(id=resume_id, user=request.user)
        except ResumeProcessing.DoesNotExist:
            return Response({'success': False, 'message': 'Access denied or resume not found'}, status=403)
    else:
        try:
            resume = ResumeProcessing.objects.get(id=resume_id)
        except ResumeProcessing.DoesNotExist:
            return Response({'success': False, 'message': 'Resume not found'}, status=404)

    # Build absolute path
    rel = resume.resume_path or ''
    rel = rel.lstrip('/\\')
    absolute_path = os.path.join(settings.BASE_DIR, rel)
    if not os.path.exists(absolute_path):
        return Response({'success': False, 'message': 'Resume file not found on disk'}, status=404)

    # Stream file back
    file_handle = open(absolute_path, 'rb')
    response = FileResponse(file_handle)
    response['Content-Disposition'] = f'attachment; filename="{resume.original_filename}"'
    return response
