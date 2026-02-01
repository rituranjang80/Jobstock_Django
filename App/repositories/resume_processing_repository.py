from App.models import ResumeProcessing
from django.db.models import QuerySet
from typing import List, Optional

class ResumeProcessingRepository:
    @staticmethod
    def filter_resumes(
        user,
        is_rpo_admin: bool,
        job_id: Optional[int] = None,
        resumesource_ids: Optional[List[str]] = None,
        status_list: Optional[List[str]] = None,
        sort: str = '-id',
    ) -> QuerySet:
        qs = ResumeProcessing.objects.all()
        if not user.is_superuser:
            if is_rpo_admin:
                qs = qs.filter(user__groups__name='rpo_admin')
            else:
                qs = qs.filter(user=user)
        if job_id is not None:
            qs = qs.filter(job__id=job_id)
        if resumesource_ids:
            qs = qs.filter(resumesource__id__in=resumesource_ids)
        if status_list:
            qs = qs.filter(status__in=status_list)
        return qs.order_by(sort)
