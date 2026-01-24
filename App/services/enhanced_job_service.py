"""
Enhanced Job Service - Production Ready
Complete job management with external job board integration support
Database Table: app_job
Supports: JobElephant, ZipRecruiter, Indeed Employer, LinkedIn Recruiter
Author: Reetch Development Team
Date: December 22, 2025
"""
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.db.models import Q, Count, Avg, F
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from App.models import Job, DropdownMaster
from App.models_extended import JobApplication, SavedJob
from App.services.base_generic_service import GenericService, ServiceResponse

logger = logging.getLogger(__name__)


class EnhancedJobService(GenericService):
    """
    Enhanced Job Service with comprehensive job management
    Uses app_job table, integrates with major job boards
    """
    
    model = Job
    
    # Fields to optimize queries
    SELECT_RELATED = [
        'job_category', 'job_type', 'job_level',
        'experience_required', 'qualification_required',
        'gender_preference', 'total_openings', 'job_fee_type',
        'country', 'state_city', 'posted_by'
    ]
    
    SEARCH_FIELDS = [
        'title', 'job_summary', 'responsibilities',
        'qualifications', 'skills', 'permanent_address'
    ]
    
    # ==================== JOB CREATION ====================
    
    def create_job_post(self, data: Dict[str, Any], user: User,
                        publish_to_boards: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new job posting
        
        Args:
            data: Job details dictionary
            user: User posting the job
            publish_to_boards: List of job boards to publish to
                              ['jobelelephant', 'ziprecruiter', 'indeed', 'linkedin']
        
        Returns:
            ServiceResponse with created job and board publication status
        
        Example:
            result = service.create_job_post({
                'title': 'Senior Python Developer',
                'job_summary': 'Looking for experienced developer...',
                'min_salary': 80000,
                'max_salary': 120000,
                'job_category_id': 1,
                'job_type_id': 2,
                'skills': 'Python, Django, PostgreSQL',
                'total_openings_id': 3,
                'deadline': '2025-12-31'
            }, user=request.user, publish_to_boards=['indeed', 'linkedin'])
        """
        try:
            with transaction.atomic():
                # Auto-generate slug if not provided
                if 'slug' not in data or not data['slug']:
                    base_slug = slugify(data.get('title', ''))
                    data['slug'] = self._generate_unique_slug(base_slug)
                
                # Set posted_by
                data['posted_by'] = user
                
                # Set default is_active
                if 'is_active' not in data:
                    data['is_active'] = True
                
                # Create job using base service
                result = self.create(data, user=user)
                
                if not result['success']:
                    return result
                
                job_id = result['data']['id']
                
                # Publish to job boards if requested
                publication_results = {}
                if publish_to_boards:
                    from App.services.job_board_integration_service import JobBoardIntegrationService
                    board_service = JobBoardIntegrationService()
                    
                    for board in publish_to_boards:
                        pub_result = board_service.publish_job(job_id, board)
                        publication_results[board] = pub_result
                
                # Return complete result
                return ServiceResponse.success(
                    data={
                        'job': result['data'],
                        'publications': publication_results
                    },
                    message="Job created successfully"
                )
                
        except Exception as e:
            logger.error(f"Error creating job post: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to create job post",
                errors=str(e),
                code='JOB_CREATE_ERROR'
            )
    
    def _generate_unique_slug(self, base_slug: str) -> str:
        """Generate unique slug for job"""
        slug = base_slug
        counter = 1
        
        while Job.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    # ==================== JOB SEARCH & FILTER ====================
    
    def search_jobs(self, search_query: Optional[str] = None,
                   filters: Optional[Dict[str, Any]] = None,
                   page: int = 1, per_page: int = 20,
                   order_by: str = '-created_at') -> Dict[str, Any]:
        """
        Advanced job search with filters (like JobElephant, ZipRecruiter, Indeed)
        
        Args:
            search_query: Free text search
            filters: Dictionary of filters
                - job_category: Category ID or value
                - job_type: Type ID or value (Full-time, Part-time, etc.)
                - job_level: Level ID or value (Entry, Mid, Senior)
                - min_salary: Minimum salary
                - max_salary: Maximum salary
                - location: City/state
                - experience: Experience level
                - remote: Boolean for remote jobs
                - posted_within_days: Jobs posted in last N days
            page: Page number
            per_page: Results per page
            order_by: Sort field
        
        Returns:
            ServiceResponse with paginated job list
            
        Example:
            result = service.search_jobs(
                search_query='python developer',
                filters={
                    'job_type': 'full_time',
                    'min_salary': 50000,
                    'location': 'New York',
                    'posted_within_days': 30
                },
                page=1,
                per_page=20
            )
        """
        try:
            queryset = Job.objects.select_related(*self.SELECT_RELATED)
            
            # Apply active filter by default
            queryset = queryset.filter(is_active=True)
            
            # Free text search
            if search_query:
                search_q = Q()
                for field in self.SEARCH_FIELDS:
                    search_q |= Q(**{f"{field}__icontains": search_query})
                queryset = queryset.filter(search_q)
            
            # Apply filters
            if filters:
                # Category filter
                if filters.get('job_category'):
                    queryset = queryset.filter(
                        Q(job_category_id=filters['job_category']) |
                        Q(job_category__value=filters['job_category'])
                    )
                
                # Job type filter
                if filters.get('job_type'):
                    queryset = queryset.filter(
                        Q(job_type_id=filters['job_type']) |
                        Q(job_type__value__iexact=filters['job_type'])
                    )
                
                # Job level filter
                if filters.get('job_level'):
                    queryset = queryset.filter(
                        Q(job_level_id=filters['job_level']) |
                        Q(job_level__value__iexact=filters['job_level'])
                    )
                
                # Salary filters
                if filters.get('min_salary'):
                    queryset = queryset.filter(max_salary__gte=filters['min_salary'])
                
                if filters.get('max_salary'):
                    queryset = queryset.filter(min_salary__lte=filters['max_salary'])
                
                # Location filter
                if filters.get('location'):
                    location = filters['location']
                    queryset = queryset.filter(
                        Q(permanent_address__icontains=location) |
                        Q(temporary_address__icontains=location) |
                        Q(state_city__text__icontains=location) |
                        Q(country__text__icontains=location)
                    )
                
                # Experience filter
                if filters.get('experience'):
                    queryset = queryset.filter(
                        Q(experience_required_id=filters['experience']) |
                        Q(experience_required__value__iexact=filters['experience'])
                    )
                
                # Posted within days filter
                if filters.get('posted_within_days'):
                    days = int(filters['posted_within_days'])
                    cutoff_date = timezone.now() - timedelta(days=days)
                    queryset = queryset.filter(created_at__gte=cutoff_date)
                
                # Deadline filter (only active jobs)
                if filters.get('has_active_deadline'):
                    queryset = queryset.filter(
                        deadline__gte=timezone.now().date()
                    )
            
            # Count total before pagination
            total_count = queryset.count()
            
            # Order
            queryset = queryset.order_by(order_by)
            
            # Paginate
            start = (page - 1) * per_page
            end = start + per_page
            jobs = queryset[start:end]
            
            # Serialize jobs
            job_list = []
            for job in jobs:
                job_data = self._serialize_job_detail(job)
                job_list.append(job_data)
            
            return ServiceResponse.paginated(
                data=job_list,
                page=page,
                per_page=per_page,
                total=total_count,
                message=f"Found {total_count} jobs"
            )
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Job search failed",
                errors=str(e),
                code='SEARCH_ERROR'
            )
    
    def get_job_details(self, job_id: int, 
                       increment_views: bool = False) -> Dict[str, Any]:
        """
        Get detailed job information
        
        Args:
            job_id: Job ID
            increment_views: Increment view count if supported
        
        Returns:
            ServiceResponse with detailed job data
        """
        try:
            job = Job.objects.select_related(*self.SELECT_RELATED).get(pk=job_id)
            
            # Get application count
            application_count = JobApplication.objects.filter(job_id=job_id).count()
            
            # Get saved count
            saved_count = SavedJob.objects.filter(job_id=job_id).count()
            
            job_data = self._serialize_job_detail(job)
            job_data['stats'] = {
                'applications': application_count,
                'saved': saved_count,
            }
            
            return ServiceResponse.success(
                data=job_data,
                message="Job details retrieved successfully"
            )
            
        except Job.DoesNotExist:
            return ServiceResponse.error(
                message="Job not found",
                code='NOT_FOUND'
            )
        except Exception as e:
            logger.error(f"Error getting job details: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to retrieve job details",
                errors=str(e)
            )
    
    def get_my_posted_jobs(self, user: User, 
                          filters: Optional[Dict[str, Any]] = None,
                          page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get jobs posted by a specific user (Employer dashboard)
        
        Args:
            user: User who posted the jobs
            filters: Additional filters
            page: Page number
            per_page: Results per page
        
        Returns:
            ServiceResponse with user's job postings
        """
        try:
            queryset = Job.objects.select_related(*self.SELECT_RELATED)#.filter(posted_by=user            )
            
            # Apply additional filters
            if filters:
                if 'is_active' in filters:
                    queryset = queryset.filter(is_active=filters['is_active'])
                
                if 'status' in filters:
                    if filters['status'] == 'active':
                        queryset = queryset.filter(
                            is_active=True,
                            deadline__gte=timezone.now().date()
                        )
                    elif filters['status'] == 'expired':
                        queryset = queryset.filter(
                            deadline__lt=timezone.now().date()
                        )
            
            # Get counts for summary
            total_jobs = queryset.count()
            active_jobs = queryset.filter(is_active=True).count()
            
            # Order by created date
            queryset = queryset.order_by('-created_at')
            
            # Paginate
            start = (page - 1) * per_page
            end = start + per_page
            jobs = queryset[start:end]
            
            # Serialize with application counts
            job_list = []
            for job in jobs:
                job_data = self._serialize_job_detail(job)
                job_data['application_count'] = JobApplication.objects.filter(
                    job_id=job.id
                ).count()
                job_list.append(job_data)
            
            return ServiceResponse.paginated(
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
            
        except Exception as e:
            logger.error(f"Error getting posted jobs: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to retrieve posted jobs",
                errors=str(e)
            )
    
    # ==================== JOB UPDATE & MANAGEMENT ====================
    
    def update_job_post(self, job_id: int, data: Dict[str, Any],
                       user: User, sync_to_boards: bool = False) -> Dict[str, Any]:
        """
        Update job posting
        
        Args:
            job_id: Job ID to update
            data: Updated job data
            user: User performing update
            sync_to_boards: Sync changes to external job boards
        
        Returns:
            ServiceResponse with updated job
        """
        try:
            # Verify ownership
            job = Job.objects.get(pk=job_id, posted_by=user)
            
            # Update using base service
            result = self.update(job_id, data, user=user)
            
            if not result['success']:
                return result
            
            # Sync to job boards if requested
            if sync_to_boards:
                from App.services.job_board_integration_service import JobBoardIntegrationService
                board_service = JobBoardIntegrationService()
                board_service.sync_job_updates(job_id)
            
            return result
            
        except Job.DoesNotExist:
            return ServiceResponse.error(
                message="Job not found or access denied",
                code='NOT_FOUND'
            )
        except Exception as e:
            logger.error(f"Error updating job: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to update job",
                errors=str(e)
            )
    
    def deactivate_job(self, job_id: int, user: User,
                      remove_from_boards: bool = True) -> Dict[str, Any]:
        """
        Deactivate/Close a job posting
        
        Args:
            job_id: Job ID
            user: User deactivating the job
            remove_from_boards: Remove from external job boards
        
        Returns:
            ServiceResponse
        """
        try:
            with transaction.atomic():
                job = Job.objects.get(pk=job_id, posted_by=user)
                job.is_active = False
                job.save()
                
                # Remove from job boards
                if remove_from_boards:
                    from App.services.job_board_integration_service import JobBoardIntegrationService
                    board_service = JobBoardIntegrationService()
                    board_service.remove_job_from_boards(job_id)
                
                logger.info(f"Deactivated job {job_id}")
                
                return ServiceResponse.success(
                    message="Job deactivated successfully"
                )
                
        except Job.DoesNotExist:
            return ServiceResponse.error(
                message="Job not found or access denied",
                code='NOT_FOUND'
            )
        except Exception as e:
            logger.error(f"Error deactivating job: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to deactivate job",
                errors=str(e)
            )
    
    def reactivate_job(self, job_id: int, user: User,
                      republish_to_boards: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Reactivate a job posting
        
        Args:
            job_id: Job ID
            user: User reactivating the job
            republish_to_boards: List of boards to republish to
        
        Returns:
            ServiceResponse
        """
        try:
            with transaction.atomic():
                job = Job.objects.get(pk=job_id, posted_by=user)
                job.is_active = True
                job.save()
                
                # Republish to job boards
                if republish_to_boards:
                    from App.services.job_board_integration_service import JobBoardIntegrationService
                    board_service = JobBoardIntegrationService()
                    
                    for board in republish_to_boards:
                        board_service.publish_job(job_id, board)
                
                logger.info(f"Reactivated job {job_id}")
                
                return ServiceResponse.success(
                    message="Job reactivated successfully"
                )
                
        except Job.DoesNotExist:
            return ServiceResponse.error(
                message="Job not found or access denied",
                code='NOT_FOUND'
            )
        except Exception as e:
            logger.error(f"Error reactivating job: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to reactivate job",
                errors=str(e)
            )
    
    # ==================== ANALYTICS & REPORTING ====================
    
    def get_job_analytics(self, job_id: int, user: User) -> Dict[str, Any]:
        """
        Get analytics for a job posting
        
        Args:
            job_id: Job ID
            user: Job owner
        
        Returns:
            ServiceResponse with analytics data
        """
        try:
            job = Job.objects.get(pk=job_id, posted_by=user)
            
            # Application statistics
            applications = JobApplication.objects.filter(job_id=job_id)
            total_applications = applications.count()
            
            # Group by status if status field exists
            application_stats = {
                'total': total_applications,
                'new': applications.filter(status='pending').count() if hasattr(JobApplication, 'status') else 0,
            }
            
            # Saved statistics
            total_saved = SavedJob.objects.filter(job_id=job_id).count()
            
            # Time analytics
            days_posted = (timezone.now() - job.created_at).days
            days_remaining = (job.deadline - timezone.now().date()).days if job.deadline else None
            
            analytics = {
                'job_id': job_id,
                'title': job.title,
                'created_at': job.created_at.isoformat(),
                'days_posted': days_posted,
                'days_remaining': days_remaining,
                'is_active': job.is_active,
                'applications': application_stats,
                'saved_count': total_saved,
                'engagement': {
                    'applications_per_day': round(total_applications / max(days_posted, 1), 2),
                    'total_engagement': total_applications + total_saved
                }
            }
            
            return ServiceResponse.success(
                data=analytics,
                message="Job analytics retrieved successfully"
            )
            
        except Job.DoesNotExist:
            return ServiceResponse.error(
                message="Job not found or access denied",
                code='NOT_FOUND'
            )
        except Exception as e:
            logger.error(f"Error getting job analytics: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to retrieve analytics",
                errors=str(e)
            )
    
    # ==================== HELPER METHODS ====================
    
    def _serialize_job_detail(self, job: Job) -> Dict[str, Any]:
        """
        Serialize job instance as a flat dict with string keys/values, matching the required API response format.
        """
        return {
            "title": job.title or "",
            "jobSummary": job.job_summary or "",
            "responsibilities": job.responsibilities or "",
            "qualifications": job.qualifications or "",
            "skills": job.skills or "",
            "jobCategory": (job.job_category.value if job.job_category and hasattr(job.job_category, 'value') else ""),
            "jobType": (job.job_type.value if job.job_type and hasattr(job.job_type, 'value') else ""),
            "jobLevel": (job.job_level.value if job.job_level and hasattr(job.job_level, 'value') else ""),
            "experience": (job.experience_required.value if job.experience_required and hasattr(job.experience_required, 'value') else ""),
            "qualification": (job.qualification_required.value if job.qualification_required and hasattr(job.qualification_required, 'value') else ""),
            "gender": (job.gender_preference.value if hasattr(job, 'gender_preference') and job.gender_preference and hasattr(job.gender_preference, 'value') else ""),
            "minSalary": str(job.min_salary) if job.min_salary is not None else "",
            "maxSalary": str(job.max_salary) if job.max_salary is not None else "",
            "startDate": job.start_date.isoformat() if job.start_date else "",
            "deadline": job.deadline.isoformat() if job.deadline else "",
            "totalOpenings": (job.total_openings.label if job.total_openings and hasattr(job.total_openings, 'label') else ""),
            "jobFeeType": (job.job_fee_type.value if hasattr(job, 'job_fee_type') and job.job_fee_type and hasattr(job.job_fee_type, 'value') else ""),
            "permanentAddress": job.permanent_address or "",
            "temporaryAddress": job.temporary_address or "",
            "country": (job.country.label if job.country and hasattr(job.country, 'label') else ""),
            "city": (job.state_city.label if job.state_city and hasattr(job.state_city, 'label') else ""),
            "zipCode": job.zip_code or "",
            "videoUrl": job.video_url or "",
            "latitude": str(job.latitude) if job.latitude is not None else "",
            "longitude": str(job.longitude) if job.longitude is not None else "",
            "job_id": str(job.id) if job.id is not None else "",
        }
    
    def get_dropdown_options(self, group_value: str) -> Dict[str, Any]:
        """
        Get dropdown options for job forms
        
        Args:
            group_value: Dropdown group value (job_category, job_type, etc.)
        
        Returns:
            ServiceResponse with dropdown options
        """
        try:
            options = DropdownMaster.objects.filter(
                group__value=group_value,
                is_active=True
            ).values('id', 'text', 'value')
            
            return ServiceResponse.success(
                data={'options': list(options)},
                message=f"Retrieved {group_value} options"
            )
            
        except Exception as e:
            logger.error(f"Error getting dropdown options: {e}")
            return ServiceResponse.error(
                message="Failed to retrieve options",
                errors=str(e)
            )


# Convenience instance for direct import
job_service = EnhancedJobService()
