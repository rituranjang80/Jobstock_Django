# Job Management Service Layer - Complete Documentation

## Overview

This is a production-ready, enterprise-level service layer architecture for managing job postings and applications. The system integrates with major job boards (JobElephant, ZipRecruiter, Indeed, LinkedIn) and supports both Django Templates (MVT) and REST API.

**Database Table:** `app_job`

**Author:** Reetch Development Team  
**Date:** December 22, 2025

---

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  Django Views   │         │   REST API      │
│   (MVT/HTML)    │         │   (DRF/JSON)    │
└────────┬────────┘         └────────┬────────┘
         │                           │
         └──────────┬────────────────┘
                    │
         ┌──────────▼──────────┐
         │   SERVICE LAYER     │
         │  (Business Logic)   │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │   DATABASE (ORM)    │
         │   app_job table     │
         └─────────────────────┘
```

### Key Principles

1. **Service Layer Pattern**: All business logic resides in services
2. **Thin Controllers**: Views/API endpoints are lightweight
3. **Reusability**: Services work with both MVT and REST API
4. **Separation of Concerns**: Clear boundaries between layers
5. **Single Responsibility**: Each service has a focused purpose

---

## File Structure

```
App/
├── services/
│   ├── base_generic_service.py          # Generic CRUD operations
│   ├── enhanced_job_service.py          # Job management
│   ├── job_board_integration_service.py # External job boards
│   └── job_application_service.py       # Application handling
├── serializers/
│   └── job_serializers.py               # REST API serializers
├── forms/
│   └── job_forms.py                     # Django forms
└── views/
    ├── job_mvt_views.py                 # Template-based views
    └── job_api_views.py                 # REST API views
```

---

## Services Documentation

### 1. Base Generic Service (`base_generic_service.py`)

Generic CRUD operations that can be used with any Django model.

#### Key Features
- Create, Read, Update, Delete operations
- Pagination support
- Search and filtering
- Bulk operations
- Standardized response format

#### Usage Example

```python
from App.services.base_generic_service import GenericService
from App.models import YourModel

# Instantiate service
service = GenericService(YourModel)

# Create a record
result = service.create({'title': 'Example', 'description': 'Test'})

# Get all records with pagination
result = service.get_paginated(page=1, per_page=20, filters={'is_active': True})

# Update a record
result = service.update(pk=1, data={'title': 'Updated'})

# Delete a record
result = service.delete(pk=1, soft_delete=True)
```

#### Response Format

All service methods return a standardized response:

```python
{
    'success': True/False,
    'message': 'Operation message',
    'data': {...},  # Actual data
    'error': None or error details,
    'timestamp': '2025-12-22T10:00:00Z'
}
```

---

### 2. Enhanced Job Service (`enhanced_job_service.py`)

Complete job posting management with external job board integration.

#### Key Methods

##### Create Job Post
```python
from App.services.enhanced_job_service import job_service

result = job_service.create_job_post(
    data={
        'title': 'Senior Python Developer',
        'job_summary': 'Looking for experienced Python developer...',
        'min_salary': 80000,
        'max_salary': 120000,
        'job_category_id': 1,
        'job_type_id': 2,
        'skills': 'Python, Django, PostgreSQL',
        'deadline': '2025-12-31'
    },
    user=request.user,
    publish_to_boards=['indeed', 'linkedin']  # Optional
)

if result['success']:
    job_data = result['data']['job']
    publications = result['data']['publications']
