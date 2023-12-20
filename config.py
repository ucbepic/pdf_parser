import torch

if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

# infer.py schema
first_page = "first_page"
page_path = "page_path"

# WebApp schema
from app.constants import pdf_name, page_color


__all__ = ["device", "first_page", "page_path", "pdf_name", "page_color"]
