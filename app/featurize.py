from .constants import PDF_DIR, TXT_DIR
import re


def analyze_text(text_file):
    with open(text_file, 'r') as file:
        text = file.read()

    # Example pattern for detecting headings (e.g., all caps)
    headings = re.findall(r'^[A-Z\s]+$', text, re.MULTILINE)

    # Example pattern for detecting page numbers
    page_numbers = re.findall(r'\b\d+\b', text)  # Simplistic; needs refinement

    # Other analysis can be added here

    return headings, page_numbers, text 