```

##### Search Jobs (Like Indeed/ZipRecruiter)
```python
result = job_service.search_jobs(
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

jobs = result['data']  # List of jobs
pagination = result['pagination']
```

##### Get Job Details
```python
result = job_service.get_job_details(job_id=123)

if result['success']:
    job = result['data']
    print(f"Title: {job['title']}")
    print(f"Applications: {job['stats']['applications']}")
```

##### Get My Posted Jobs (Employer Dashboard)
```python
result = job_service.get_my_posted_jobs(
    user=request.user,
    filters={'status': 'active'},
    page=1,
    per_page=10
)

jobs = result['data']
summary = result['summary']  # {'total_jobs': 50, 'active_jobs': 35, ...}
```

##### Update Job
```python
result = job_service.update_job_post(
    job_id=123,
    data={'title': 'Senior Python Developer (Updated)'},
    user=request.user,
    sync_to_boards=True  # Sync changes to external boards
)
```

##### Deactivate/Reactivate Job
```python
# Deactivate
result = job_service.deactivate_job(
    job_id=123,
    user=request.user,
    remove_from_boards=True
)

# Reactivate
result = job_service.reactivate_job(
    job_id=123,
    user=request.user,
    republish_to_boards=['indeed', 'ziprecruiter']
)
```

##### Get Job Analytics
```python
result = job_service.get_job_analytics(job_id=123, user=request.user)

if result['success']:
    analytics = result['data']
    print(f"Total Applications: {analytics['applications']['total']}")
    print(f"Applications per day: {analytics['engagement']['applications_per_day']}")
```

---

### 3. Job Board Integration Service (`job_board_integration_service.py`)

Handles posting jobs to and receiving applications from external job boards.

#### Supported Platforms
- **Indeed Employer**
- **ZipRecruiter**
- **LinkedIn Recruiter**
- **JobElephant**

#### Configuration

Add to your `settings.py`:

```python
# Job Board API Credentials
JOBBOARD_CREDENTIALS = {
    'indeed': {
        'api_key': 'your_indeed_api_key',
        'employer_id': 'your_employer_id'
    },
    'ziprecruiter': {
        'api_key': 'your_ziprecruiter_api_key',
        'account_id': 'your_account_id'
    },
    'linkedin': {
        'client_id': 'your_client_id',
        'client_secret': 'your_client_secret'
    },
    'jobelephant': {
        'api_key': 'your_jobelephant_api_key',
        'partner_id': 'your_partner_id'
    }
}

# Email for job applications
JOB_APPLICATION_EMAIL = 'jobs@yourcompany.com'
```

#### Usage

##### Publish to Single Board
```python
from App.services.job_board_integration_service import job_board_service

result = job_board_service.publish_job(
    job_id=123,
    board='indeed'
)
```

##### Publish to Multiple Boards
```python
result = job_board_service.publish_to_multiple_boards(
    job_id=123,
    boards=['indeed', 'ziprecruiter', 'linkedin']
)

# Check results
for board, pub_result in result['data']['results'].items():
    if pub_result['success']:
        print(f"✓ Published to {board}")
    else:
        print(f"✗ Failed to publish to {board}")
```

##### Sync Job Updates
```python
# After editing a job, sync changes to all boards
result = job_board_service.sync_job_updates(job_id=123)
```

##### Fetch Applications from External Boards
```python
# Fetch from all boards
result = job_board_service.fetch_applications(job_id=123)

# Fetch from specific board
result = job_board_service.fetch_applications(job_id=123, board='indeed')

applications = result['data']['applications']
for app in applications:
    print(f"Application from {app['source_board']}: {app['applicant_name']}")
```

---

### 4. Job Application Service (`job_application_service.py`)

Handles job applications from all sources.

#### Submit Application (Direct)
```python
from App.services.job_application_service import application_service

result = application_service.submit_application(
    job_id=123,
    applicant_data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '555-1234',
        'cover_letter': 'I am very interested in...'
    },
    resume_file=request.FILES['resume'],
    source='direct'
)
```

#### Receive External Application (from job boards)
```python
# This is typically called via webhook
result = application_service.receive_external_application(
    job_external_id='indeed_job_123',
    board='indeed',
    application_data={
        'candidate_name': 'John Doe',
        'candidate_email': 'john@example.com',
        'resume_url': 'https://indeed.com/resumes/123.pdf'
    }
)
```

#### Get Job Applications
```python
result = application_service.get_job_applications(
    job_id=123,
    user=request.user,
    filters={'status': 'pending'},
    page=1,
    per_page=20
)

applications = result['data']
stats = result['stats']  # Application statistics
```

#### Update Application Status
```python
result = application_service.update_application_status(
    application_id=456,
    status='shortlisted',
    user=request.user,
    notes='Strong candidate, schedule interview'
)
```

#### Bulk Status Update
```python
result = application_service.bulk_update_status(
    application_ids=[456, 457, 458],
    status='reviewed',
    user=request.user
)
```

---

## Using with Django Templates (MVT)

### URL Configuration

Add to `urls.py`:

```python
from django.urls import path
from App.views.job_mvt_views import *

