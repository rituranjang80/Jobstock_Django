from App.models_navigation_ui import NavigationUiGroup, NavigationUiItem
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Insert initial navigation UI data for hiring_manager'

    def handle(self, *args, **options):
        group, created = NavigationUiGroup.objects.get_or_create(
            slug='hiring-manager-main-menu',
            defaults={
                'name': 'Hiring Manager Main Menu',
                'icon': 'fa-bars',
                'order': 1,
                'visible_to_roles': ['hiring_manager'],
                'is_active': True
            }
        )
        items_data = [
            {"title": "User Dashboard", "url_name": "employer-dashboard", "icon": "fa-solid fa-gauge-high me-2"},
            {"title": "User Profile", "url_name": "employer-profile", "icon": "fa-regular fa-user me-2"},
            {"title": "My Jobs", "url_name": "employer-jobs", "icon": "fa-solid fa-business-time me-2"},
            {"title": "Submit Jobs", "url_name": "employer-submit-job", "icon": "fa-solid fa-pen-ruler me-2"},
            {"title": "Applicants Jobs", "url_name": "employer-applicants-jobs", "icon": "fa-solid fa-user-group me-2"},
            {"title": "Shortlisted Candidates", "url_name": "employer-shortlist-candidates", "icon": "fa-solid fa-user-clock me-2"},
            {"title": "Package", "url_name": "employer-package", "icon": "fa-solid fa-wallet me-2"},
            {"title": "Messages", "url_name": "employer-messages", "icon": "fa-solid fa-comments me-2"},
            {"title": "Change Password", "url_name": "employer-change-password", "icon": "fa-solid fa-unlock-keyhole me-2"},
            {"title": "Delete Account", "url_name": "employer-delete-account", "icon": "fa-solid fa-trash-can me-2"},
            {"title": "Log Out", "url_name": "logout", "icon": "fa-solid fa-power-off me-2"}
        ]
        for idx, item in enumerate(items_data, start=1):
            NavigationUiItem.objects.get_or_create(
                group=group,
                title=item["title"],
                url_name=item["url_name"],
                icon=item["icon"],
                order=idx,
                visible_to_roles=["hiring_manager"],
                is_active=True
            )
        self.stdout.write(self.style.SUCCESS('Navigation UI data inserted.'))
