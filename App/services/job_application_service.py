"""
Job Application Service
Handles resume submissions from both direct applications and external job boards
(JobElephant, ZipRecruiter, Indeed, LinkedIn)

Author: Reetch Development Team
Date: December 22, 2025
"""
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone
import logging
import base64
import requests

from App.models import Job
from App.models_extended import JobApplication, CandidateProfile
from App.services.base_generic_service import GenericService, ServiceResponse

logger = logging.getLogger(__name__)


class JobApplicationService(GenericService):
    """
    Service for managing job applications and resume submissions
    Handles applications from multiple sources
    """
    
    model = JobApplication
    
    # ==================== APPLICATION SUBMISSION ====================
    
    def submit_application(self, job_id: int, applicant_data: Dict[str, Any],
                          resume_file: Any = None, 
                          source: str = 'direct') -> Dict[str, Any]:
        """
        Submit a job application
        
        Args:
            job_id: Job ID to apply for
            applicant_data: Dictionary with applicant information
                - name/full_name: Applicant's full name
                - email: Email address
                - phone: Phone number
                - cover_letter: Optional cover letter
                - user_id: Optional user ID if logged in
            resume_file: Resume file upload
            source: Application source ('direct', 'indeed', 'ziprecruiter', 'linkedin', 'jobelephant')
        
        Returns:
            ServiceResponse with application details
            
        Example:
            result = service.submit_application(
                job_id=123,
                applicant_data={
                    'name': 'John Doe',
                    'email': 'john@example.com',
                    'phone': '555-1234',
                    'cover_letter': 'I am interested in...'
                },
                resume_file=request.FILES['resume'],
                source='direct'
            )
        """
        try:
            with transaction.atomic():
                # Verify job exists and is active
                job = Job.objects.get(pk=job_id, is_active=True)
                
                # Prepare application data
                application_data = {
                    'job_id': job_id,
                    'applicant_name': applicant_data.get('name') or applicant_data.get('full_name'),
                    'applicant_email': applicant_data.get('email'),
                    'applicant_phone': applicant_data.get('phone'),
                    'cover_letter': applicant_data.get('cover_letter'),
                    'source': source,
                    'status': 'pending',
                }
                
                # Link to user if provided
                if applicant_data.get('user_id'):
                    application_data['user_id'] = applicant_data['user_id']
                elif applicant_data.get('user'):
                    application_data['user'] = applicant_data['user']
                
                # Handle resume file
                if resume_file:
                    application_data['resume'] = resume_file
                
                # Create application
                application = JobApplication(**application_data)
                application.full_clean()
                application.save()
                
                logger.info(f"Application submitted for job {job_id} from {source}")
                
                # Send notification (implement as needed)
                self._send_application_notification(application, job)
                
                return ServiceResponse.success(
                    data=self._serialize_application(application),
                    message="Application submitted successfully"
                )
                
        except Job.DoesNotExist:
            return ServiceResponse.error(
                message="Job not found or no longer active",
                code='JOB_NOT_FOUND'
            )
        except Exception as e:
            logger.error(f"Error submitting application: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to submit application",
                errors=str(e),
                code='APPLICATION_ERROR'
            )
    
    def receive_external_application(self, job_external_id: str, board: str,
                                    application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive application from external job board via webhook/API
        
        Args:
            job_external_id: External job ID from the board
            board: Source board name
            application_data: Application data from the board
        
        Returns:
            ServiceResponse
        """
        try:
            with transaction.atomic():
                # Find internal job ID
                # TODO: Query JobBoardMapping to get internal job_id
                # For now, assume job_external_id is our internal ID
                job_id = self._resolve_external_job_id(job_external_id, board)
                
                if not job_id:
                    return ServiceResponse.error(
                        message="Job mapping not found",
                        code='MAPPING_ERROR'
                    )
                
                # Download resume if URL provided
                resume_file = None
                if application_data.get('resume_url'):
                    resume_file = self._download_resume(application_data['resume_url'])
                
                # Submit application
                applicant_data = {
                    'name': application_data.get('candidate_name') or application_data.get('name'),
                    'email': application_data.get('candidate_email') or application_data.get('email'),
                    'phone': application_data.get('candidate_phone') or application_data.get('phone'),
                    'cover_letter': application_data.get('cover_letter'),
                }
                
                return self.submit_application(
                    job_id=job_id,
                    applicant_data=applicant_data,
                    resume_file=resume_file,
                    source=board
                )
                
        except Exception as e:
            logger.error(f"Error receiving external application: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to process external application",
                errors=str(e)
            )
    
    # ==================== APPLICATION MANAGEMENT ====================
    
    def get_job_applications(self, job_id: int, user: Optional[User] = None,
                            filters: Optional[Dict[str, Any]] = None,
                            page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get all applications for a job
        
        Args:
            job_id: Job ID
            user: Optional user to verify job ownership
            filters: Optional filters (status, source, date_range)
            page: Page number
            per_page: Items per page
        
        Returns:
            ServiceResponse with paginated applications
        """
        try:
            # Verify job access if user provided
            if user:
                job = Job.objects.get(pk=job_id, posted_by=user)
            else:
                job = Job.objects.get(pk=job_id)
            
            queryset = JobApplication.objects.filter(job_id=job_id)
            
            # Apply filters
            if filters:
                if filters.get('status'):
                    queryset = queryset.filter(status=filters['status'])
                
                if filters.get('source'):
                    queryset = queryset.filter(source=filters['source'])
                
                if filters.get('date_from'):
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                
                if filters.get('date_to'):
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
            
            # Count total
            total = queryset.count()
            
            # Order by date (newest first)
            queryset = queryset.order_by('-created_at')
            
            # Paginate
            start = (page - 1) * per_page
            end = start + per_page
            applications = queryset[start:end]
            
            # Serialize
            app_list = [self._serialize_application(app) for app in applications]
            
            # Get statistics
            stats = self._get_application_stats(job_id)
            
            return ServiceResponse.paginated(
                data=app_list,
                page=page,
                per_page=per_page,
                total=total,
                stats=stats,
                message=f"Retrieved {total} applications"
            )
            
        except Job.DoesNotExist:
            return ServiceResponse.error(
                message="Job not found or access denied",
                code='NOT_FOUND'
            )
        except Exception as e:
            logger.error(f"Error getting applications: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to retrieve applications",
                errors=str(e)
            )
    
    def get_application_details(self, application_id: int,
                               user: Optional[User] = None) -> Dict[str, Any]:
        """
        Get detailed application information
        
        Args:
            application_id: Application ID
            user: Optional user to verify access
        
        Returns:
            ServiceResponse with application details
        """
        try:
            queryset = JobApplication.objects.select_related('job', 'user')
            
            if user:
                # Verify user is job owner or applicant
                application = queryset.filter(
                    Q(id=application_id) & 
                    (Q(job__posted_by=user) | Q(user=user))
                ).first()
                
                if not application:
                    return ServiceResponse.error(
                        message="Application not found or access denied",
                        code='NOT_FOUND'
                    )
            else:
                application = queryset.get(pk=application_id)
            
            return ServiceResponse.success(
                data=self._serialize_application(application, detailed=True),
                message="Application retrieved successfully"
            )
            
        except JobApplication.DoesNotExist:
            return ServiceResponse.error(
                message="Application not found",
                code='NOT_FOUND'
            )
        except Exception as e:
            logger.error(f"Error getting application details: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to retrieve application",
                errors=str(e)
            )
    
    def update_application_status(self, application_id: int, status: str,
                                 user: User, notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Update application status
        
        Args:
            application_id: Application ID
            status: New status ('pending', 'reviewed', 'shortlisted', 'rejected', 'accepted')
            user: User making the update (must be job owner)
            notes: Optional notes
        
        Returns:
            ServiceResponse
        """
        try:
            with transaction.atomic():
                application = JobApplication.objects.select_related('job').get(
                    pk=application_id,
                    job__posted_by=user
                )
                
                old_status = application.status
                application.status = status
                
                if notes and hasattr(application, 'notes'):
                    application.notes = notes
                
                application.save()
                
                logger.info(f"Application {application_id} status changed from {old_status} to {status}")
                
                # Send notification to applicant
                self._send_status_update_notification(application, old_status, status)
                
                return ServiceResponse.success(
                    data=self._serialize_application(application),
                    message="Application status updated successfully"
                )
                
        except JobApplication.DoesNotExist:
            return ServiceResponse.error(
                message="Application not found or access denied",
                code='NOT_FOUND'
            )
        except Exception as e:
            logger.error(f"Error updating application status: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to update application status",
                errors=str(e)
            )
    
    def bulk_update_status(self, application_ids: List[int], status: str,
                          user: User) -> Dict[str, Any]:
        """
        Bulk update application statuses
        
        Args:
            application_ids: List of application IDs
            status: New status to set
            user: User making the update
        
        Returns:
            ServiceResponse
        """
        try:
            with transaction.atomic():
                applications = JobApplication.objects.filter(
                    pk__in=application_ids,
                    job__posted_by=user
                )
                
                count = applications.update(status=status)
                
                logger.info(f"Bulk updated {count} applications to status {status}")
                
                return ServiceResponse.success(
                    data={'updated_count': count},
                    message=f"{count} applications updated successfully"
                )
                
        except Exception as e:
            logger.error(f"Error in bulk status update: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to bulk update applications",
                errors=str(e)
            )
    
    # ==================== HELPER METHODS ====================
    
    def _serialize_application(self, application: JobApplication,
                              detailed: bool = False) -> Dict[str, Any]:
        """Serialize application instance"""
        data = {
            'id': application.id,
            'applicant_name': application.applicant_name,
            'applicant_email': application.applicant_email,
            'applicant_phone': application.applicant_phone,
            'source': application.source if hasattr(application, 'source') else 'direct',
            'status': application.status if hasattr(application, 'status') else 'pending',
            'created_at': application.created_at.isoformat() if hasattr(application, 'created_at') else None,
        }
        
        # Add resume URL if exists
        if hasattr(application, 'resume') and application.resume:
            data['resume_url'] = application.resume.url
        
        # Add cover letter if exists
        if hasattr(application, 'cover_letter'):
            data['cover_letter'] = application.cover_letter
        
        # Add detailed info if requested
        if detailed:
            if hasattr(application, 'job'):
                data['job'] = {
                    'id': application.job.id,
                    'title': application.job.title,
                    'company': application.job.posted_by.get_full_name() if application.job.posted_by else None,
                }
            
            if hasattr(application, 'notes'):
                data['notes'] = application.notes
        
        return data
    
    def _get_application_stats(self, job_id: int) -> Dict[str, int]:
        """Get application statistics for a job"""
        queryset = JobApplication.objects.filter(job_id=job_id)
        
        stats = {
            'total': queryset.count(),
            'by_source': {},
            'by_status': {}
        }
        
        # Count by source
        if hasattr(JobApplication, 'source'):
            from django.db.models import Count
            source_counts = queryset.values('source').annotate(count=Count('id'))
            stats['by_source'] = {item['source']: item['count'] for item in source_counts}
        
        # Count by status
        if hasattr(JobApplication, 'status'):
            from django.db.models import Count
            status_counts = queryset.values('status').annotate(count=Count('id'))
            stats['by_status'] = {item['status']: item['count'] for item in status_counts}
        
        return stats
    
    def _resolve_external_job_id(self, external_id: str, board: str) -> Optional[int]:
        """Resolve external job ID to internal job ID"""
        # TODO: Query JobBoardMapping model
        # mapping = JobBoardMapping.objects.filter(
        #     external_id=external_id,
        #     board=board
        # ).first()
        # return mapping.job_id if mapping else None
        
        # For now, try to extract numeric ID
        try:
            return int(external_id.split('_')[-1])
        except:
            return None
    
    def _download_resume(self, url: str) -> Optional[ContentFile]:
        """Download resume from external URL"""
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                filename = url.split('/')[-1]
                return ContentFile(response.content, name=filename)
        except Exception as e:
            logger.error(f"Error downloading resume: {e}")
        
        return None
    
    def _send_application_notification(self, application: JobApplication, 
                                      job: Job) -> None:
        """Send notification to employer about new application"""
        # TODO: Implement email notification
        logger.info(f"Would send notification about application {application.id} to {job.posted_by.email if job.posted_by else 'unknown'}")
    
    def _send_status_update_notification(self, application: JobApplication,
                                        old_status: str, new_status: str) -> None:
        """Send notification to applicant about status change"""
        # TODO: Implement email notification
        logger.info(f"Would send status update notification to {application.applicant_email}")


# Convenience instance
application_service = JobApplicationService()
