import json
import os
from django.conf import settings

CONFIG_PATH = os.path.join(settings.BASE_DIR, 'confg', 'Searchconfig.json')

def get_search_fields(function_name):
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get(function_name, [])
    except Exception as e:
        raise RuntimeError(f"Error loading search configuration: {e}")
