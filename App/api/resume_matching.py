
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from App.api.response_mixin import APIResponseMixin
from App.models import ResumeJobMatch
from App.services.resume_matching_service import ResumeJobMatchingService

class ResumeMatchingDashboardAPI(APIResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get resume-job matching dashboard data",
        tags=["resume_management"],
        responses={200: openapi.Response("Dashboard data")}
    )
    def get(self, request):
        stats = {
            'total_matches': ResumeJobMatch.objects.count(),
            'excellent': ResumeJobMatch.objects.filter(match_quality='excellent').count(),
            'good': ResumeJobMatch.objects.filter(match_quality='good').count(),
            'fair': ResumeJobMatch.objects.filter(match_quality='fair').count(),
            'poor': ResumeJobMatch.objects.filter(match_quality='poor').count(),
        }
        return self.api_response(data={'stats': stats}, message="Dashboard stats fetched successfully")

class ViewMatchDetailsAPI(APIResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get details for a specific match",
        tags=["resume_management"],
        responses={200: openapi.Response("Match details")}
    )
    def get(self, request, match_id):
        try:
            match = ResumeJobMatch.objects.select_related('job', 'resume__user').get(id=match_id)
            data = {
                'match_id': match.id,
                'job_id': match.job.id,
                'job_title': match.job.title,
                'resume_id': match.resume.id,
                'candidate_name': match.resume.user.get_full_name() or match.resume.user.username,
                'overall_match': float(match.overall_match_percentage),
                'match_quality': match.match_quality,
                'is_recommended': match.is_recommended,
                'skills_match': float(match.skills_match_percentage),
                'experience_match': float(match.experience_match_percentage),
                'matching_skills': match.matching_skills,
                'success_reasons': match.success_reasons,
                'failure_reasons': match.failure_reasons,
                'created_at': match.created_at.isoformat(),
            }
            return self.api_response(data=data, message="Match details fetched successfully")
        except ResumeJobMatch.DoesNotExist:
            return self.api_response(data=None, status_code=404, message="Match not found")

class MatchResumeToJobsAPI(APIResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Match a resume to all jobs",
        tags=["resume_management"],
        responses={200: openapi.Response("Match started")}
    )
    def post(self, request, resume_id):
        result = ResumeJobMatchingService.match_resume_to_all_jobs(resume_id, user=request.user)
        return self.api_response(data=result.data, status_code=200 if result.success else 400, message=result.message)

class MatchJobToResumesAPI(APIResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Match a job to all resumes (returns top matches)",
        tags=["resume_management"],
        responses={200: openapi.Response("Match started")}
    )
    def post(self, request, job_id):
        result = ResumeJobMatchingService.get_top_matches_for_job(job_id, limit=20)
        return self.api_response(data=result.data, status_code=200 if result.success else 400, message=result.message)

    @swagger_auto_schema(
        operation_description="Match a job to all resumes (returns top matches) [GET]",
        tags=["resume_management"],
        responses={200: openapi.Response("Match started")}
    )
    def get(self, request, job_id):
        result = ResumeJobMatchingService.get_top_matches_for_job(job_id, limit=20)
        return self.api_response(data=result.data, status_code=200 if result.success else 400, message=result.message)

class TopCandidatesForJobAPI(APIResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get top candidates for a job",
        tags=["resume_management"],
        responses={200: openapi.Response("Top candidates")}
    )
    def get(self, request, job_id):
        result = ResumeJobMatchingService.get_top_matches_for_job(job_id, limit=10)
        return self.api_response(data=result.data, status_code=200 if result.success else 400, message=result.message)

class TopJobsForResumeAPI(APIResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get top jobs for a resume",
        tags=["resume_management"],
        responses={200: openapi.Response("Top jobs")}
    )
    def get(self, request, resume_id):
        result = ResumeJobMatchingService.get_top_jobs_for_resume(resume_id, limit=10)
        return self.api_response(data=result.data, status_code=200 if result.success else 400, message=result.message)

class RecalculateMatchAPI(APIResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Recalculate a specific match",
        tags=["resume_management"],
        responses={200: openapi.Response("Recalculation started")}
    )
    def post(self, request, match_id):
        try:
            match = ResumeJobMatch.objects.get(id=match_id)
            result = ResumeJobMatchingService.match_resume_to_job(match.job.id, match.resume.id, user=request.user)
            return self.api_response(data=result.data, status_code=200 if result.success else 400, message=result.message)
        except ResumeJobMatch.DoesNotExist:
            return self.api_response(data=None, status_code=404, message="Match not found")

class MatchSingleResumeJobAPI(APIResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Match a single resume to a single job",
        tags=["resume_management"],
        manual_parameters=[
            openapi.Parameter('job_id', openapi.IN_QUERY, description="Job ID", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('resume_id', openapi.IN_QUERY, description="Resume ID", type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={200: openapi.Response("Single match result")}
    )
    def post(self, request):
        job_id = request.data.get('job_id') or request.query_params.get('job_id')
        resume_id = request.data.get('resume_id') or request.query_params.get('resume_id')
        if not job_id or not resume_id:
            return self.api_response(data=None, status_code=400, message="job_id and resume_id are required")
        result = ResumeJobMatchingService.match_resume_to_job(int(job_id), int(resume_id), user=request.user)
        return self.api_response(data=result.data, status_code=200 if result.success else 400, message=result.message)

