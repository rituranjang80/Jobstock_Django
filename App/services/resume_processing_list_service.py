from App.repositories.resume_processing_repository import ResumeProcessingRepository
from typing import Dict, Any

class ResumeProcessingListService:
    @staticmethod
    def get_resume_list(user, is_rpo_admin, filters: Dict[str, Any], sort: str, offset: int, limit: int):
        job_id = filters.get('job_id')
        resumesource_ids = filters.get('resumesource')
        status_list = filters.get('status')
        qs = ResumeProcessingRepository.filter_resumes(user, is_rpo_admin, job_id, resumesource_ids, status_list, sort)
        total = qs.count()
        resumes = qs[offset:offset+limit]
        return resumes, total
