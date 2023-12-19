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

__all__ = ["device", "first_page", "page_path"]
