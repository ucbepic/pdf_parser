import os

# Absolute path to the directory where PDFs are stored
PDF_DIR = os.path.join("app", "static", "private", "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

IMGS_DIR = os.path.join("app", "static", "private", "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)

TXT_DIR = os.path.join("app", "static", "private", "txts")
os.makedirs(TXT_DIR, exist_ok=True)

OCR_DIR = os.path.join("app", "static", "private", "ocr")
os.makedirs(OCR_DIR, exist_ok=True)


__all__ = ["PDF_DIR", "IMGS_DIR", "TXT_DIR", "OCR_DIR"]
