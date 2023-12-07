import flor
import fitz
import os

from app import PDF_DIR

import warnings

delta_colors = flor.pivot("pdf_name", "color")
delta_colors = flor.utils.latest(delta_colors)
delta_colors = delta_colors.sort_values(by=["pdf_name", "color"])
# print(delta_colors)
color_segments = delta_colors.groupby(["pdf_name", "color"])["colors"].agg(
    ["min", "max"]
)
print(color_segments)

import sys
sys.exit(0)

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


for index, row in color_segments.iterrows():
    pdf_name, color = index
    start_page, end_page = row["min"], row["max"]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        split_pdf(pdf_name, start_page, end_page)

for pdf_name in delta_colors["pdf_name"].unique():
    os.remove(os.path.join(PDF_DIR, pdf_name))
