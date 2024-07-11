import os
from app import IMGS_DIR, config
import flor

documents = sorted(
    [
        each
        for each in os.listdir(IMGS_DIR)
        if os.path.isdir(os.path.join(IMGS_DIR, each))
    ]
)

# 0-indexed first pages of each document
# v1 :: TOC -> page_num := TOC + 8 -> TOC + 7
first_page = {"mueller_report": [0, 207, 394]}


if __name__ == "__main__":
    for doc in flor.loop("document", documents):
        for i in flor.loop("page", range(len(os.listdir(os.path.join(IMGS_DIR, doc))))):
            page_path = f"page_{i}.png"
            flor.log(config.page_path, os.path.join(IMGS_DIR, doc, page_path))
            if doc in first_page:
                flor.log(config.first_page, 1 if i in first_page[doc] else 0)
            else:
                flor.log(config.first_page, 1 if i == 0 else 0)
