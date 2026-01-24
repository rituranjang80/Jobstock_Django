"""
Django Forms for Job Management (MVT - Template-based views)
Uses the service layer for all business logic

Author: Reetch Development Team
Date: December 22, 2025
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from App.models import Job, DropdownMaster
from App.models_extended import JobApplication


class JobPostForm(forms.ModelForm):
    """
    Form for creating/editing job posts
    Used in Django template-based views
    """
    # Job board selection
    publish_to_indeed = forms.BooleanField(required=False, label="Publish to Indeed")
    publish_to_ziprecruiter = forms.BooleanField(required=False, label="Publish to ZipRecruiter")
    publish_to_linkedin = forms.BooleanField(required=False, label="Publish to LinkedIn")
    publish_to_jobelephant = forms.BooleanField(required=False, label="Publish to JobElephant")
    
    class Meta:
        model = Job
        fields = [
            'title', 'company_logo', 'job_summary', 'responsibilities', 'qualifications',
            'job_category', 'job_type', 'job_level', 'experience_required',
            'qualification_required', 'gender_preference', 'min_salary', 'max_salary',
            'start_date', 'deadline', 'total_openings', 'job_fee_type', 'skills',
            'permanent_address', 'temporary_address', 'country', 'state_city',
            'zip_code', 'video_url', 'latitude', 'longitude', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Python Developer'
            }),
            'job_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Brief summary of the job position...'
            }),
            'responsibilities': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'List the key responsibilities...'
            }),
            'qualifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Required qualifications and skills...'
            }),
            'job_category': forms.Select(attrs={'class': 'form-control'}),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'job_level': forms.Select(attrs={'class': 'form-control'}),
            'experience_required': forms.Select(attrs={'class': 'form-control'}),
            'qualification_required': forms.Select(attrs={'class': 'form-control'}),
            'gender_preference': forms.Select(attrs={'class': 'form-control'}),
            'min_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '50000'
            }),
            'max_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '80000'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'total_openings': forms.Select(attrs={'class': 'form-control'}),
            'job_fee_type': forms.Select(attrs={'class': 'form-control'}),
            'skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Python, Django, PostgreSQL, Git'
            }),
            'permanent_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123 Main St, Suite 100'
            }),
            'temporary_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional temporary address'
            }),
            'country': forms.Select(attrs={'class': 'form-control'}),
            'state_city': forms.Select(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/...'
            }),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set queryset for dropdown fields
        self.fields['job_category'].queryset = DropdownMaster.objects.filter(
            group__value='job_category', is_active=True
        )
        self.fields['job_type'].queryset = DropdownMaster.objects.filter(
            group__value='job_type', is_active=True
        )
        self.fields['job_level'].queryset = DropdownMaster.objects.filter(
            group__value='job_level', is_active=True
        )
        self.fields['experience_required'].queryset = DropdownMaster.objects.filter(
            group__value='experience', is_active=True
        )
        self.fields['qualification_required'].queryset = DropdownMaster.objects.filter(
            group__value='qualification', is_active=True
        )
        self.fields['gender_preference'].queryset = DropdownMaster.objects.filter(
            group__value='gender', is_active=True
        )
        self.fields['total_openings'].queryset = DropdownMaster.objects.filter(
            group__value='total_openings', is_active=True
        )
        self.fields['job_fee_type'].queryset = DropdownMaster.objects.filter(
            group__value='job_fee_type', is_active=True
        )
        self.fields['country'].queryset = DropdownMaster.objects.filter(
            group__value='country', is_active=True
        )
        self.fields['state_city'].queryset = DropdownMaster.objects.filter(
            group__value='state_city', is_active=True
        )
        
        # Make some fields optional
        self.fields['company_logo'].required = False
        self.fields['job_summary'].required = False
        self.fields['responsibilities'].required = False
        self.fields['qualifications'].required = False
    
    def clean_deadline(self):
        """Validate deadline is in the future"""
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now().date():
            raise ValidationError("Deadline must be in the future")
        return deadline
    
    def clean(self):
        """Validate salary range"""
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('min_salary')
        max_salary = cleaned_data.get('max_salary')
        
        if min_salary and max_salary and min_salary > max_salary:
            raise ValidationError({
                'min_salary': "Minimum salary cannot be greater than maximum salary"
            })
        
        return cleaned_data
    
    def get_selected_boards(self):
        """Get list of selected job boards"""
        boards = []
        if self.cleaned_data.get('publish_to_indeed'):
            boards.append('indeed')
        if self.cleaned_data.get('publish_to_ziprecruiter'):
            boards.append('ziprecruiter')
        if self.cleaned_data.get('publish_to_linkedin'):
            boards.append('linkedin')
        if self.cleaned_data.get('publish_to_jobelephant'):
            boards.append('jobelephant')
        return boards


class JobSearchForm(forms.Form):
    """Form for job search"""
    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job title, keywords, or company...'
        })
    )
    job_category = forms.ModelChoiceField(
        queryset=DropdownMaster.objects.filter(group__value='job_category', is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    job_type = forms.ModelChoiceField(
        queryset=DropdownMaster.objects.filter(group__value='job_type', is_active=True),
        required=False,
        empty_label="All Types",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    job_level = forms.ModelChoiceField(
        queryset=DropdownMaster.objects.filter(group__value='job_level', is_active=True),
        required=False,
        empty_label="All Levels",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    location = forms.CharField(
        required=False,
        label='Location',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City or State'
        })
    )
    min_salary = forms.DecimalField(
        required=False,
        label='Min Salary',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0'
        })
    )
    max_salary = forms.DecimalField(
        required=False,
        label='Max Salary',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '200000'
        })
    )
    posted_within_days = forms.ChoiceField(
        required=False,
        label='Posted Within',
        choices=[
            ('', 'Any time'),
            ('1', 'Last 24 hours'),
            ('7', 'Last week'),
            ('30', 'Last month'),
            ('90', 'Last 3 months'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class JobApplicationForm(forms.Form):
    """Form for job application submission"""
    applicant_name = forms.CharField(
        max_length=255,
        label='Full Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John Doe'
        })
    )
    applicant_email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'john@example.com'
        })
    )
    applicant_phone = forms.CharField(
        max_length=20,
        required=False,
        label='Phone Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '555-1234'
        })
    )
    cover_letter = forms.CharField(
        required=False,
        label='Cover Letter',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Tell us why you are a great fit for this position...'
        })
    )
    resume = forms.FileField(
        label='Resume/CV',
        help_text='Accepted formats: PDF, DOC, DOCX, TXT (Max 5MB)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.txt'
        })
    )
    
    def clean_resume(self):
        """Validate resume file"""
        resume = self.cleaned_data.get('resume')
        
        if resume:
            # Check file size (max 5MB)
            if resume.size > 5 * 1024 * 1024:
                raise ValidationError("Resume file size cannot exceed 5MB")
            
            # Check file type
            import os
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
            ext = os.path.splitext(resume.name)[1].lower()
            if ext not in allowed_extensions:
                raise ValidationError(
                    f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
                )
        
        return resume


class ApplicationStatusForm(forms.Form):
    """Form for updating application status"""
    status = forms.ChoiceField(
        choices=[
            ('pending', 'Pending'),
            ('reviewed', 'Reviewed'),
            ('shortlisted', 'Shortlisted'),
            ('rejected', 'Rejected'),
            ('accepted', 'Accepted'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add notes about this decision...'
        })
    )
