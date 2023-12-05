from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import os


app = Flask(__name__)

# Absolute path to the directory where PDFs are stored
PDF_DIR = os.path.join("app", "static", "private", "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

IMGS_DIR = os.path.join("app", "static", "private", "imgs")
os.makedirs(IMGS_DIR, exist_ok=True)


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


@app.route("/view-pdf")
def view_pdf():
    pdf_name = request.args.get("name")
    if not pdf_name:
        return "No file specified.", 400

    pdf_name = secure_filename(pdf_name)

    pdf_path = os.path.join(PDF_DIR, pdf_name)

    if os.path.isfile(pdf_path):
        # Render the label_pdf.html template with the PDF name
        return render_template("label_pdf.html", pdf_name=pdf_name)
    else:
        return "File not found.", 404


@app.route("/save_colors", methods=["POST"])
def save_colors():
    j = request.get_json()
    colors = j.get("colors", [])
    # Process the colors here...
    for color in colors:
        print(f"Color: {color}")
    return jsonify({"message": "Colors saved successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
