import flor
import fitz
import os
import warnings
import sys
from tqdm import tqdm
from app import PDF_DIR

delta_colors = flor.pivot("pdf_name", "color")
delta_colors = flor.utils.latest(delta_colors)
delta_colors = delta_colors.sort_values(by=["pdf_name", "colors"])
print(delta_colors)


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

for pdf_name in delta_colors["pdf_name"].unique():
    pdf_colors = delta_colors[delta_colors["pdf_name"] == pdf_name].sort_values(by=["colors"])
    print(pdf_colors)
    segments = []
    for index, row in pdf_colors.iterrows():
        print(index, row)
        if index == 0 or (int(row["color"]) != int(pdf_colors.iloc[index - 1]["color"])):
            print("New segment")
            segments.append([row["colors"]])
        else:
            segments[-1].append(row["colors"])
    for segment in segments:
        split_pdf(pdf_name, min(segment), max(segment))


for pdf_name in delta_colors["pdf_name"].unique():
    os.remove(os.path.join(PDF_DIR, pdf_name))
