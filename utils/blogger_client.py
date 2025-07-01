import requests

BASE_URL = "https://www.googleapis.com/blogger/v3"


def publish_post(blog_id: str, api_key: str, title: str, content: str) -> dict:
    """Publish a post to Blogger via the REST API.

    Args:
        blog_id: ID of the target blog.
        api_key: Blogger API key.
        title: Title of the post.
        content: HTML content of the post.

    Returns:
        Dictionary containing status information from the API.
    """
    url = f"{BASE_URL}/blogs/{blog_id}/posts/"
    payload = {
        "kind": "blogger#post",
        "blog": {"id": blog_id},
        "title": title,
        "content": content,
    }
    try:
        response = requests.post(url, params={"key": api_key}, json=payload)
        response.raise_for_status()
        return {
            "status": "success",
            "post_id": response.json().get("id"),
            "response": response.json(),
        }
    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "message": str(exc),
            "response": getattr(exc, "response", None).text if getattr(exc, "response", None) else None,
        }
