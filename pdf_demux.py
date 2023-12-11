import fitz
import os

from app import PDF_DIR, IMGS_DIR, TXT_DIR
from tqdm import tqdm


def process_pdf(pdf_path, img_path, txt_path):
    doc = fitz.open(pdf_path)  # type: ignore
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Save page as PNG
        pix = page.get_pixmap()
        output_image = os.path.join(img_path, f"page_{page_num}.png")
        pix.save(output_image)

        if page_num == 0:
            # Save the first page as the preview
            preview_path = os.path.join(
                IMGS_DIR, os.path.splitext(os.path.basename(pdf_path))[0] + ".png"
            )
            pix.save(preview_path)

        # Extract text and save as TXT
        text = page.get_text()
        output_text = os.path.join(txt_path, f"page_{page_num}.txt")
        with open(output_text, "w") as text_file:
            text_file.write(text)

    doc.close()


if __name__ == "__main__":
    for pdf_file in tqdm(os.listdir(PDF_DIR)):
        if not pdf_file.endswith(".pdf"):
            continue
        pdf_name = os.path.splitext(pdf_file)[0]

        img_path = os.path.join(IMGS_DIR, pdf_name)
        os.makedirs(img_path, exist_ok=True)
        txt_path = os.path.join(TXT_DIR, pdf_name)
        os.makedirs(txt_path, exist_ok=True)

        pdf_path = os.path.join(PDF_DIR, pdf_file)
        process_pdf(pdf_path, img_path, txt_path)
