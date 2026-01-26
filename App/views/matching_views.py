"""
Resume-Job Matching Views
MVT views for AI-powered resume matching system
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from App.models import ResumeJobMatch, ResumeProcessing, Job, DropdownGroup, DropdownMaster
from App.services.resume_matching_service import ResumeJobMatchingService
from App.tasks_matching import (
    match_resume_to_job_task,
    match_resume_to_all_jobs_task,
    match_all_resumes_to_job_task
)


def check_rpo_admin_access(request):
    """Check if user has RPO Admin access"""
    user_role = request.user.profile.role if hasattr(request.user, 'profile') else 'unknown'
    is_rpo_admin = user_role == 'rpo_admin' or request.user.groups.filter(name='rpo_admin').exists()
    return is_rpo_admin or request.user.is_superuser


@login_required
def resume_matching_dashboard(request):
    """
    Resume Matching Dashboard
    Shows overview of all matches, statistics, and quick actions
    """
    # Check if user is RPO Admin
    if not check_rpo_admin_access(request):
        messages.error(request, 'Access denied. RPO Admin role required.')
        return redirect('App:index')
    
    # Get filter parameters
    match_quality = request.GET.get('quality', '')
    job_id = request.GET.get('job', '')
    resume_id = request.GET.get('resume', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    matches = ResumeJobMatch.objects.select_related(
        'job', 'resume', 'matched_by'
    ).filter(status='completed')
    
    # Apply filters
    if match_quality:
        matches = matches.filter(match_quality=match_quality)
    if job_id:
        matches = matches.filter(job_id=job_id)
    if resume_id:
        matches = matches.filter(resume_id=resume_id)
    if search:
        matches = matches.filter(
            Q(job__title__icontains=search) |
            Q(resume__user__username__icontains=search) |
            Q(resume__user__first_name__icontains=search) |
            Q(resume__user__last_name__icontains=search) |
            Q(resume__profile__full_name__icontains=search) |
            Q(resume__original_filename__icontains=search)
        )
    
    # Order by match percentage
    matches = matches.order_by('-overall_match_percentage', '-created_at')
    
    # Pagination
    paginator = Paginator(matches, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Statistics - Build base queryset for stats with same filters as main queryset
    stats_queryset = ResumeJobMatch.objects.filter(status='completed')
    
    # Apply same filters to stats
    if match_quality:
        stats_queryset = stats_queryset.filter(match_quality=match_quality)
    if job_id:
        stats_queryset = stats_queryset.filter(job_id=job_id)
    if resume_id:
        stats_queryset = stats_queryset.filter(resume_id=resume_id)
    if search:
        stats_queryset = stats_queryset.filter(
            Q(job__title__icontains=search) |
            Q(resume__user__username__icontains=search) |
            Q(resume__user__first_name__icontains=search) |
            Q(resume__user__last_name__icontains=search) |
            Q(resume__profile__full_name__icontains=search) |
            Q(resume__original_filename__icontains=search)
        )
    
    # Calculate statistics from filtered queryset
    stats = {
        'total_matches': stats_queryset.count(),
        'excellent_matches': stats_queryset.filter(match_quality='excellent').count(),
        'good_matches': stats_queryset.filter(match_quality='good').count(),
        'recommended_matches': stats_queryset.filter(is_recommended=True).count(),
        'avg_match_percentage': stats_queryset.aggregate(
            Avg('overall_match_percentage')
        )['overall_match_percentage__avg'] or 0,
    }
    
    # Get active jobs and completed resumes for filters
    active_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:50]
    completed_resumes = ResumeProcessing.objects.filter(
        status='completed'
    ).order_by('-created_at')[:50]
    
    # Get ResumeSource companies for dropdown
    try:
        resume_source_group = DropdownGroup.objects.get(value='ResumeSource', is_active=True)
        resume_sources = DropdownMaster.objects.filter(group=resume_source_group, is_active=True).order_by('sort_order', 'label')
    except DropdownGroup.DoesNotExist:
        resume_sources = []
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'active_jobs': active_jobs,
        'completed_resumes': completed_resumes,
        'resume_sources': resume_sources,
        'current_filters': {
            'quality': match_quality,
            'job': job_id,
            'resume': resume_id,
            'search': search,
        },
        'search': search,
    }
    
    return render(request, 'Pages/RPO-Admin/resume_matching_dashboard.html', context)


@login_required
def match_resume_to_jobs(request, resume_id):
    """
    Match a specific resume to all active jobs
    """
    # Check if user is RPO Admin
    if not check_rpo_admin_access(request):
        messages.error(request, 'Access denied. RPO Admin role required.')
        return redirect('App:index')
    resume = get_object_or_404(ResumeProcessing, id=resume_id, status='completed')
    
    if request.method == 'POST':
        # Run background task
        task = match_resume_to_all_jobs_task.delay(resume_id, request.user.id)
        messages.success(
            request, 
            f"Matching job started for {resume.candidate_name}. "
            f"Task ID: {task.id}"
        )
        return redirect('App:resume_matching_dashboard')
    
    # Show confirmation page
    active_jobs_count = Job.objects.filter(is_active=True).count()
    context = {
        'resume': resume,
        'active_jobs_count': active_jobs_count
    }
    return render(request, 'Pages/RPO-Admin/match_resume_confirm.html', context)


@login_required
def match_job_to_resumes(request, job_id):
    """
    Match a specific job to all completed resumes
    """
    # Check if user is RPO Admin
    if not check_rpo_admin_access(request):
        messages.error(request, 'Access denied. RPO Admin role required.')
        return redirect('App:index')
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    if request.method == 'POST':
        # Run background task
        task = match_all_resumes_to_job_task.delay(job_id, request.user.id)
        messages.success(
            request, 
            f"Matching job started for {job.title}. "
            f"Task ID: {task.id}"
        )
        return redirect('App:resume_matching_dashboard')
    
    # Show confirmation page
    completed_resumes_count = ResumeProcessing.objects.filter(
        status='completed'
    ).count()
    context = {
        'job': job,
        'completed_resumes_count': completed_resumes_count
    }
    return render(request, 'Pages/RPO-Admin/match_job_confirm.html', context)


@login_required
def view_match_details(request, match_id):
    """
    View detailed analysis of a specific match
    """
    # Check if user is RPO Admin
    if not check_rpo_admin_access(request):
        messages.error(request, 'Access denied. RPO Admin role required.')
        return redirect('App:index')
    match = get_object_or_404(
        ResumeJobMatch.objects.select_related('job', 'resume', 'matched_by'),
        id=match_id
    )
    context = {
        'match': match,
        'detailed_analysis': match.detailed_analysis or {}
    }
    return render(request, 'Pages/RPO-Admin/match_details.html', context)
@login_required
def top_candidates_for_job(request, job_id):
    """
    View top matching candidates for a specific job
    """
    # Check if user is RPO Admin
    if not check_rpo_admin_access(request):
        messages.error(request, 'Access denied. RPO Admin role required.')
        return redirect('App:index')
    job = get_object_or_404(Job, id=job_id, is_active=True)
    # Get top matches
    result = ResumeJobMatchingService.get_top_candidates_for_job(job_id, limit=20)
    if not result.success:
        messages.error(request, result.message)
        return redirect('App:resume_matching_dashboard')
    matches = result.data.get('matches', [])
    context = {
        'job': job,
        'matches': matches,
        'total_matches': result.data.get('total_matches', 0)
    }
    return render(request, 'Pages/RPO-Admin/top_candidates.html', context)

@login_required
def top_jobs_for_resume(request, resume_id):
    """
    View top matching jobs for a specific resume
    """
    # Check if user is RPO Admin
    if not check_rpo_admin_access(request):
        messages.error(request, 'Access denied. RPO Admin role required.')
        return redirect('App:index')
    resume = get_object_or_404(ResumeProcessing, id=resume_id)
    # Get top matches
    result = ResumeJobMatchingService.get_top_jobs_for_resume(resume_id, limit=20)
    if not result.success:
        messages.error(request, result.message)
        return redirect('App:resume_matching_dashboard')
    matches = result.data.get('matches', [])
    context = {
        'resume': resume,
        'matches': matches,
        'total_matches': result.data.get('total_matches', 0)
    }
    return render(request, 'Pages/RPO-Admin/top_jobs.html', context)


@login_required
@require_http_methods(['POST'])
def recalculate_match(request, match_id):
    """
    Recalculate a specific match
    """
    # Check if user is RPO Admin
    if not check_rpo_admin_access(request):
        messages.error(request, 'Access denied. RPO Admin role required.')
        return redirect('App:index')
    match = get_object_or_404(ResumeJobMatch, id=match_id)
    
    # Run synchronous recalculation
    result = ResumeJobMatchingService.match_resume_to_job(
        match.job_id,
        match.resume_id,
        request.user
    )
    
    if result.success:
        messages.success(
            request, 
            f"Match recalculated: {result.data.get('overall_match', 0):.2f}%"
        )
    else:
        messages.error(request, f"Recalculation failed: {result.message}")
    
    return redirect('App:view_match_details', match_id=match_id)


@login_required
def match_single_resume_job(request):
    """
    Match a single resume to a single job (AJAX)
    """
    # Check if user is RPO Admin
    if not check_rpo_admin_access(request):
        return JsonResponse({
            'success': False,
            'message': 'Access denied. RPO Admin role required.'
        }, status=403)
    if request.method == 'POST':
        resume_id = request.POST.get('resume_id')
        job_id = request.POST.get('job_id')
        
        if not resume_id or not job_id:
            return JsonResponse({
                'success': False,
                'message': 'Resume ID and Job ID are required'
            }, status=400)
        
        # Run synchronous matching
        result = ResumeJobMatchingService.match_resume_to_job(
            job_id,
            resume_id,
            request.user
        )
        
        return JsonResponse({
            'success': result.success,
            'message': result.message,
            'data': result.data
        })
    
    return JsonResponse({
        'success': False,
        'message': 'POST method required'
    }, status=405)