urlpatterns = [
    # Public job pages
    path('jobs/', job_list_view, name='job_list'),
    path('jobs/<int:job_id>/', job_detail_view, name='job_detail'),
    path('jobs/<int:job_id>/apply/', job_apply_view, name='job_apply'),
    
    # Employer dashboard
    path('employer/dashboard/', employer_dashboard_view, name='employer_dashboard'),
    path('employer/jobs/create/', job_post_create_view, name='job_create'),
    path('employer/jobs/<int:job_id>/edit/', job_post_edit_view, name='job_edit'),
    path('employer/jobs/<int:job_id>/deactivate/', job_deactivate_view, name='job_deactivate'),
    path('employer/jobs/<int:job_id>/reactivate/', job_reactivate_view, name='job_reactivate'),
    
    # Application management
    path('employer/jobs/<int:job_id>/applications/', job_applications_view, name='job_applications'),
    path('employer/applications/<int:application_id>/', application_detail_view, name='application_detail'),
    path('employer/applications/<int:application_id>/status/', application_update_status_view, name='update_application_status'),
    
    # AJAX endpoints
    path('ajax/jobs/<int:job_id>/analytics/', job_analytics_ajax, name='job_analytics_ajax'),
    path('ajax/applications/bulk-status/', bulk_application_status_ajax, name='bulk_application_status'),
]
```

### Template Example

**templates/jobs/job_list.html:**
```html
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <h1>Find Jobs</h1>
    
    <!-- Search Form -->
    <form method="get" action="{% url 'job_list' %}">
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">Search</button>
    </form>
    
    <!-- Results -->
    <div class="job-list">
        <p>Found {{ total_jobs }} jobs</p>
        
        {% for job in jobs %}
        <div class="job-card">
            <h3><a href="{% url 'job_detail' job.id %}">{{ job.title }}</a></h3>
            <p>{{ job.job_summary|truncatewords:30 }}</p>
            <div class="job-meta">
                <span>{{ job.location.city }}</span>
                <span>{{ job.salary.min }} - {{ job.salary.max }}</span>
                <span>{{ job.job_type.text }}</span>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <!-- Pagination -->
    {% if pagination.has_prev %}
        <a href="?page={{ pagination.page|add:-1 }}">Previous</a>
    {% endif %}
    
    Page {{ pagination.page }} of {{ pagination.total_pages }}
    
    {% if pagination.has_next %}
        <a href="?page={{ pagination.page|add:1 }}">Next</a>
    {% endif %}
</div>
{% endblock %}
```

---

## Using with REST API (DRF)

### URL Configuration

Add to `urls.py`:

```python
from django.urls import path
from App.views.job_api_views import *

urlpatterns = [
    # Job endpoints
    path('api/jobs/', job_list_api, name='api_job_list'),
    path('api/jobs/<int:job_id>/', job_detail_api, name='api_job_detail'),
    path('api/jobs/create/', job_create_api, name='api_job_create'),
    path('api/jobs/<int:job_id>/update/', job_update_api, name='api_job_update'),
    path('api/jobs/<int:job_id>/delete/', job_delete_api, name='api_job_delete'),
    path('api/jobs/my-jobs/', my_jobs_api, name='api_my_jobs'),
    path('api/jobs/<int:job_id>/analytics/', job_analytics_api, name='api_job_analytics'),
    
    # Job board integration
    path('api/jobs/publish-to-boards/', job_publish_to_boards_api, name='api_publish_to_boards'),
    path('api/jobs/<int:job_id>/sync-to-boards/', job_sync_to_boards_api, name='api_sync_to_boards'),
    path('api/jobs/<int:job_id>/fetch-external-applications/', job_fetch_external_applications_api, name='api_fetch_external_apps'),
    
    # Application endpoints
    path('api/jobs/apply/', job_apply_api, name='api_job_apply'),
    path('api/jobs/<int:job_id>/applications/', job_applications_api, name='api_job_applications'),
    path('api/applications/<int:application_id>/', application_detail_api, name='api_application_detail'),
    path('api/applications/<int:application_id>/status/', application_update_status_api, name='api_update_application_status'),
    path('api/applications/bulk-update-status/', applications_bulk_update_status_api, name='api_bulk_update_status'),
    
    # Webhooks
    path('api/webhooks/applications/<str:board>/', external_application_webhook, name='webhook_external_application'),
]
```

### API Examples

#### Search Jobs
```bash
GET /api/jobs/?q=python&job_type=full_time&location=New York&page=1&per_page=20

Response:
{
    "success": true,
    "data": [...],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 150,
        "total_pages": 8,
        "has_next": true,
        "has_prev": false
    }
}
```

#### Create Job
```bash
POST /api/jobs/create/
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "Senior Python Developer",
    "job_summary": "Looking for experienced developer",
    "min_salary": 80000,
    "max_salary": 120000,
    "job_category": 1,
    "job_type": 2,
    "skills": "Python, Django, PostgreSQL",
    "deadline": "2025-12-31",
    "publish_to_boards": ["indeed", "linkedin"]
}

Response:
{
    "success": true,
    "message": "Job created successfully",
    "data": {
        "job": {...},
        "publications": {
            "indeed": {"success": true, "external_job_id": "indeed_123"},
            "linkedin": {"success": true, "external_job_id": "linkedin_456"}
        }
    }
}
```

#### Submit Application
```bash
POST /api/jobs/apply/
Content-Type: multipart/form-data

job_id: 123
applicant_name: John Doe
applicant_email: john@example.com
applicant_phone: 555-1234
cover_letter: I am very interested...
resume: [file]

Response:
{
    "success": true,
    "message": "Application submitted successfully",
    "data": {
        "id": 789,
        "applicant_name": "John Doe",
        "status": "pending"
    }
}
```

---

## Complete Workflow Examples

### Example 1: Employer Posts a Job

```python
# In view or API endpoint
from App.services.enhanced_job_service import job_service

