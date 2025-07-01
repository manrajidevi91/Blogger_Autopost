"""Helper functions for extracting text from PDFs and images."""

import pdfplumber
import pytesseract
from PIL import Image, UnidentifiedImageError
from pytesseract import TesseractError


def extract_text_from_pdf(pdf_path):
    """Return text content from a PDF file or an empty string on failure."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except FileNotFoundError:
        print(f"File not found: {pdf_path}")
    except Exception as e:
        print(f"OCR error while processing PDF {pdf_path}: {e}")
    return ""


def extract_text_from_image(image_path):
    """Return text extracted from an image file or an empty string on failure."""
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text
    except FileNotFoundError:
        print(f"File not found: {image_path}")
    except (UnidentifiedImageError, TesseractError) as e:
        print(f"OCR error while processing image {image_path}: {e}")
    except Exception as e:
        print(f"Unexpected error reading image {image_path}: {e}")
    return ""

