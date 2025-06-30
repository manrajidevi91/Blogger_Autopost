import os
from utils.ai_engine import scrape_url_content, generate_content_with_ai
from utils.youtube_service import get_youtube_transcript
from utils.pdf_image_service import extract_text_from_pdf, extract_text_from_image

def create_post(site_name, content_source, ai_model, template, source_input):
    extracted_content = None
    if content_source == 'url':
        extracted_content = scrape_url_content(source_input)
    elif content_source == 'youtube':
        # Assuming source_input is YouTube video ID or URL that can be parsed for ID
        video_id = source_input.split('v=')[-1].split('&')[0] # Simple parsing
        extracted_content = get_youtube_transcript(video_id)
    elif content_source == 'pdf':
        extracted_content = extract_text_from_pdf(source_input)
    elif content_source == 'image':
        extracted_content = extract_text_from_image(source_input)
    else:
        return {"status": "error", "message": "Unsupported content source"}

    if not extracted_content:
        return {"status": "error", "message": "Failed to extract content"}

    # Generate content using AI
    ai_generated_content = generate_content_with_ai(extracted_content, ai_model)

    # Placeholder for applying template and posting to Blogger
    final_post_content = f"<!-- Template: {template} -->\n{ai_generated_content}"
    print(f"Final post content for Blogger:\n{final_post_content}")

    return {"status": "success", "message": "Post created successfully (Blogger API integration pending)", "content": final_post_content}
