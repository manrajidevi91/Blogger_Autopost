import os
from utils.config import load_sites_data

STATIC_TEMPLATES_DIR = 'static/templates'

def get_site_by_name(site_name):
    sites = load_sites_data()
    return sites.get(site_name)

def list_site_templates(site_name):
    site_template_path = os.path.join(STATIC_TEMPLATES_DIR, site_name)
    if os.path.exists(site_template_path):
        return [f for f in os.listdir(site_template_path) if f.endswith('.html')]
    return []
