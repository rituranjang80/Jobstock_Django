"""
Django Template-Based Views (MVT Pattern)
All business logic is in services - views are thin controllers

Author: Reetch Development Team
Date: December 22, 2025
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from App.models import Job
from App.forms.job_forms import JobPostForm, JobSearchForm, JobApplicationForm, ApplicationStatusForm
from App.services.enhanced_job_service import job_service
from App.services.job_application_service import application_service
from App.services.job_board_integration_service import job_board_service


# ==================== PUBLIC JOB VIEWS ====================

def job_list_view(request):
    """
    Public job listing page with search and filters
    Similar to Indeed, ZipRecruiter interfaces
    """
    form = JobSearchForm(request.GET or None)
    
    # Build filters from form
    filters = {}
    search_query = None
    
    if form.is_valid():
        if form.cleaned_data.get('q'):
            search_query = form.cleaned_data['q']
        
        if form.cleaned_data.get('job_category'):
            filters['job_category'] = form.cleaned_data['job_category'].id
        
        if form.cleaned_data.get('job_type'):
            filters['job_type'] = form.cleaned_data['job_type'].value
        
        if form.cleaned_data.get('job_level'):
            filters['job_level'] = form.cleaned_data['job_level'].value
        
        if form.cleaned_data.get('location'):
            filters['location'] = form.cleaned_data['location']
        
        if form.cleaned_data.get('min_salary'):
            filters['min_salary'] = form.cleaned_data['min_salary']
        
        if form.cleaned_data.get('max_salary'):
            filters['max_salary'] = form.cleaned_data['max_salary']
        
        if form.cleaned_data.get('posted_within_days'):
            filters['posted_within_days'] = form.cleaned_data['posted_within_days']
    
    # Get page number
    page = request.GET.get('page', 1)
    
    # Call service
    result = job_service.search_jobs(
        search_query=search_query,
        filters=filters,
        page=int(page),
        per_page=20
    )
    
    context = {
        'form': form,
        'jobs': result.get('data', []) if result['success'] else [],
        'pagination': result.get('pagination', {}) if result['success'] else {},
        'total_jobs': result.get('total', 0) if result['success'] else 0,
    }
    
    return render(request, 'jobs/job_list.html', context)


def job_detail_view(request, job_id):
    """Job detail page"""
    result = job_service.get_job_details(job_id, increment_views=True)
    
    if not result['success']:
        messages.error(request, result['message'])
        return redirect('job_list')
    
    context = {
        'job': result['data'],
        'application_form': JobApplicationForm()
    }
    
    return render(request, 'jobs/job_detail.html', context)


@require_http_methods(["POST"])
def job_apply_view(request, job_id):
    """Handle job application submission"""
    form = JobApplicationForm(request.POST, request.FILES)
    
    if form.is_valid():
        # Prepare applicant data
        applicant_data = {
            'name': form.cleaned_data['applicant_name'],
            'email': form.cleaned_data['applicant_email'],
            'phone': form.cleaned_data.get('applicant_phone'),
            'cover_letter': form.cleaned_data.get('cover_letter'),
        }
        
        # Add user if logged in
        if request.user.is_authenticated:
            applicant_data['user'] = request.user
        
        # Submit application via service
        result = application_service.submit_application(
            job_id=job_id,
            applicant_data=applicant_data,
            resume_file=form.cleaned_data['resume'],
            source='direct'
        )
        
        if result['success']:
            messages.success(request, "Application submitted successfully!")
            return redirect('job_detail', job_id=job_id)
        else:
            messages.error(request, result['message'])
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    
    return redirect('job_detail', job_id=job_id)


# ==================== EMPLOYER JOB MANAGEMENT ====================

@login_required
def employer_dashboard_view(request):
    """Employer dashboard showing posted jobs"""
    # Get filter from query params
    status_filter = request.GET.get('status', 'all')
    page = request.GET.get('page', 1)
    
    filters = {}
    if status_filter == 'active':
        filters['status'] = 'active'
    elif status_filter == 'expired':
        filters['status'] = 'expired'
    elif status_filter == 'inactive':
        filters['is_active'] = False
    
    # Get jobs via service
    result = job_service.get_my_posted_jobs(
        user=request.user,
        filters=filters,
        page=int(page),
        per_page=10
    )
    
    context = {
        'jobs': result.get('data', []) if result['success'] else [],
        'pagination': result.get('pagination', {}) if result['success'] else {},
        'summary': result.get('summary', {}) if result['success'] else {},
        'status_filter': status_filter
    }
    
    return render(request, 'employer/dashboard.html', context)


@login_required
def job_post_create_view(request):
    """Create new job post"""
    if request.method == 'POST':
        form = JobPostForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Get selected job boards
            selected_boards = form.get_selected_boards()
            
            # Prepare job data (exclude job board fields)
            job_data = {k: v for k, v in form.cleaned_data.items() 
                       if not k.startswith('publish_to_')}
            
            # Create job via service
            result = job_service.create_job_post(
                data=job_data,
                user=request.user,
                publish_to_boards=selected_boards if selected_boards else None
            )
            
            if result['success']:
                messages.success(request, "Job posted successfully!")
                
                # Show publication results
                if 'publications' in result['data']:
                    for board, pub_result in result['data']['publications'].items():
                        if pub_result['success']:
                            messages.success(request, f"Published to {board.title()}")
                        else:
                            messages.warning(request, f"Failed to publish to {board.title()}")
                
                return redirect('employer_dashboard')
            else:
                messages.error(request, result['message'])
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = JobPostForm()
    
    context = {'form': form}
    return render(request, 'employer/job_form.html', context)


@login_required
def job_post_edit_view(request, job_id):
    """Edit existing job post"""
    # Get job via service (ensures ownership)
    result = job_service.get_job_details(job_id)
    
    if not result['success']:
        messages.error(request, "Job not found or access denied")
        return redirect('employer_dashboard')
    
    # Get actual model instance for form
    job = get_object_or_404(Job, pk=job_id, posted_by=request.user)
    
    if request.method == 'POST':
        form = JobPostForm(request.POST, request.FILES, instance=job)
        
        if form.is_valid():
            # Update via service
            update_data = {k: v for k, v in form.cleaned_data.items() 
                          if not k.startswith('publish_to_')}
            
            result = job_service.update_job_post(
                job_id=job_id,
                data=update_data,
                user=request.user,
                sync_to_boards=True  # Sync changes to job boards
            )
            
            if result['success']:
                messages.success(request, "Job updated successfully!")
                return redirect('employer_dashboard')
            else:
                messages.error(request, result['message'])
    else:
        form = JobPostForm(instance=job)
    
    context = {'form': form, 'job': job}
    return render(request, 'employer/job_form.html', context)


@login_required
@require_http_methods(["POST"])
def job_deactivate_view(request, job_id):
    """Deactivate a job posting"""
    result = job_service.deactivate_job(
        job_id=job_id,
        user=request.user,
        remove_from_boards=True
    )
    
    if result['success']:
        messages.success(request, "Job deactivated successfully")
    else:
        messages.error(request, result['message'])
    
    return redirect('employer_dashboard')


@login_required
@require_http_methods(["POST"])
def job_reactivate_view(request, job_id):
    """Reactivate a job posting"""
    result = job_service.reactivate_job(
        job_id=job_id,
        user=request.user,
        republish_to_boards=['indeed', 'ziprecruiter']  # Example
    )
    
    if result['success']:
        messages.success(request, "Job reactivated successfully")
    else:
        messages.error(request, result['message'])
    
    return redirect('employer_dashboard')


# ==================== APPLICATION MANAGEMENT ====================

@login_required
def job_applications_view(request, job_id):
    """View applications for a job"""
    page = request.GET.get('page', 1)
    status_filter = request.GET.get('status')
    source_filter = request.GET.get('source')
    
    filters = {}
    if status_filter:
        filters['status'] = status_filter
    if source_filter:
        filters['source'] = source_filter
    
    result = application_service.get_job_applications(
        job_id=job_id,
        user=request.user,
        filters=filters,
        page=int(page),
        per_page=20
    )
    
    if not result['success']:
        messages.error(request, result['message'])
        return redirect('employer_dashboard')
    
    context = {
        'job_id': job_id,
        'applications': result.get('data', []),
        'pagination': result.get('pagination', {}),
        'stats': result.get('stats', {}),
        'status_filter': status_filter,
        'source_filter': source_filter,
    }
    
    return render(request, 'employer/applications.html', context)


@login_required
def application_detail_view(request, application_id):
    """View single application details"""
    result = application_service.get_application_details(
        application_id=application_id,
        user=request.user
    )
    
    if not result['success']:
        messages.error(request, result['message'])
        return redirect('employer_dashboard')
    
    status_form = ApplicationStatusForm()
    
    context = {
        'application': result['data'],
        'status_form': status_form
    }
    
    return render(request, 'employer/application_detail.html', context)


@login_required
@require_http_methods(["POST"])
def application_update_status_view(request, application_id):
    """Update application status"""
    form = ApplicationStatusForm(request.POST)
    
    if form.is_valid():
        result = application_service.update_application_status(
            application_id=application_id,
            status=form.cleaned_data['status'],
            user=request.user,
            notes=form.cleaned_data.get('notes')
        )
        
        if result['success']:
            messages.success(request, "Application status updated")
        else:
            messages.error(request, result['message'])
    
    return redirect('application_detail', application_id=application_id)


# ==================== AJAX/JSON ENDPOINTS ====================

@login_required
def job_analytics_ajax(request, job_id):
    """Get job analytics (AJAX endpoint)"""
    result = job_service.get_job_analytics(job_id, request.user)
    return JsonResponse(result)


@login_required
@require_http_methods(["POST"])
def bulk_application_status_ajax(request):
    """Bulk update application statuses (AJAX endpoint)"""
    import json
    
    try:
        data = json.loads(request.body)
        application_ids = data.get('application_ids', [])
        status = data.get('status')
        
        result = application_service.bulk_update_status(
            application_ids=application_ids,
            status=status,
            user=request.user
        )
        
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
