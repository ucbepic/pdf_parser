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
    "6-Complaint__Judgment": [0, 13, 14],
    "AmericanHistoriansAmicus": [0],
    "AppealsPerCuriam_NoAbsoluteImmunity": [0],
    "Menlo_Ave_9Jul20": [0, 9, 10, 16],
    "NY_Indictment_StormyD": [0, 15, 16],
    "george_santos_report": [0],
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
