import os

from utils.ai_engine import scrape_url_content, generate_content_with_ai
from utils.youtube_service import get_youtube_transcript
from utils.pdf_image_service import extract_text_from_pdf, extract_text_from_image
from utils.config import load_sites_data
from utils.blogger_client import publish_post

def create_post(site_name, content_source, ai_model, template, source_input):
    """Create and publish a post to Blogger for the specified site."""

    extracted_content = None
    if content_source == "url":
        extracted_content = scrape_url_content(source_input)
    elif content_source == "youtube":
        # Assuming source_input is YouTube video ID or URL that can be parsed for ID
        video_id = source_input.split("v=")[-1].split("&")[0]
        extracted_content = get_youtube_transcript(video_id)
    elif content_source == "pdf":
        extracted_content = extract_text_from_pdf(source_input)
    elif content_source == "image":
        extracted_content = extract_text_from_image(source_input)
    else:
        return {"status": "error", "message": "Unsupported content source"}

    if not extracted_content:
        return {"status": "error", "message": "Failed to extract content"}

    # Generate content using AI
    ai_generated_content = generate_content_with_ai(extracted_content, ai_model)

    # ------------------------------------------------------------------
    # Load site configuration (blog_id and credential path)
    sites = load_sites_data()
    site_info = sites.get(site_name)
    if not site_info:
        return {"status": "error", "message": f"Site '{site_name}' not found"}

    blog_id = site_info.get("blog_id")
    credential_path = site_info.get("credential_path")
    if not blog_id or not credential_path:
        return {
            "status": "error",
            "message": f"Missing blog_id or credentials for site '{site_name}'",
        }

    # ------------------------------------------------------------------
    # Read template file
    template_path = os.path.join("static", "templates", site_name, template)
    if not os.path.exists(template_path):
        return {
            "status": "error",
            "message": f"Template '{template}' not found for site '{site_name}'",
        }

    with open(template_path, "r", encoding="utf-8") as f:
        template_str = f.read()

    # Insert AI generated content into template
    if "{{content}}" in template_str:
        final_post_content = template_str.replace("{{content}}", ai_generated_content)
    else:
        final_post_content = f"{template_str}\n{ai_generated_content}"

    title = f"Automated Post - {site_name}"

    # ------------------------------------------------------------------
    # Publish to Blogger
    publish_result = publish_post(blog_id, credential_path, title, final_post_content)

    # Combine result info with content for debugging
    publish_result["content"] = final_post_content

    return publish_result
