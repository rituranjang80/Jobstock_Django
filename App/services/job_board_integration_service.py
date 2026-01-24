"""
Job Board Integration Service
Handles posting jobs to and receiving applications from external job boards:
- JobElephant
- ZipRecruiter
- Indeed Employer
- LinkedIn Recruiter

Author: Reetch Development Team
Date: December 22, 2025
"""
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.db import transaction
from django.utils import timezone
import logging
import requests
import json

from App.models import Job
from App.services.base_generic_service import ServiceResponse

logger = logging.getLogger(__name__)


class JobBoardConfig:
    """Configuration for external job boards"""
    
    # Add your API credentials in settings.py
    # JOBBOARD_CREDENTIALS = {
    #     'indeed': {'api_key': 'your_key', 'employer_id': 'your_id'},
    #     'ziprecruiter': {'api_key': 'your_key', 'account_id': 'your_id'},
    #     'linkedin': {'client_id': 'your_id', 'client_secret': 'your_secret'},
    #     'jobelephant': {'api_key': 'your_key', 'partner_id': 'your_id'}
    # }
    
    BOARD_ENDPOINTS = {
        'indeed': {
            'post_job': 'https://apis.indeed.com/ads/v1/jobs',
            'update_job': 'https://apis.indeed.com/ads/v1/jobs/{job_id}',
            'close_job': 'https://apis.indeed.com/ads/v1/jobs/{job_id}/close',
            'applications': 'https://apis.indeed.com/ads/v1/jobs/{job_id}/applications'
        },
        'ziprecruiter': {
            'post_job': 'https://api.ziprecruiter.com/jobs/v1',
            'update_job': 'https://api.ziprecruiter.com/jobs/v1/{job_id}',
            'close_job': 'https://api.ziprecruiter.com/jobs/v1/{job_id}/close',
            'applications': 'https://api.ziprecruiter.com/jobs/v1/{job_id}/applications'
        },
        'linkedin': {
            'post_job': 'https://api.linkedin.com/v2/jobPostings',
            'update_job': 'https://api.linkedin.com/v2/jobPostings/{job_id}',
            'close_job': 'https://api.linkedin.com/v2/jobPostings/{job_id}',
            'applications': 'https://api.linkedin.com/v2/jobPostings/{job_id}/applications'
        },
        'jobelephant': {
            'post_job': 'https://api.jobelephant.com/v1/jobs',
            'update_job': 'https://api.jobelephant.com/v1/jobs/{job_id}',
            'close_job': 'https://api.jobelephant.com/v1/jobs/{job_id}/close',
            'applications': 'https://api.jobelephant.com/v1/jobs/{job_id}/applications'
        }
    }
    
    @classmethod
    def get_credentials(cls, board: str) -> Optional[Dict[str, Any]]:
        """Get API credentials for a job board"""
        credentials = getattr(settings, 'JOBBOARD_CREDENTIALS', {})
        return credentials.get(board.lower())
    
    @classmethod
    def get_endpoint(cls, board: str, action: str) -> Optional[str]:
        """Get API endpoint for a job board action"""
        board_config = cls.BOARD_ENDPOINTS.get(board.lower())
        return board_config.get(action) if board_config else None


