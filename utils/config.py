import json
import os

CONFIG_DIR = 'config'
SITES_DATA_FILE = os.path.join(CONFIG_DIR, 'sites_data.json')
# Store global AI provider and API key
AI_CONFIG_FILE = os.path.join(CONFIG_DIR, 'ai_config.json')
AI_CONFIG_EXAMPLE_FILE = os.path.join(CONFIG_DIR, 'ai_config.example.json')

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

def _initialize_ai_config():
    """Create ``AI_CONFIG_FILE`` using the example file if available."""
    if os.path.exists(AI_CONFIG_EXAMPLE_FILE):
        try:
            with open(AI_CONFIG_EXAMPLE_FILE, "r") as src:
                data = json.load(src)
        except Exception:
            data = {"providers": {}}
    else:
        data = {"providers": {}}

    with open(AI_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)
    return data


def load_ai_config():
    """Load global AI provider configuration with safe fallback."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if not os.path.exists(AI_CONFIG_FILE):
        return _initialize_ai_config()

    try:
        with open(AI_CONFIG_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                raise json.JSONDecodeError("Empty file", "", 0)
            return json.loads(content)
    except json.JSONDecodeError:
        # Corrupted or empty file — reset to defaults
        return _initialize_ai_config()

def save_ai_config(data):
    """Persist global AI provider configuration."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    with open(AI_CONFIG_FILE, 'w') as f:
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
