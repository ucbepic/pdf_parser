import flor
import fitz
import os

from app.constants import PDF_DIR, IMGS_DIR, OCR_DIR
from app import config

from tqdm import tqdm


def split_pdf(pdf_name, start_page, end_page):
    print(f"Splitting {pdf_name} from {start_page} to {end_page}")
    pdf_path = os.path.join(PDF_DIR, pdf_name)
    assert os.path.exists(pdf_path)
    doc = fitz.open(pdf_path)  # type: ignore
    new_pdf_name = f"{pdf_name.rsplit('.', 1)[0]}_to_{end_page}.pdf"
    new_pdf_path = os.path.join(PDF_DIR, new_pdf_name)

    new_doc = fitz.open()  # type: ignore
    for i in range(start_page, end_page + 1):  # 0-indexed
        new_doc.insert_pdf(doc, from_page=i, to_page=i)

    new_doc.save(new_pdf_path)
    new_doc.close()
    doc.close()


if __name__ == "__main__":

    df = flor.utils.latest(flor.dataframe(config.first_page, config.page_color))
    if not df.empty:
        if df[config.first_page].isna().any():
            df[config.first_page] = (
                df.shift(1)[config.page_color] != df[config.page_color]
            ).astype(int)
        else:
            df[config.first_page] = df[config.first_page].astype(int)

    for doc_name in tqdm(df["document_value"].unique()):
        document = df[df["document_value"] == doc_name]
        first_pages = document[document[config.first_page] == 1].reset_index(drop=True)

        if len(first_pages) == 1:
            continue

        first_pages["last_page"] = (
            first_pages["page_value"].shift(-1).fillna(document.max().page).astype(int)
            - 1
        )

        for index, row in first_pages.iterrows():
            split_pdf(doc_name + ".pdf", int(row["page_value"]), int(row["last_page"]))

        os.remove(os.path.join(PDF_DIR, doc_name + ".pdf"))
