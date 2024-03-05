import torch

if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

# train.py schema
train_loss = "train_loss"
train_acc = "train_acc"
train_recall = "train_recall"
val_acc = "val_acc"
val_loss = "val_loss"
val_recall = "val_recall"

# infer.py schema
first_page = "first_page"
page_path = "page_path"

# WebApp schema
page_color = "page_color"


__all__ = ["device", "first_page", "page_path", "page_color"]
