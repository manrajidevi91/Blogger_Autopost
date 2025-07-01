import json
import os

CONFIG_DIR = 'config'
SITES_DATA_FILE = os.path.join(CONFIG_DIR, 'sites_data.json')
MODEL_CONFIG_FILE = os.path.join(CONFIG_DIR, 'model_config.json')

def load_sites_data():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(SITES_DATA_FILE):
        with open(SITES_DATA_FILE, 'w') as f:
            json.dump({}, f)
    with open(SITES_DATA_FILE, 'r') as f:
        return json.load(f)

def save_sites_data(data):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    with open(SITES_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_model_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(MODEL_CONFIG_FILE):
        with open(MODEL_CONFIG_FILE, 'w') as f:
            json.dump({}, f)
    with open(MODEL_CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_model_config(data):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    with open(MODEL_CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def get_credentials_dir(site_name):
    """Return directory path for credentials for a given site."""
    return os.path.join(CONFIG_DIR, site_name)


def save_client_secret(site_name, file_obj):
    """Save uploaded client secret file for ``site_name`` and return its path."""
    cred_dir = get_credentials_dir(site_name)
    os.makedirs(cred_dir, exist_ok=True)
    cred_path = os.path.join(cred_dir, "client_secret.json")
    file_obj.save(cred_path)
    return cred_path
