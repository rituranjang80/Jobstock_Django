"""
Resume Job Matching Service
AI-powered resume-to-job matching with detailed analysis
"""
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime
from django.db.models import Q
from django.utils import timezone
import re
import json

from App.models import Job, ResumeProcessing, ResumeJobMatch
from App.services.base_service import BaseService
from App.utils.response import ApiResponse


class ResumeJobMatchingService(BaseService):
    """Service for matching resumes to job postings"""
    
    @classmethod
    def calculate_skills_match(cls, resume_skills: str, job_skills: str) -> Dict:
        """
        Calculate skills compatibility between resume and job
        
        Args:
            resume_skills: Comma-separated skills from resume
            job_skills: Comma-separated required skills from job
            
        Returns:
            Dict with matching_skills, missing_skills, additional_skills, percentage
        """
        if not resume_skills or not job_skills:
            return {
                'matching_skills': [],
                'missing_skills': job_skills.split(',') if job_skills else [],
                'additional_skills': [],
                'percentage': 0.0
            }
        
        # Normalize and split skills
        resume_skills_list = [s.strip().lower() for s in resume_skills.split(',') if s.strip()]
        job_skills_list = [s.strip().lower() for s in job_skills.split(',') if s.strip()]
        
        # Find matching skills
        matching_skills = []
        for job_skill in job_skills_list:
            for resume_skill in resume_skills_list:
                # Check for exact match or partial match
                if job_skill in resume_skill or resume_skill in job_skill:
                    if resume_skill not in matching_skills:
                        matching_skills.append(resume_skill)
                    break
        
        # Find missing skills
        missing_skills = []
        for job_skill in job_skills_list:
            found = False
            for resume_skill in resume_skills_list:
                if job_skill in resume_skill or resume_skill in job_skill:
                    found = True
                    break
            if not found:
                missing_skills.append(job_skill)
        
        # Find additional skills
        additional_skills = [s for s in resume_skills_list if s not in matching_skills]
        
        # Calculate percentage
        if len(job_skills_list) == 0:
            percentage = 100.0
        else:
            percentage = (len(matching_skills) / len(job_skills_list)) * 100.0
        
        return {
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'additional_skills': additional_skills,
            'percentage': round(percentage, 2)
        }
    
    @classmethod
    def calculate_experience_match(cls, resume_exp: str, job_exp_required: str) -> Dict:
        """
        Calculate experience level compatibility
        
        Args:
            resume_exp: Years of experience from resume (e.g., "5 years")
            job_exp_required: Experience requirement text from job
            
        Returns:
            Dict with percentage and analysis
        """
        if not resume_exp or not job_exp_required:
            return {'percentage': 50.0, 'match': 'Unknown', 'reason': 'Insufficient data'}
        
        # Extract years from resume experience
        resume_years = 0
        resume_match = re.search(r'(\d+)', str(resume_exp))
        if resume_match:
            resume_years = int(resume_match.group(1))
        
        # Extract required years from job (patterns like "3-5 years", "5+ years", etc.)
        job_exp_lower = job_exp_required.lower()
        
        # Try to extract minimum required years
        min_required = 0
        max_required = 100
        
        # Pattern: "3-5 years"
        range_match = re.search(r'(\d+)\s*-\s*(\d+)', job_exp_lower)
        if range_match:
            min_required = int(range_match.group(1))
            max_required = int(range_match.group(2))
        # Pattern: "5+ years" or "5 years"
        else:
            single_match = re.search(r'(\d+)', job_exp_lower)
            if single_match:
                min_required = int(single_match.group(1))
                max_required = min_required + 5
        
        # Calculate match percentage
        if resume_years >= min_required and resume_years <= max_required:
            percentage = 100.0
            match = 'Perfect Match'
            reason = f'{resume_years} years meets requirement of {job_exp_required}'
        elif resume_years >= min_required:
            # Over-qualified
            excess = resume_years - max_required
            if excess <= 2:
                percentage = 90.0
                match = 'Over-qualified (Acceptable)'
                reason = f'{resume_years} years exceeds requirement by {excess} years'
            else:
                percentage = 70.0
                match = 'Over-qualified'
                reason = f'{resume_years} years significantly exceeds requirement'
        elif resume_years < min_required:
            # Under-qualified
            shortage = min_required - resume_years
            if shortage <= 1:
                percentage = 80.0
                match = 'Slightly Under-qualified'
                reason = f'{resume_years} years, short by {shortage} year'
            elif shortage <= 2:
                percentage = 60.0
                match = 'Under-qualified'
                reason = f'{resume_years} years, short by {shortage} years'
            else:
                percentage = 30.0
                match = 'Significantly Under-qualified'
                reason = f'{resume_years} years, short by {shortage} years'
        else:
            percentage = 0.0
            match = 'No Match'
            reason = 'Cannot determine experience level'
        
        return {
            'percentage': round(percentage, 2),
            'match': match,
            'reason': reason,
            'resume_years': resume_years,
            'required_range': f'{min_required}-{max_required}'
        }
    
    @classmethod
    def calculate_location_match(cls, resume_location: str, job_location: str) -> Dict:
        """
        Calculate location compatibility
        
        Args:
            resume_location: Location from resume
            job_location: Job location requirement
            
        Returns:
            Dict with percentage and analysis
        """
        if not job_location:
            return {'percentage': 100.0, 'match': 'No location requirement'}
        
        if not resume_location:
            return {'percentage': 50.0, 'match': 'Unknown location'}
        
        resume_loc = resume_location.lower().strip()
        job_loc = job_location.lower().strip()
        
        # Exact match
        if resume_loc == job_loc or job_loc in resume_loc or resume_loc in job_loc:
            return {'percentage': 100.0, 'match': 'Same location'}
        
        # Check for same city/state
        resume_parts = resume_loc.split(',')
        job_parts = job_loc.split(',')
        
        for r_part in resume_parts:
            for j_part in job_parts:
                if r_part.strip() in j_part.strip() or j_part.strip() in r_part.strip():
                    return {'percentage': 90.0, 'match': 'Nearby location'}
        
        return {'percentage': 40.0, 'match': 'Different location (Remote work possible)'}
    
    @classmethod
    def analyze_sentiment_impact(cls, sentiment_score: float) -> Dict:
        """
        Analyze how resume sentiment affects match quality
        
        Args:
            sentiment_score: Polarity score from -1 to 1
            
        Returns:
            Dict with impact analysis
        """
        if sentiment_score is None:
            return {
                'impact': 'neutral',
                'impact_percentage': 0.0,
                'description': 'No sentiment analysis available'
            }
        
        if sentiment_score >= 0.3:
            return {
                'impact': 'positive',
                'impact_percentage': 5.0,
                'description': 'Positive tone enhances profile (+5%)'
            }
        elif sentiment_score >= 0.1:
            return {
                'impact': 'slightly_positive',
                'impact_percentage': 2.0,
                'description': 'Slightly positive tone (+2%)'
            }
        elif sentiment_score <= -0.3:
            return {
                'impact': 'negative',
                'impact_percentage': -5.0,
                'description': 'Negative tone impacts profile (-5%)'
            }
        elif sentiment_score <= -0.1:
            return {
                'impact': 'slightly_negative',
                'impact_percentage': -2.0,
                'description': 'Slightly negative tone (-2%)'
            }
        else:
            return {
                'impact': 'neutral',
                'impact_percentage': 0.0,
                'description': 'Neutral tone (no impact)'
            }
    
    @classmethod
    def generate_success_reasons(cls, skills_data: Dict, exp_data: Dict, loc_data: Dict, sentiment_data: Dict) -> List[str]:
        """Generate list of reasons why candidate is a good match"""
        reasons = []
        
        # Skills
        if skills_data['percentage'] >= 80:
            reasons.append(f"Excellent skills match ({skills_data['percentage']}%) - has {len(skills_data['matching_skills'])} required skills")
        elif skills_data['percentage'] >= 60:
            reasons.append(f"Good skills match ({skills_data['percentage']}%) - has most required skills")
        
        if len(skills_data['additional_skills']) > 0:
            reasons.append(f"Has {len(skills_data['additional_skills'])} additional valuable skills")
        
        # Experience
        if exp_data['percentage'] >= 80:
            reasons.append(f"{exp_data['match']} - {exp_data['reason']}")
        
        # Location
        if loc_data['percentage'] >= 90:
            reasons.append(f"Location: {loc_data['match']}")
        
        # Sentiment
        if sentiment_data['impact_percentage'] > 0:
            reasons.append(sentiment_data['description'])
        
        return reasons
    
    @classmethod
    def generate_failure_reasons(cls, skills_data: Dict, exp_data: Dict, loc_data: Dict, sentiment_data: Dict) -> List[str]:
        """Generate list of reasons why candidate doesn't match well"""
        reasons = []
        
        # Skills
        if skills_data['percentage'] < 40:
            reasons.append(f"Low skills match ({skills_data['percentage']}%) - missing critical skills")
        
        if len(skills_data['missing_skills']) > 0:
            missing_count = min(5, len(skills_data['missing_skills']))
            missing_list = ', '.join(skills_data['missing_skills'][:missing_count])
            reasons.append(f"Missing {len(skills_data['missing_skills'])} required skills: {missing_list}")
        
        # Experience
        if exp_data['percentage'] < 60:
            reasons.append(f"{exp_data['match']} - {exp_data['reason']}")
        
        # Location
        if loc_data['percentage'] < 50:
            reasons.append(f"Location mismatch - {loc_data['match']}")
        
        # Sentiment
        if sentiment_data['impact_percentage'] < 0:
            reasons.append(sentiment_data['description'])
        
        return reasons
    
    @classmethod
    def generate_improvement_suggestions(cls, skills_data: Dict, exp_data: Dict) -> List[str]:
        """Generate suggestions for improving match score"""
        suggestions = []
        
        # Skills suggestions
        if len(skills_data['missing_skills']) > 0:
            top_missing = ', '.join(skills_data['missing_skills'][:3])
            suggestions.append(f"Acquire or highlight these skills: {top_missing}")
        
        # Experience suggestions
        if exp_data['percentage'] < 80:
            if 'Under-qualified' in exp_data['match']:
                suggestions.append(f"Gain more experience in the field (currently {exp_data.get('resume_years', 0)} years)")
            suggestions.append("Highlight relevant projects and achievements")
        
        # General suggestions
        if skills_data['percentage'] < 100:
            suggestions.append("Tailor resume to emphasize skills mentioned in job description")
        
        suggestions.append("Use action verbs and quantify achievements")
        suggestions.append("Ensure resume has positive, professional tone")
        
        return suggestions
    
    @classmethod
    def calculate_overall_match(cls, job: Job, resume: ResumeProcessing) -> Dict:
        """
        Calculate comprehensive match between resume and job
        
        Args:
            job: Job instance
            resume: ResumeProcessing instance
            
        Returns:
            Dict with complete matching analysis
        """
        try:
            # Skills matching (40% weight)
            skills_analysis = cls.calculate_skills_match(
                resume.extracted_skills or '',
                job.skills or ''
            )
            
            # Experience matching (30% weight)
            job_exp = job.experience_required.value if job.experience_required else ''
            exp_analysis = cls.calculate_experience_match(
                resume.years_of_experience or '',
                job_exp
            )
            
            # Location matching (15% weight)
            resume_loc = resume.resume_json.get('location', '') if resume.resume_json else ''
            job_loc = job.state_city.value if job.state_city else ''
            loc_analysis = cls.calculate_location_match(resume_loc, job_loc)
            
            # Qualification matching (10% weight) - simplified
            qual_percentage = 75.0  # Default moderate match
            
            # Sentiment analysis (5% weight)
            sentiment_analysis = cls.analyze_sentiment_impact(resume.sentiment_score or 0.0)
            
            # Calculate weighted overall percentage
            overall_percentage = (
                (skills_analysis['percentage'] * 0.40) +
                (exp_analysis['percentage'] * 0.30) +
                (loc_analysis['percentage'] * 0.15) +
                (qual_percentage * 0.10) +
                (50.0 * 0.05)  # Base sentiment weight
            ) + sentiment_analysis['impact_percentage']
            
            # Ensure within 0-100 range
            overall_percentage = max(0.0, min(100.0, overall_percentage))
            
            # Generate reasons
            success_reasons = cls.generate_success_reasons(
                skills_analysis, exp_analysis, loc_analysis, sentiment_analysis
            )
            failure_reasons = cls.generate_failure_reasons(
                skills_analysis, exp_analysis, loc_analysis, sentiment_analysis
            )
            improvement_suggestions = cls.generate_improvement_suggestions(
                skills_analysis, exp_analysis
            )
            
            # Determine match quality
            if overall_percentage >= 80:
                match_quality = 'excellent'
                is_recommended = True
            elif overall_percentage >= 60:
                match_quality = 'good'
                is_recommended = True
            elif overall_percentage >= 40:
                match_quality = 'fair'
                is_recommended = False
            else:
                match_quality = 'poor'
                is_recommended = False
            
            return {
                'overall_match_percentage': round(overall_percentage, 2),
                'skills_match_percentage': skills_analysis['percentage'],
                'experience_match_percentage': exp_analysis['percentage'],
                'qualification_match_percentage': qual_percentage,
                'location_match_percentage': loc_analysis['percentage'],
                'sentiment_score': resume.sentiment_score,
                'sentiment_impact': sentiment_analysis['impact'],
                'matching_skills': skills_analysis['matching_skills'],
                'missing_skills': skills_analysis['missing_skills'],
                'additional_skills': skills_analysis['additional_skills'],
                'success_reasons': success_reasons,
                'failure_reasons': failure_reasons,
                'improvement_suggestions': improvement_suggestions,
                'match_quality': match_quality,
                'is_recommended': is_recommended,
                'detailed_analysis': {
                    'skills': skills_analysis,
                    'experience': exp_analysis,
                    'location': loc_analysis,
                    'sentiment': sentiment_analysis,
                    'weights': {
                        'skills': '40%',
                        'experience': '30%',
                        'location': '15%',
                        'qualification': '10%',
                        'sentiment': '5%'
                    }
                }
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'overall_match_percentage': 0.0
            }
    
    @classmethod
    def match_resume_to_job(cls, job_id: int, resume_id: int, user=None) -> ApiResponse:
        """
        Match a single resume to a job and save results
        
        Args:
            job_id: Job ID
            resume_id: ResumeProcessing ID
            user: User initiating the match (optional)
            
        Returns:
            ApiResponse with match result
        """
        try:
            # Get job and resume
            job = Job.objects.select_related(
                'job_category', 'job_type', 'experience_required', 'state_city'
            ).get(id=job_id)
            
            resume = ResumeProcessing.objects.select_related('user').get(id=resume_id)
            
            # Check if match already exists
            existing_match = ResumeJobMatch.objects.filter(job=job, resume=resume).first()
            
            if existing_match:
                # Update existing match
                match_obj = existing_match
                match_obj.status = 'processing'
                match_obj.processing_started_at = timezone.now()
            else:
                # Create new match
                match_obj = ResumeJobMatch(
                    job=job,
                    resume=resume,
                    matched_by=user,
                    status='processing',
                    processing_started_at=timezone.now()
                )
            
            match_obj.save()
            
            # Calculate match
            match_data = cls.calculate_overall_match(job, resume)
            
            if 'error' in match_data:
                match_obj.status = 'failed'
                match_obj.error_message = match_data['error']
                match_obj.save()
                return ApiResponse.error(f"Matching failed: {match_data['error']}")
            
            # Update match object with results
            match_obj.overall_match_percentage = Decimal(str(match_data['overall_match_percentage']))
            match_obj.skills_match_percentage = Decimal(str(match_data['skills_match_percentage']))
            match_obj.experience_match_percentage = Decimal(str(match_data['experience_match_percentage']))
            match_obj.qualification_match_percentage = Decimal(str(match_data['qualification_match_percentage']))
            match_obj.location_match_percentage = Decimal(str(match_data['location_match_percentage']))
            match_obj.sentiment_score = match_data['sentiment_score']
            match_obj.sentiment_impact = match_data['sentiment_impact']
            match_obj.matching_skills = match_data['matching_skills']
            match_obj.missing_skills = match_data['missing_skills']
            match_obj.additional_skills = match_data['additional_skills']
            match_obj.success_reasons = match_data['success_reasons']
            match_obj.failure_reasons = match_data['failure_reasons']
            match_obj.improvement_suggestions = match_data['improvement_suggestions']
            match_obj.match_quality = match_data['match_quality']
            match_obj.is_recommended = match_data['is_recommended']
            match_obj.detailed_analysis = match_data['detailed_analysis']
            match_obj.status = 'completed'
            match_obj.processing_completed_at = timezone.now()
            match_obj.save()
            
            return ApiResponse.success(
                data={
                    'match_id': match_obj.id,
                    'job_title': job.title,
                    'resume_user': resume.user.username,
                    'overall_match': float(match_obj.overall_match_percentage),
                    'match_quality': match_obj.match_quality,
                    'is_recommended': match_obj.is_recommended,
                    'success_reasons': match_obj.success_reasons,
                    'failure_reasons': match_obj.failure_reasons
                },
                message=f"Match completed: {match_obj.overall_match_percentage}% compatibility"
            )
        
        except Job.DoesNotExist:
            return ApiResponse.not_found(f"Job with ID {job_id} not found")
        except ResumeProcessing.DoesNotExist:
            return ApiResponse.not_found(f"Resume with ID {resume_id} not found")
        except Exception as e:
            return ApiResponse.server_error(f"Error in matching process: {str(e)}")
    
    @classmethod
    def match_resume_to_all_jobs(cls, resume_id: int, user=None, filters: Dict = None,resume_record: Optional[ResumeProcessing] = None) -> ApiResponse:
        """
        Match a resume to all active jobs (or filtered jobs)
        
        Args:
            resume_id: ResumeProcessing ID
            user: User initiating the matches
            filters: Optional filters for jobs (category, type, etc.)
            
        Returns:
            ApiResponse with list of matches
        """
        try:
           # resume = ResumeProcessing.objects.get(id=resume_id)
            
            # Get jobs
            jobs_query = Job.objects.filter(is_active=True)
            
            if filters:
                if filters.get('job_category'):
                    jobs_query = jobs_query.filter(job_category_id=filters['job_category'])
                if filters.get('job_type'):
                    jobs_query = jobs_query.filter(job_type_id=filters['job_type'])
            
            jobs = jobs_query.select_related('job_category', 'job_type', 'experience_required')

            results = []
            match_result = cls.match_resume_to_job(resume_record.job_id, resume_id, user)
            if match_result.success:
                    results.append(match_result.data)
            
            # results = []
            # for job in jobs:
            #     match_result = cls.match_resume_to_job(job.id, resume_id, user)
            #     if match_result.success:
            #         results.append(match_result.data)
            
            return ApiResponse.success(
                data={
                    'resume_id': resume_id,
                    'total_jobs_matched': len(results),
                    'matches': results
                },
                message=f"Successfully matched resume to {len(results)} jobs"
            )
        
        except ResumeProcessing.DoesNotExist:
            return ApiResponse.not_found(f"Resume with ID {resume_id} not found")
        except Exception as e:
            return ApiResponse.server_error(f"Error matching to all jobs: {str(e)}")
    
    @classmethod
    def get_top_matches_for_job(cls, job_id: int, limit: int = 10) -> ApiResponse:
        """
        Get top matching resumes for a specific job
        
        Args:
            job_id: Job ID
            limit: Maximum number of results
            
        Returns:
            ApiResponse with top matches
        """
        try:
            job = Job.objects.get(id=job_id)
            
            matches = ResumeJobMatch.objects.filter(
                job=job,
                status='completed'
            ).select_related('resume__user').order_by('-overall_match_percentage')[:limit]
            
            results = []
            for match in matches:
                resume = match.resume
                resume_json = getattr(resume, 'resume_json', None)
                contact_info = None
                if resume_json and isinstance(resume_json, dict):
                    contact_info = resume_json.get('contact_info', None)
                results.append({
                    'match_id': match.id,
                    'resume_id': resume.id,
                    'candidate_name':contact_info['name'] if contact_info else None,# contact_info.name,#resume.user.get_full_name() or resume.user.username,
                    'overall_match': float(match.overall_match_percentage),
                    'match_quality': match.match_quality,
                    'is_recommended': match.is_recommended,
                    'skills_match': float(match.skills_match_percentage),
                    'experience_match': float(match.experience_match_percentage),
                    'matching_skills': match.matching_skills,
                    'success_reasons': match.success_reasons,
                    'created_at': match.created_at.isoformat(),
                    'extracted_phone': getattr(resume, 'extracted_phone', None),
                    'resume_json': resume_json,
                    'extracted_email': getattr(resume, 'extracted_email', None),
                    'phones': contact_info['phones'] if contact_info else None,
                    'emails': contact_info['emails'] if contact_info else None,

                })
            
            return ApiResponse.success(
                data={
                    'job_id': job_id,
                    'job_title': job.title,
                    'total_matches': len(results),
                    'top_matches': results
                },
                message=f"Found {len(results)} matches for {job.title}"
            )
        
        except Job.DoesNotExist:
            return ApiResponse.not_found(f"Job with ID {job_id} not found")
        except Exception as e:
            return ApiResponse.server_error(f"Error getting top matches: {str(e)}")
    
    @classmethod
    def get_top_jobs_for_resume(cls, resume_id: int, limit: int = 10) -> ApiResponse:
        """
        Get top matching jobs for a specific resume
        
        Args:
            resume_id: ResumeProcessing ID
            limit: Maximum number of results
            
        Returns:
            ApiResponse with top job matches
        """
        try:
            resume = ResumeProcessing.objects.get(id=resume_id)
            
            matches = ResumeJobMatch.objects.filter(
                resume=resume,
                status='completed'
            ).select_related('job__job_category', 'job__job_type').order_by('-overall_match_percentage')[:limit]
            
            results = []
            for match in matches:
                results.append({
                    'match_id': match.id,
                    'job_id': match.job.id,
                    'job_title': match.job.title,
                    'job_category': match.job.job_category.value if match.job.job_category else None,
                    'job_type': match.job.job_type.value if match.job.job_type else None,
                    'overall_match': float(match.overall_match_percentage),
                    'match_quality': match.match_quality,
                    'is_recommended': match.is_recommended,
                    'skills_match': float(match.skills_match_percentage),
                    'experience_match': float(match.experience_match_percentage),
                    'success_reasons': match.success_reasons,
                    'failure_reasons': match.failure_reasons,
                    'improvement_suggestions': match.improvement_suggestions,
                    'created_at': match.created_at.isoformat()
                })
            
            return ApiResponse.success(
                data={
                    'resume_id': resume_id,
                    'candidate_name': resume.user.get_full_name() or resume.user.username,
                    'total_matches': len(results),
                    'top_jobs': results
                },
                message=f"Found {len(results)} job matches for resume"
            )
        
        except ResumeProcessing.DoesNotExist:
            return ApiResponse.not_found(f"Resume with ID {resume_id} not found")
        except Exception as e:
            return ApiResponse.server_error(f"Error getting top jobs: {str(e)}")
