from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle

# Step 1: Paths
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
TOKEN_PATH = os.path.join(CONFIG_DIR, 'token.pickle')
CLIENT_SECRET_PATH = os.path.join(CONFIG_DIR, 'client_secret.json')

# Step 2: Scope and blog config
SCOPES = ['https://www.googleapis.com/auth/blogger']
BLOG_ID = '5284815992985674732'

# Step 3: Load or get credentials
creds = None
if os.path.exists(TOKEN_PATH):
    with open(TOKEN_PATH, 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
    with open(TOKEN_PATH, 'wb') as token:
        pickle.dump(creds, token)

# Step 4: Create Draft Post
service = build('blogger', 'v3', credentials=creds)
post = {
    "kind": "blogger#post",
    "title": "Draft Post via Python",
    "content": "<p>This is a saved draft post created using token.pickle from config folder.</p>"
}

result = service.posts().insert(blogId=BLOG_ID, body=post, isDraft=True).execute()
print("✅ Draft post created:", result['url'])
