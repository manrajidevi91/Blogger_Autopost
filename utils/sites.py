import os
from utils.config import load_sites_data

STATIC_TEMPLATES_DIR = 'static/templates'

def get_site_by_name(site_name):
    """Return site configuration for ``site_name`` if it exists."""
    sites = load_sites_data()
    return sites.get(site_name)

def list_site_templates(site_name):
    """Return HTML templates available for a site.

    Parameters
    ----------
    site_name : str
        Name of the site to look up templates for.

    Returns
    -------
    list[str]
        A list of template file names. If the directory does not exist or
        cannot be read, an empty list is returned.
    """
    site_template_path = os.path.join(STATIC_TEMPLATES_DIR, site_name)
    if os.path.exists(site_template_path):
        try:
            return [
                f
                for f in os.listdir(site_template_path)
                if f.endswith('.html')
            ]
        except OSError:
            return []
    return [] 