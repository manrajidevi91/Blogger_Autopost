import os
import requests
from bs4 import BeautifulSoup
import openai
import google.generativeai as genai
from utils.config import load_ai_config

def scrape_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract readable content (e.g., paragraphs, article body)
        paragraphs = soup.find_all('p')
        content = '\n'.join([p.get_text() for p in paragraphs])
        return content
    except requests.exceptions.RequestException as e:
        print(f"Error scraping URL {url}: {e}")
        return None

def generate_content_with_ai(text_input, ai_model):
    """Generate content using the selected AI model."""

    model = ai_model.lower()
    if model == "chatgpt":
        return generate_with_chatgpt(text_input)
    if model == "gemini":
        return generate_with_gemini(text_input)

    return f"Unsupported AI model: {ai_model}"


def generate_with_chatgpt(text: str) -> str:
    """Generate text using the ChatGPT API."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        cfg = load_ai_config()
        if cfg.get("provider", "").lower() == "openai":
            api_key = cfg.get("api_key")
    if not api_key:
        return "OpenAI API key not configured."

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}],
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:  # noqa: BLE001
        return f"Error calling ChatGPT API: {exc}"


def generate_with_gemini(text: str) -> str:
    """Generate text using the Google Gemini API."""

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        cfg = load_ai_config()
        if cfg.get("provider", "").lower() == "gemini":
            api_key = cfg.get("api_key")
    if not api_key:
        return "Google API key not configured."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(text)
        return response.text
    except Exception as exc:  # noqa: BLE001
        return f"Error calling Gemini API: {exc}"

