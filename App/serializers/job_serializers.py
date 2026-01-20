"""
REST API Serializers for Job Management
For use with Django REST Framework
Utilizes the service layer for all business logic

Author: JobStock Development Team
Date: December 22, 2025
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from App.models import Job, DropdownMaster
from App.models_extended import JobApplication, SavedJob


class DropdownSerializer(serializers.ModelSerializer):
    """Serializer for dropdown options"""
    class Meta:
        model = DropdownMaster
        fields = ['id', 'text', 'value']


class JobListSerializer(serializers.ModelSerializer):
    """Serializer for job list view"""
    job_category = DropdownSerializer(read_only=True)
    job_type = DropdownSerializer(read_only=True)
    location = serializers.SerializerMethodField()
    salary_range = serializers.SerializerMethodField()
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'company_logo',
            'job_category', 'job_type', 'location', 'salary_range',
            'deadline', 'posted_by_name', 'is_active', 'created_at'
        ]
    
    def get_location(self, obj):
        if obj.state_city:
            return obj.state_city.text
        return obj.permanent_address or obj.temporary_address
    
    def get_salary_range(self, obj):
        if obj.min_salary and obj.max_salary:
            return f"${obj.min_salary:,.0f} - ${obj.max_salary:,.0f}"
        elif obj.min_salary:
            return f"From ${obj.min_salary:,.0f}"
        elif obj.max_salary:
            return f"Up to ${obj.max_salary:,.0f}"
        return "Not specified"


class JobDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed job view"""
    job_category = DropdownSerializer(read_only=True)
    job_type = DropdownSerializer(read_only=True)
    job_level = DropdownSerializer(read_only=True)
    experience_required = DropdownSerializer(read_only=True)
    qualification_required = DropdownSerializer(read_only=True)
    gender_preference = DropdownSerializer(read_only=True)
    total_openings = DropdownSerializer(read_only=True)
    country = DropdownSerializer(read_only=True)
    state_city = DropdownSerializer(read_only=True)
    posted_by_info = serializers.SerializerMethodField()
    skills_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = '__all__'
    
    def get_posted_by_info(self, obj):
        if obj.posted_by:
            return {
                'id': obj.posted_by.id,
                'username': obj.posted_by.username,
                'full_name': obj.posted_by.get_full_name(),
                'email': obj.posted_by.email
            }
        return None
    
    def get_skills_list(self, obj):
        if obj.skills:
            return [skill.strip() for skill in obj.skills.split(',')]
        return []


class JobCreateUpdateSerializer(serializers.Serializer):
    """Serializer for creating/updating jobs with all DropdownMaster fields as string (value)."""
    title = serializers.CharField(max_length=255)
    company_logo = serializers.ImageField(required=False, allow_null=True)
    job_summary = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    responsibilities = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    qualifications = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    job_category = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    job_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    job_level = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    experience_required = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    qualification_required = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gender_preference = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    min_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    max_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    deadline = serializers.DateField(required=False, allow_null=True)
    total_openings = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    job_fee_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    skills = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    permanent_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    temporary_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    state_city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    zip_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    video_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)
    publish_to_boards = serializers.MultipleChoiceField(
        choices=['indeed', 'ziprecruiter', 'linkedin', 'jobelephant'],
        required=False,
        write_only=True
    )
    job_id = serializers.IntegerField(required=False)

    def validate_deadline(self, value):
        from django.utils import timezone
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Deadline must be in the future")
        return value

    def validate(self, data):
        min_sal = data.get('min_salary')
        max_sal = data.get('max_salary')
        if min_sal and max_sal and min_sal > max_sal:
            raise serializers.ValidationError({
                'min_salary': "Minimum salary cannot be greater than maximum salary"
            })
        return data


class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for job applications"""
    job_title = serializers.CharField(source='job.title', read_only=True)
    resume_url = serializers.SerializerMethodField()
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'job_title', 'applicant_name', 'applicant_email',
            'applicant_phone', 'cover_letter', 'resume_url', 'status',
            'source', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'status': {'required': False},
            'source': {'required': False}
        }
    
    def get_resume_url(self, obj):
        if hasattr(obj, 'resume') and obj.resume:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.resume.url)
            return obj.resume.url
        return None


class JobApplicationCreateSerializer(serializers.Serializer):
    """Serializer for submitting job applications"""
    job_id = serializers.IntegerField()
    applicant_name = serializers.CharField(max_length=255)
    applicant_email = serializers.EmailField()
    applicant_phone = serializers.CharField(max_length=20, required=False)
    cover_letter = serializers.CharField(required=False, allow_blank=True)
    resume = serializers.FileField()
    
    def validate_resume(self, value):
        """Validate resume file"""
        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Resume file size cannot exceed 5MB")
        
        # Check file type
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        return value


class JobSearchSerializer(serializers.Serializer):
    """Serializer for job search parameters"""
    q = serializers.CharField(required=False, help_text="Search query")
    job_category = serializers.IntegerField(required=False)
    job_type = serializers.CharField(required=False)
    job_level = serializers.CharField(required=False)
    min_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    location = serializers.CharField(required=False)
    experience = serializers.CharField(required=False)
    posted_within_days = serializers.IntegerField(required=False, min_value=1)
    has_active_deadline = serializers.BooleanField(required=False)
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    per_page = serializers.IntegerField(required=False, default=20, min_value=1, max_value=100)
    order_by = serializers.ChoiceField(
        choices=['-created_at', 'created_at', 'title', '-title', 'deadline'],
        required=False,
        default='-created_at'
    )


class JobBoardPublishSerializer(serializers.Serializer):
    """Serializer for publishing jobs to external boards"""
    job_id = serializers.IntegerField()
    boards = serializers.MultipleChoiceField(
        choices=['indeed', 'ziprecruiter', 'linkedin', 'jobelephant']
    )


class ApplicationStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating application status"""
    status = serializers.ChoiceField(
        choices=['pending', 'reviewed', 'shortlisted', 'rejected', 'accepted']
    )
    notes = serializers.CharField(required=False, allow_blank=True)


class BulkApplicationStatusSerializer(serializers.Serializer):
    """Serializer for bulk status update"""
    application_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    status = serializers.ChoiceField(
        choices=['pending', 'reviewed', 'shortlisted', 'rejected', 'accepted']
    )
