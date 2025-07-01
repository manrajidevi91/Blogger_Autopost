from google.oauth2 import service_account
from googleapiclient.discovery import build

BASE_URL = "https://www.googleapis.com/blogger/v3"
SCOPES = ["https://www.googleapis.com/auth/blogger"]


def publish_post(blog_id: str, credential_path: str, title: str, content: str) -> dict:
    """Publish a post to Blogger via the REST API using OAuth credentials.

    Args:
        blog_id: ID of the target blog.
        credential_path: Path to service account JSON credentials.
        title: Title of the post.
        content: HTML content of the post.

    Returns:
        Dictionary containing status information from the API.
    """
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credential_path, scopes=SCOPES
        )
    except Exception as exc:
        return {"status": "error", "message": f"Failed to load credentials: {exc}"}

    try:
        service = build("blogger", "v3", credentials=credentials)
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
