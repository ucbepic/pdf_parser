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
first_page = {
    "mueller_report": [0, 207, 394],
    # v1 :: TOC + 7
    # "mueller_report_V1": [0, (11 + 7), (14 + 7), (36 + 7), (66 + 7), (174 + 7)],
    # v2 :: TOC + 4
    # "mueller_report_V2": [0, (9 + 4), (15 + 4), (159 + 4), (182 + 4)],
    "Presidential_Immunity": [0, 51, 60, 67, 97],  # TODO: split on syllabus?
}


if __name__ == "__main__":
    for doc in flor.loop("document", documents):
        for i in flor.loop("page", range(len(os.listdir(os.path.join(IMGS_DIR, doc))))):
            page_path = f"page_{i}.png"
            flor.log(config.page_path, os.path.join(IMGS_DIR, doc, page_path))
            if doc in first_page:
                flor.log(config.first_page, 1 if i in first_page[doc] else 0)
            else:
                flor.log(config.first_page, 1 if i == 0 else 0)
