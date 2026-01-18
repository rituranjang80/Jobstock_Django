from App.models_navigation_ui import NavigationUiGroup, NavigationUiItem
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Insert initial navigation UI data for rpo_admin'

    def handle(self, *args, **options):
        group, created = NavigationUiGroup.objects.get_or_create(
            slug='rpo_admin',
            defaults={
                'name': 'candidate Management',
                'icon': 'fa-bars',
                'order': 1,
                'visible_to_roles': ['rpo_admin'],
                'is_active': True
            }
        )
       
        items_data = [
            {"title": "candidate dashboard", "url_name": "candidate-dashboard", "icon": "fa-solid fa-gauge-high me-2"},
            {"title": "candidate Profile", "url_name": "candidate-profile", "icon": "fa-regular fa-user me-2"},
            {"title": "candidate-resume", "url_name": "candidate-resume", "icon": "fa-solid fa-business-time me-2"},
            {"title": "candidate-saved-jobs", "url_name": "candidate-saved-jobs", "icon": "fa-solid fa-pen-ruler me-2"},
            {"title": "Messages", "url_name": "rpoadmin-messages", "icon": "fa-solid fa-comments me-2"},
            {"title": "Change Password", "url_name": "rpoadmin-change-password", "icon": "fa-solid fa-unlock-keyhole me-2"},
            {"title": "Delete Account", "url_name": "rpoadmin-delete-account", "icon": "fa-solid fa-trash-can me-2"},
            {"title": "Log Out", "url_name": "logout", "icon": "fa-solid fa-power-off me-2"}
        ]
        for idx, item in enumerate(items_data, start=1):
            NavigationUiItem.objects.get_or_create(
                group=group,
                title=item["title"],
                url_name=item["url_name"],
                icon=item["icon"],
                order=idx,
                visible_to_roles=["candidate"],
                is_active=True
            )
        self.stdout.write(self.style.SUCCESS('Navigation UI data inserted.'))
