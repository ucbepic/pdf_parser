import fitz
import os
from PIL import Image
import pytesseract
from multiprocessing import Pool

from app import PDF_DIR, IMGS_DIR, TXT_DIR, OCR_DIR
from tqdm import tqdm
import io


def process_page(pdf_path, page_num, img_path, txt_path, ocr_path):
    doc = fitz.open(pdf_path)  # type: ignore
    page = doc.load_page(page_num)

    pix = page.get_pixmap()
    output_image = os.path.join(img_path, f"page_{page_num}.png")
    pix.save(output_image)
    img_bytes = io.BytesIO(pix.tobytes("png"))
    img = Image.open(img_bytes)

    if page_num == 0:
        # Save the first page as the preview
        preview_path = os.path.join(
            IMGS_DIR, os.path.splitext(os.path.basename(pdf_path))[0] + ".png"
        )
        pix.save(preview_path)

    # Extract text and save as TXT
    text = page.get_text()
    output_text = os.path.join(txt_path, f"page_{page_num}.txt")
    with open(output_text, "w", encoding="utf-8") as text_file:
        text_file.write(text)

    # Extract text with pytesseract
    extracted_text = pytesseract.image_to_string(img)

    # Save the extracted text
    ocr_file_path = os.path.join(ocr_path, f"page_{page_num}.txt")
    with open(ocr_file_path, "w", encoding="utf-8") as text_file:
        text_file.write(extracted_text)

    doc.close()


def process_pdf(pdf_path):
    # set img_path, txt_path, and ocr_path
    img_path = os.path.join(IMGS_DIR, os.path.splitext(os.path.basename(pdf_path))[0])
    os.makedirs(img_path, exist_ok=True)
    txt_path = os.path.join(TXT_DIR, os.path.splitext(os.path.basename(pdf_path))[0])
    os.makedirs(txt_path, exist_ok=True)
    ocr_path = os.path.join(OCR_DIR, os.path.splitext(os.path.basename(pdf_path))[0])
    os.makedirs(ocr_path, exist_ok=True)

    doc = fitz.open(pdf_path)  # type: ignore
    page_numbers = range(len(doc))
    doc.close()

    # Create a pool of workers and distribute the tasks
    with Pool() as pool:
        args = [
            (pdf_path, page_num, img_path, txt_path, ocr_path)
            for page_num in page_numbers
        ]
        pool.starmap(process_page, args)


if __name__ == "__main__":
    for pdf_file in tqdm(os.listdir(PDF_DIR)):
        if not pdf_file.endswith(".pdf"):
            continue

        pdf_path = os.path.join(PDF_DIR, pdf_file)
        process_pdf(pdf_path)