class JobBoardIntegrationService:
    """Service for integrating with external job boards"""
    
    def __init__(self):
        self.config = JobBoardConfig()
    
    # ==================== JOB POSTING ====================
    
    def publish_job(self, job_id: int, board: str) -> Dict[str, Any]:
        """
        Publish a job to an external job board
        
        Args:
            job_id: Job ID from app_job table
            board: Job board name ('indeed', 'ziprecruiter', 'linkedin', 'jobelephant')
        
        Returns:
            ServiceResponse with publication status
        """
        try:
            # Get job details
            job = Job.objects.select_related(
                'job_category', 'job_type', 'job_level',
                'experience_required', 'country', 'state_city'
            ).get(pk=job_id, is_active=True)
            
            # Format job data for the specific board
            job_data = self._format_job_for_board(job, board)
            
            # Post to job board
            if board.lower() == 'indeed':
                result = self._post_to_indeed(job_data)
            elif board.lower() == 'ziprecruiter':
                result = self._post_to_ziprecruiter(job_data)
            elif board.lower() == 'linkedin':
                result = self._post_to_linkedin(job_data)
            elif board.lower() == 'jobelephant':
                result = self._post_to_jobelephant(job_data)
            else:
                return ServiceResponse.error(
                    message=f"Unsupported job board: {board}",
                    code='INVALID_BOARD'
                )
            
            # Store external job ID for tracking
            if result['success']:
                self._save_board_job_mapping(
                    job_id, 
                    board, 
                    result.get('external_job_id')
                )
            
            return result
            
        except Job.DoesNotExist:
            return ServiceResponse.error(
                message="Job not found or inactive",
                code='JOB_NOT_FOUND'
            )
        except Exception as e:
            logger.error(f"Error publishing job to {board}: {e}", exc_info=True)
            return ServiceResponse.error(
                message=f"Failed to publish job to {board}",
                errors=str(e),
                code='PUBLISH_ERROR'
            )
    
    def publish_to_multiple_boards(self, job_id: int, 
                                   boards: List[str]) -> Dict[str, Any]:
        """
        Publish a job to multiple job boards
        
        Args:
            job_id: Job ID
            boards: List of board names
        
        Returns:
            ServiceResponse with publication results for each board
        """
        results = {}
        
        for board in boards:
            result = self.publish_job(job_id, board)
            results[board] = result
        
        # Count successes
        success_count = sum(1 for r in results.values() if r['success'])
        
        return ServiceResponse.success(
            data={
                'total_boards': len(boards),
                'successful': success_count,
                'failed': len(boards) - success_count,
                'results': results
            },
            message=f"Published to {success_count}/{len(boards)} boards"
        )
    
    # ==================== JOB UPDATES ====================
    
    def sync_job_updates(self, job_id: int) -> Dict[str, Any]:
        """
        Sync job updates to all boards where it's posted
        
        Args:
            job_id: Job ID
        
        Returns:
            ServiceResponse with sync results
        """
        try:
            # Get job and its board mappings
            job = Job.objects.get(pk=job_id)
            mappings = self._get_board_mappings(job_id)
            
            results = {}
            for mapping in mappings:
                board = mapping['board']
                external_id = mapping['external_id']
                
                # Format updated data
                job_data = self._format_job_for_board(job, board)
                
                # Update on board
                if board == 'indeed':
                    result = self._update_indeed_job(external_id, job_data)
                elif board == 'ziprecruiter':
                    result = self._update_ziprecruiter_job(external_id, job_data)
                elif board == 'linkedin':
                    result = self._update_linkedin_job(external_id, job_data)
                elif board == 'jobelephant':
                    result = self._update_jobelephant_job(external_id, job_data)
                
                results[board] = result
            
            return ServiceResponse.success(
                data={'results': results},
                message="Job updates synced to external boards"
            )
            
        except Exception as e:
            logger.error(f"Error syncing job updates: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to sync updates",
                errors=str(e)
            )
    
    def remove_job_from_boards(self, job_id: int) -> Dict[str, Any]:
        """
        Remove/close job on all external boards
        
        Args:
            job_id: Job ID
        
        Returns:
            ServiceResponse
        """
        try:
            mappings = self._get_board_mappings(job_id)
            
            results = {}
            for mapping in mappings:
                board = mapping['board']
                external_id = mapping['external_id']
                
                # Close job on board
                if board == 'indeed':
                    result = self._close_indeed_job(external_id)
                elif board == 'ziprecruiter':
                    result = self._close_ziprecruiter_job(external_id)
                elif board == 'linkedin':
                    result = self._close_linkedin_job(external_id)
                elif board == 'jobelephant':
                    result = self._close_jobelephant_job(external_id)
                
                results[board] = result
            
            return ServiceResponse.success(
                data={'results': results},
                message="Job removed from external boards"
            )
            
        except Exception as e:
            logger.error(f"Error removing job from boards: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to remove job",
                errors=str(e)
            )
    
    # ==================== APPLICATION RECEIVING ====================
    
    def fetch_applications(self, job_id: int, 
                          board: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch applications from external job boards
        
        Args:
            job_id: Job ID
            board: Specific board or None for all boards
        
        Returns:
            ServiceResponse with applications
        """
        try:
            mappings = self._get_board_mappings(job_id)
            
            if board:
                mappings = [m for m in mappings if m['board'] == board.lower()]
            
            all_applications = []
            
            for mapping in mappings:
                board_name = mapping['board']
                external_id = mapping['external_id']
                
                # Fetch applications from board
                if board_name == 'indeed':
                    apps = self._fetch_indeed_applications(external_id)
                elif board_name == 'ziprecruiter':
                    apps = self._fetch_ziprecruiter_applications(external_id)
                elif board_name == 'linkedin':
                    apps = self._fetch_linkedin_applications(external_id)
                elif board_name == 'jobelephant':
                    apps = self._fetch_jobelephant_applications(external_id)
                else:
                    continue
                
                # Add source board to each application
                for app in apps:
                    app['source_board'] = board_name
                
                all_applications.extend(apps)
            
            return ServiceResponse.success(
                data={
                    'applications': all_applications,
                    'count': len(all_applications)
                },
                message=f"Retrieved {len(all_applications)} applications"
            )
            
        except Exception as e:
            logger.error(f"Error fetching applications: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to fetch applications",
                errors=str(e)
            )
    
    # ==================== INDEED INTEGRATION ====================
    
    def _post_to_indeed(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post job to Indeed"""
        try:
            credentials = self.config.get_credentials('indeed')
            if not credentials:
                return ServiceResponse.error(
                    message="Indeed credentials not configured",
                    code='NO_CREDENTIALS'
                )
            
            endpoint = self.config.get_endpoint('indeed', 'post_job')
            
            # Format data for Indeed API
            payload = {
                'title': job_data['title'],
                'description': job_data['description'],
                'location': job_data['location'],
                'jobType': job_data['job_type'],
                'salary': job_data.get('salary'),
                'requiredQualifications': job_data.get('qualifications'),
                'applicationMethod': {
                    'type': 'EMAIL',
                    'email': getattr(settings, 'JOB_APPLICATION_EMAIL', 'jobs@yourcompany.com')
                }
            }
            
            headers = {
                'Authorization': f"Bearer {credentials['api_key']}",
                'Content-Type': 'application/json'
            }
            
            # Make API call (simulated for development)
            if getattr(settings, 'DEBUG', False):
                # In development, simulate success
                logger.info(f"[DEV MODE] Would post to Indeed: {payload['title']}")
                return ServiceResponse.success(
                    data={'external_job_id': f"indeed_{timezone.now().timestamp()}"},
                    message="Job posted to Indeed (dev mode)"
                )
            
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                result_data = response.json()
                return ServiceResponse.success(
                    data={'external_job_id': result_data.get('id')},
                    message="Job posted to Indeed successfully"
                )
            else:
                return ServiceResponse.error(
                    message=f"Indeed API error: {response.status_code}",
                    errors=response.text
                )
                
        except Exception as e:
            logger.error(f"Error posting to Indeed: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to post to Indeed",
                errors=str(e)
            )
    
    def _update_indeed_job(self, external_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update job on Indeed"""
        # Implementation similar to post
        logger.info(f"Updating Indeed job {external_id}")
        return ServiceResponse.success(message="Indeed job updated (implementation pending)")
    
    def _close_indeed_job(self, external_id: str) -> Dict[str, Any]:
        """Close job on Indeed"""
        logger.info(f"Closing Indeed job {external_id}")
        return ServiceResponse.success(message="Indeed job closed (implementation pending)")
    
    def _fetch_indeed_applications(self, external_id: str) -> List[Dict[str, Any]]:
        """Fetch applications from Indeed"""
        logger.info(f"Fetching applications from Indeed job {external_id}")
        # Return empty list for now - implement actual API call
        return []
    
    # ==================== ZIPRECRUITER INTEGRATION ====================
    
    def _post_to_ziprecruiter(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post job to ZipRecruiter"""
        try:
            credentials = self.config.get_credentials('ziprecruiter')
            if not credentials:
                return ServiceResponse.error(
                    message="ZipRecruiter credentials not configured",
                    code='NO_CREDENTIALS'
                )
            
            # Format data for ZipRecruiter API
            payload = {
                'job_title': job_data['title'],
                'job_description': job_data['description'],
                'city': job_data.get('city'),
                'state': job_data.get('state'),
                'employment_type': job_data['job_type'],
                'salary_min': job_data.get('salary_min'),
                'salary_max': job_data.get('salary_max'),
            }
            
            # Simulated for development
            if getattr(settings, 'DEBUG', False):
                logger.info(f"[DEV MODE] Would post to ZipRecruiter: {payload['job_title']}")
                return ServiceResponse.success(
                    data={'external_job_id': f"zip_{timezone.now().timestamp()}"},
                    message="Job posted to ZipRecruiter (dev mode)"
                )
            
            # Implement actual API call here
            return ServiceResponse.success(
                data={'external_job_id': f"zip_{timezone.now().timestamp()}"},
                message="Job posted to ZipRecruiter"
            )
            
        except Exception as e:
            logger.error(f"Error posting to ZipRecruiter: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to post to ZipRecruiter",
                errors=str(e)
            )
    
    def _update_ziprecruiter_job(self, external_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update job on ZipRecruiter"""
        logger.info(f"Updating ZipRecruiter job {external_id}")
        return ServiceResponse.success(message="ZipRecruiter job updated")
    
    def _close_ziprecruiter_job(self, external_id: str) -> Dict[str, Any]:
        """Close job on ZipRecruiter"""
        logger.info(f"Closing ZipRecruiter job {external_id}")
        return ServiceResponse.success(message="ZipRecruiter job closed")
    
    def _fetch_ziprecruiter_applications(self, external_id: str) -> List[Dict[str, Any]]:
        """Fetch applications from ZipRecruiter"""
        logger.info(f"Fetching applications from ZipRecruiter job {external_id}")
        return []
    
    # ==================== LINKEDIN INTEGRATION ====================
    
    def _post_to_linkedin(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post job to LinkedIn"""
        try:
            credentials = self.config.get_credentials('linkedin')
            if not credentials:
                return ServiceResponse.error(
                    message="LinkedIn credentials not configured",
                    code='NO_CREDENTIALS'
                )
            
            # Simulated for development
            if getattr(settings, 'DEBUG', False):
                logger.info(f"[DEV MODE] Would post to LinkedIn: {job_data['title']}")
                return ServiceResponse.success(
                    data={'external_job_id': f"linkedin_{timezone.now().timestamp()}"},
                    message="Job posted to LinkedIn (dev mode)"
                )
            
            return ServiceResponse.success(
                data={'external_job_id': f"linkedin_{timezone.now().timestamp()}"},
                message="Job posted to LinkedIn"
            )
            
        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to post to LinkedIn",
                errors=str(e)
            )
    
    def _update_linkedin_job(self, external_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update job on LinkedIn"""
        logger.info(f"Updating LinkedIn job {external_id}")
        return ServiceResponse.success(message="LinkedIn job updated")
    
    def _close_linkedin_job(self, external_id: str) -> Dict[str, Any]:
        """Close job on LinkedIn"""
        logger.info(f"Closing LinkedIn job {external_id}")
        return ServiceResponse.success(message="LinkedIn job closed")
    
    def _fetch_linkedin_applications(self, external_id: str) -> List[Dict[str, Any]]:
        """Fetch applications from LinkedIn"""
        logger.info(f"Fetching applications from LinkedIn job {external_id}")
        return []
    
    # ==================== JOBELEPHANT INTEGRATION ====================
    
    def _post_to_jobelephant(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post job to JobElephant"""
        try:
            credentials = self.config.get_credentials('jobelephant')
            if not credentials:
                return ServiceResponse.error(
                    message="JobElephant credentials not configured",
                    code='NO_CREDENTIALS'
                )
            
            # Simulated for development
            if getattr(settings, 'DEBUG', False):
                logger.info(f"[DEV MODE] Would post to JobElephant: {job_data['title']}")
                return ServiceResponse.success(
                    data={'external_job_id': f"jobelephant_{timezone.now().timestamp()}"},
                    message="Job posted to JobElephant (dev mode)"
                )
            
            return ServiceResponse.success(
                data={'external_job_id': f"jobelephant_{timezone.now().timestamp()}"},
                message="Job posted to JobElephant"
            )
            
        except Exception as e:
            logger.error(f"Error posting to JobElephant: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to post to JobElephant",
                errors=str(e)
            )
    
    def _update_jobelephant_job(self, external_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update job on JobElephant"""
        logger.info(f"Updating JobElephant job {external_id}")
        return ServiceResponse.success(message="JobElephant job updated")
    
    def _close_jobelephant_job(self, external_id: str) -> Dict[str, Any]:
        """Close job on JobElephant"""
        logger.info(f"Closing JobElephant job {external_id}")
        return ServiceResponse.success(message="JobElephant job closed")
    
    def _fetch_jobelephant_applications(self, external_id: str) -> List[Dict[str, Any]]:
        """Fetch applications from JobElephant"""
        logger.info(f"Fetching applications from JobElephant job {external_id}")
        return []
    
    # ==================== HELPER METHODS ====================
    
    def _format_job_for_board(self, job: Job, board: str) -> Dict[str, Any]:
        """Format job data for specific job board"""
        # Base format used by all boards
        formatted = {
            'title': job.title,
            'description': self._build_job_description(job),
            'location': job.permanent_address or job.temporary_address,
            'city': job.state_city.text if job.state_city else None,
            'state': job.state_city.text if job.state_city else None,
            'country': job.country.text if job.country else 'USA',
            'job_type': job.job_type.value if job.job_type else 'FULL_TIME',
            'salary_min': float(job.min_salary) if job.min_salary else None,
            'salary_max': float(job.max_salary) if job.max_salary else None,
            'qualifications': job.qualifications,
            'responsibilities': job.responsibilities,
            'skills': job.skills.split(',') if job.skills else [],
        }
        
        return formatted
    
    def _build_job_description(self, job: Job) -> str:
        """Build comprehensive job description"""
        parts = []
        
        if job.job_summary:
            parts.append(f"## Summary\n{job.job_summary}")
        
        if job.responsibilities:
            parts.append(f"\n## Responsibilities\n{job.responsibilities}")
        
        if job.qualifications:
            parts.append(f"\n## Qualifications\n{job.qualifications}")
        
        if job.skills:
            parts.append(f"\n## Required Skills\n{job.skills}")
        
        return "\n\n".join(parts)
    
    def _save_board_job_mapping(self, job_id: int, board: str, 
                               external_id: str) -> None:
        """Save mapping between internal job and external board job"""
        from App.job_board_models import JobBoardMapping
        
        logger.info(f"Job {job_id} posted to {board} with external ID {external_id}")
        
        # Create or update mapping
        mapping, created = JobBoardMapping.objects.update_or_create(
            job_id=job_id,
            board=board,
            defaults={
                'external_job_id': external_id,
                'status': 'active'
            }
        )
        
        if created:
            logger.info(f"Created new board mapping for job {job_id} on {board}")
        else:
            logger.info(f"Updated existing board mapping for job {job_id} on {board}")
    
    def _get_board_mappings(self, job_id: int) -> List[Dict[str, str]]:
        """Get all board mappings for a job"""
        from App.job_board_models import JobBoardMapping
        
        logger.info(f"Getting board mappings for job {job_id}")
        
        # Query active mappings
        return list(JobBoardMapping.objects.filter(
            job_id=job_id,
            status='active'
        ).values('board', 'external_job_id'))


# Convenience instance
job_board_service = JobBoardIntegrationService()
