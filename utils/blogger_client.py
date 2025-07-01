import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE_URL = "https://www.googleapis.com/blogger/v3"
SCOPES = ["https://www.googleapis.com/auth/blogger"]


def publish_post(blog_id: str, credential_path: str, title: str, content: str) -> dict:
    """Publish a post to Blogger using OAuth user credentials.

    Args:
        blog_id: ID of the target blog.
        credential_path: Path to OAuth ``client_secret.json`` file.
        title: Title of the post.
        content: HTML content of the post.

    Returns:
        Dictionary containing status information from the API.
    """
    token_path = os.path.join(os.path.dirname(credential_path), "token.pickle")
    creds = None
    try:
        if os.path.exists(token_path):
            with open(token_path, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credential_path, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, "wb") as token:
                pickle.dump(creds, token)
    except Exception as exc:
        return {"status": "error", "message": f"Failed to load credentials: {exc}"}

    try:
        service = build("blogger", "v3", credentials=creds)
        body = {
            "kind": "blogger#post",
            "title": title,
            "content": content,
        }
        response = service.posts().insert(blogId=blog_id, body=body).execute()
        return {
            "status": "success",
            "post_id": response.get("id"),
            "response": response,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
