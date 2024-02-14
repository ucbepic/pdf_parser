import flor
import fitz
import os
import warnings
import sys
from tqdm import tqdm

from app.constants import PDF_DIR
from app import config

infer = flor.dataframe(config.page_path, config.first_page)
infer = flor.utils.latest(infer)
infer[config.pdf_name] = infer[config.page_path].map(
    lambda x: os.path.basename(os.path.split(x)[0])
)
if not infer.empty:
    infer[config.first_page] = infer[config.first_page].astype(int)
    infer = infer.sort_values(by=["document", "page"])

# TODO: use page_colors if tstamp for flask > infer tstamp


def split_pdf(pdf_name, start_page, end_page):
    print(f"Splitting {pdf_name} from {start_page} to {end_page}")
    pdf_path = os.path.join(PDF_DIR, pdf_name)
    assert os.path.exists(pdf_path)
    doc = fitz.open(pdf_path)  # type: ignore
    new_pdf_name = f"{pdf_name.rsplit('.', 1)[0]}_to_{end_page}.pdf"
    new_pdf_path = os.path.join(PDF_DIR, new_pdf_name)

    new_doc = fitz.open()  # type: ignore
    for i in range(start_page - 1, end_page):  # adjust from 1-indexed to 0-indexed
        new_doc.insert_pdf(doc, from_page=i, to_page=i)

    new_doc.save(new_pdf_path)
    new_doc.close()
    doc.close()


for pdf_name in infer["pdf_name"].unique():
    document = infer[infer["pdf_name"] == pdf_name]
    first_pages = document[document[config.first_page] == 1].reset_index(drop=True)

    print(first_pages)
    print("num segments", len(first_pages))
    print("last page", document.iloc[-1]["page"])

    if len(first_pages) == 1:
        print(f"No splitting to do for {pdf_name}")
        continue

    for index, row in first_pages.iterrows():
        if index + 1 == len(first_pages):
            split_pdf(
                pdf_name + ".pdf", int(row["page"]), int(document.iloc[-1]["page"])
            )
        else:
            next_row = first_pages.iloc[index + 1]
            split_pdf(pdf_name + ".pdf", int(row["page"]), int(next_row["page"]) - 1)

    os.remove(os.path.join(PDF_DIR, pdf_name + ".pdf"))
