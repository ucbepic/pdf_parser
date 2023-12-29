from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import os
import flor
import numpy as np


from .featurize import analyze_text

from . import constants as const
from .constants import PDF_DIR, IMGS_DIR, TXT_DIR, OCR_DIR

app = Flask(__name__)
pdf_names = []


def resize_image(image_path, size=(300, 400)):
    # Open an image file
    with Image.open(image_path) as img:
        # Resize the image
        img = img.resize(size, Image.LANCZOS)
        # Save the image back to the same path
        img.save(image_path)


@app.route("/")
def index():
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]

    # Resize each image and create a list of tuples (pdf, image_path)
    pdf_previews = []
    for pdf in pdf_files:
        image_name = pdf.replace(".pdf", ".png")
        image_path = os.path.join(IMGS_DIR, image_name)
        if os.path.exists(image_path):
            resize_image(image_path)
            # Only include the part of the image_path that comes after 'app/static/private/imgs'
            relative_image_path = os.path.relpath(image_path, start="app/static")
            pdf_previews.append((pdf, relative_image_path))

    # Render the template with the PDF previews
    return render_template("index.html", pdf_previews=pdf_previews)


def get_colors():
    infer = flor.pivot("first_page", "page_path")
    infer = flor.utils.latest(
        infer[infer["page_path"].map(lambda x: os.path.splitext(pdf_names[-1])[0] in x)]
    )
    infer = infer.sort_values("page")
    if not infer.empty:
        webapp = flor.pivot("pdf_name", "page_color")
        webapp = flor.utils.latest(webapp[webapp["pdf_name"] == pdf_names[-1]])
        webapp = webapp.sort_values("page")
        if not webapp.empty:
            if (
                infer["tstamp"].drop_duplicates().values[0]
                > webapp["tstamp"].drop_duplicates().values[0]
            ):
                return (infer["first_page"].astype(int).cumsum() - 1).tolist()
            else:
                return webapp["page_color"].astype(int).tolist()
        else:
            return (infer["first_page"].astype(int).cumsum() - 1).tolist()


@app.route("/view-pdf")
def view_pdf():
    # TODO: Display the PNG not the PDF. Easier overlay.
    pdf_name = request.args.get("name")
    if not pdf_name:
        return "No file specified.", 400

    pdf_name = secure_filename(pdf_name)
    pdf_names.append(pdf_name)

    pdf_path = os.path.join(PDF_DIR, pdf_name)

    if os.path.isfile(pdf_path):
        # Render the label_pdf.html template with the PDF name and get_colors()
        return render_template("label_pdf.html", pdf_name=pdf_name, colors=get_colors())
    else:
        return "File not found.", 404


@app.route("/save_colors", methods=["POST"])
def save_colors():
    j = request.get_json()
    colors = j.get("colors", [])
    # Process the colors here...
    pdf_name = pdf_names.pop()
    pdf_names.clear()
    flor.log(const.pdf_name, pdf_name)
    for c in flor.loop("page", colors):
        flor.log(const.page_color, c)
    flor.commit()
    return "OK", 200


@app.route("/metadata-for-page/<int:page_num>")
def metadata_for_page(page_num: int):
    # Retrieve metadata for the specified page number
    metadata = [{"page_num": page_num}]
    # Identify the PDF that we're working with
    pdf_name = pdf_names[-1]
    metadata.append({"pdf_name": pdf_name})
    # Construct path to the text file
    txt_name = os.path.join(
        TXT_DIR, os.path.splitext(os.path.basename(pdf_name))[0], f"page_{page_num}.txt"
    )
    # Analyze the text on the page
    headings, page_numbers, txt_text = analyze_text(txt_name)
    # Add the results to the metadata dictionary

    metadata.append({"txt-headings": headings})
    metadata.append({"txt-page_numbers": page_numbers})

    # Construct path to the OCR file
    ocr_name = os.path.join(
        OCR_DIR, os.path.splitext(os.path.basename(pdf_name))[0], f"page_{page_num}.txt"
    )
    # Analyze the ocr on the page
    headings, page_numbers, ocr_text = analyze_text(ocr_name)
    # Add the results to the metadata dictionary
    metadata.append({"ocr-headings": headings})
    metadata.append({"ocr-page_numbers": page_numbers})

    if (
        len(txt_text) < len(ocr_text) // 2
        or len(txt_text.strip()) < len(txt_text) * 3 // 4
    ):
        metadata.append({"ocr-text": ocr_text})
    else:
        metadata.append({"txt-text": txt_text})

    # Retrieve metadata for the specified page number
    return jsonify(metadata)


if __name__ == "__main__":
    app.run(debug=True)
