from django.urls import path


from .resume_management import RPOResumeUploadAPI
from .process_resumes import RPOProcessResumesAPI
from .resume_matching import (
    ResumeMatchingDashboardAPI,
    ViewMatchDetailsAPI,
    MatchResumeToJobsAPI,
    MatchJobToResumesAPI,
    TopCandidatesForJobAPI,
    TopJobsForResumeAPI,
    RecalculateMatchAPI,
    MatchSingleResumeJobAPI,
)

urlpatterns = [
    path('rpo/resume-upload/', RPOResumeUploadAPI.as_view(), name='rpo_resume_upload_api'),
    path('rpo/process-resumes/', RPOProcessResumesAPI.as_view(), name='rpo_process_resumes_api'),

    # Resume-Job Matching REST API
    path('resume-matching/', ResumeMatchingDashboardAPI.as_view(), name='resume_matching_dashboard_api'),
    path('resume-matching/match-details/<int:match_id>/', ViewMatchDetailsAPI.as_view(), name='view_match_details_api'),
    path('resume-matching/match-resume/<int:resume_id>/', MatchResumeToJobsAPI.as_view(), name='match_resume_to_jobs_api'),
    path('resume-matching/match-job/<int:job_id>/', MatchJobToResumesAPI.as_view(), name='match_job_to_resumes_api'),
    path('resume-matching/top-candidates/<int:job_id>/', TopCandidatesForJobAPI.as_view(), name='top_candidates_for_job_api'),
    path('resume-matching/top-jobs/<int:resume_id>/', TopJobsForResumeAPI.as_view(), name='top_jobs_for_resume_api'),
    path('resume-matching/recalculate/<int:match_id>/', RecalculateMatchAPI.as_view(), name='recalculate_match_api'),
    path('resume-matching/match-single/', MatchSingleResumeJobAPI.as_view(), name='match_single_resume_job_api'),
]
