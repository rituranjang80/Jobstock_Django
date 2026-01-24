import django
import os
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jobstock.settings')
django.setup()

from App.models import DropdownMaster, DropdownGroup

# Map POST data keys to (value, group__value)
POST_DATA = {
    'job_category': ('ui_ux_design', 'job_category'),
    'job_type': ('part_time', 'job_type'),
    'job_level': ('lead', 'job_level'),
    'experience_required': ('2plus_years', 'experience'),
    'qualification_required': ('12th_class', 'qualification'),
    'gender_preference': ('female', 'gender'),
    'total_openings': ('04', 'total_openings'),
    'job_fee_type': ('premium', 'job_fee_type'),
    'country': ('australia', 'country'),
    'state_city': ('United State', 'state_city'),
}

def ensure_dropdown_entry(value, group_value):
    group, _ = DropdownGroup.objects.get_or_create(value=group_value, defaults={'label': group_value.replace('_', ' ').title()})
    obj, created = DropdownMaster.objects.get_or_create(value=value, group=group, defaults={'label': value.replace('_', ' ').title()})
    if created:
        print(f"Created: {group_value} -> {value}")
    else:
        print(f"Exists: {group_value} -> {value}")

if __name__ == "__main__":
    for key, (value, group_value) in POST_DATA.items():
        ensure_dropdown_entry(value, group_value)
    print("DropdownMaster check/creation complete.")
