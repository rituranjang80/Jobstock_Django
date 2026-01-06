from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from App.serializers.resume_processing_list_serializer import ResumeProcessingListSerializer
from App.services.resume_processing_list_service import ResumeProcessingListService

class RPOResumeListAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List uploaded resumes with filters, sorting, and pagination",
        tags=["rpo_admin"],
        manual_parameters=[
            openapi.Parameter('limit', openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER),
            openapi.Parameter('offset', openapi.IN_QUERY, description="Offset", type=openapi.TYPE_INTEGER),
            openapi.Parameter('sort', openapi.IN_QUERY, description="Sort field", type=openapi.TYPE_STRING),
            openapi.Parameter('job', openapi.IN_QUERY, description="Job title filter", type=openapi.TYPE_STRING, multiple=True),
            openapi.Parameter('resumesource', openapi.IN_QUERY, description="Resume source filter", type=openapi.TYPE_STRING, multiple=True),
            openapi.Parameter('status', openapi.IN_QUERY, description="Status filter", type=openapi.TYPE_STRING, multiple=True),
        ],
        responses={200: ResumeProcessingListSerializer(many=True)}
    )
    def get(self, request):
        user = request.user
        user_role = getattr(user.profile, 'role', 'unknown') if hasattr(user, 'profile') else 'unknown'
        is_rpo_admin = user_role == 'rpo_admin' or user.groups.filter(name='rpo_admin').exists()
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        sort = request.GET.get('sort', '-id')
        filters = {
            'job': request.GET.getlist('job'),
            'resumesource': request.GET.getlist('resumesource'),
            'status': request.GET.getlist('status'),
        }
        resumes, total = ResumeProcessingListService.get_resume_list(user, is_rpo_admin, filters, sort, offset, limit)
        serializer = ResumeProcessingListSerializer(resumes, many=True)
        return Response({
            'results': serializer.data,
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_next': (offset + limit) < total,
            'has_prev': offset > 0,
        })