# Step 1: Create job post
result = job_service.create_job_post(
    data={
        'title': 'Senior DevOps Engineer',
        'job_summary': 'We are looking for...',
        'min_salary': 100000,
        'max_salary': 150000,
        'job_category_id': 5,
        'job_type_id': 1,  # Full-time
        'deadline': '2026-01-31'
    },
    user=request.user,
    publish_to_boards=['indeed', 'ziprecruiter', 'linkedin']
)

if result['success']:
    job_id = result['data']['job']['id']
    
    # Job is now:
    # 1. Saved in database
    # 2. Posted to Indeed, ZipRecruiter, LinkedIn
    # 3. Accessible on your website
```

### Example 2: Candidate Applies for Job

```python
from App.services.job_application_service import application_service

# Candidate fills out application form
result = application_service.submit_application(
    job_id=job_id,
    applicant_data={
        'name': 'Jane Smith',
        'email': 'jane@example.com',
        'phone': '555-9876',
        'cover_letter': 'I have 8 years of experience...'
    },
    resume_file=uploaded_file,
    source='direct'
)

# Application is now:
# 1. Saved in database
# 2. Employer notified
# 3. Visible in employer dashboard
```

### Example 3: Employer Reviews Applications

```python
from App.services.job_application_service import application_service

# Get all applications for a job
result = application_service.get_job_applications(
    job_id=job_id,
    user=request.user,
    page=1,
    per_page=20
)

applications = result['data']
stats = result['stats']

# Update status
application_service.update_application_status(
    application_id=applications[0]['id'],
    status='shortlisted',
    user=request.user,
    notes='Excellent experience, schedule interview'
)
```

---

## Testing

### Unit Tests Example

```python
from django.test import TestCase
from django.contrib.auth.models import User
from App.services.enhanced_job_service import job_service

class JobServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
    
    def test_create_job(self):
        result = job_service.create_job_post(
            data={'title': 'Test Job'},
            user=self.user
        )
        self.assertTrue(result['success'])
        self.assertIn('job', result['data'])
    
    def test_search_jobs(self):
        # Create test jobs
        job_service.create_job_post({'title': 'Python Developer'}, self.user)
        job_service.create_job_post({'title': 'Java Developer'}, self.user)
        
        # Search
        result = job_service.search_jobs(search_query='Python')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)
```

---

## Best Practices

### 1. Always Use Services
```python
# ❌ Don't access models directly in views
jobs = Job.objects.filter(is_active=True)

# ✅ Use services
result = job_service.search_jobs(filters={'is_active': True})
jobs = result['data']
```

### 2. Handle Service Responses
```python
result = job_service.create_job_post(data, user)

if result['success']:
    # Success handling
    job_id = result['data']['job']['id']
    messages.success(request, result['message'])
else:
    # Error handling
    messages.error(request, result['message'])
    errors = result.get('error')
```

### 3. Use Pagination
```python
# Always paginate large datasets
result = job_service.search_jobs(page=1, per_page=20)
```

### 4. Optimize Queries
```python
# Services automatically optimize with select_related/prefetch_related
# But you can customize if needed
job_service.SELECT_RELATED = ['job_category', 'job_type', 'posted_by']
```

---

## Troubleshooting

### Issue: Job board integration not working

**Solution:**
1. Check `settings.py` for correct API credentials
2. Check logs for API errors
3. In development, ensure `DEBUG = True` (simulates successful publication)

### Issue: Applications not being received from external boards

**Solution:**
1. Configure webhook URLs in job board dashboards
2. Implement `JobBoardMapping` model to track external IDs
3. Secure webhook endpoint with API key validation

### Issue: Slow performance with many jobs

**Solution:**
1. Services already use `select_related` for optimization
2. Add database indexes on frequently queried fields
3. Use caching for job listings
4. Consider implementing Elasticsearch for search

---

## Migration Guide

If you have existing code, migrate gradually:

```python
# Old code
jobs = Job.objects.filter(is_active=True).select_related('job_type')

# New code (same result, but through service)
result = job_service.get_all(filters={'is_active': True})
jobs_data = result['data']['items']
```

---

## Summary

This service layer provides:

✅ **Generic CRUD operations** - Reusable for any model  
✅ **Job management** - Complete lifecycle from post to archive  
✅ **External job boards** - Publish to Indeed, ZipRecruiter, LinkedIn, JobElephant  
✅ **Application handling** - Receive and manage applications from all sources  
✅ **MVT support** - Works with Django templates  
✅ **REST API support** - Works with Django REST Framework  
✅ **Standardized responses** - Consistent error handling  
✅ **Production-ready** - Logging, validation, transactions  

**Start using it today and build a world-class job board platform!** 🚀
