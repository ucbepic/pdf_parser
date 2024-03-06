from typing import Any, Dict, List
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import flor


from . import config
from .constants import PDF_DIR, IMGS_DIR

app = Flask(__name__)
pdf_names = []


def get_colors():
    # TODO: this method may also be called by apply_split
    infer = flor.dataframe(config.first_page, config.page_path)
    infer = flor.utils.latest(
        infer[
            infer[config.page_path].map(
                lambda x: os.path.splitext(pdf_names[-1])[0] in x
            )
        ]
    )
    if not infer.empty:
        infer = infer.sort_values("page")
        webapp = flor.dataframe(config.page_color)
        if not webapp.empty:
            webapp = flor.utils.latest(
                webapp[webapp["document_value"] == pdf_names[-1]]
            )
            if webapp.empty:
                return (infer[config.first_page].astype(int).cumsum() - 1).tolist()
            webapp = webapp.sort_values("page")
            if (
                infer["tstamp"].drop_duplicates().values[0]
                > webapp["tstamp"].drop_duplicates().values[0]
            ):
                return (infer[config.first_page].astype(int).cumsum() - 1).tolist()
            else:
                return webapp[config.page_color].astype(int).tolist()
        else:
            return (infer[config.first_page].astype(int).cumsum() - 1).tolist()


@app.route("/")
def index():
    pdf_files = [
        os.path.splitext(f)[0] for f in os.listdir(PDF_DIR) if f.endswith(".pdf")
    ]

    # Resize each image and create a list of tuples (pdf, image_path)
    pdf_previews = []
    for doc_name in flor.loop("document", pdf_files):
        image_name = doc_name + ".png"
        image_path = os.path.join(IMGS_DIR, image_name)
        if os.path.exists(image_path):
            # Only include the part of the image_path that comes after 'app/static/private/imgs'
            relative_image_path = os.path.relpath(image_path, start="app/static")
            pdf_previews.append((doc_name + ".pdf", relative_image_path))

    # Render the template with the PDF previews
    return render_template("index.html", pdf_previews=pdf_previews)


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
    with flor.iteration("document", None, os.path.splitext(pdf_name)[0]):
        for i in flor.loop("page", range(len(colors))):
            flor.log(config.page_color, colors[i])
        flor.commit()

        return jsonify({"message": "Colors saved successfully"}), 200


memoized_features = flor.dataframe("merge-source", "merged-text")


@app.route("/metadata-for-page/<int:page_num>")
def metadata_for_page(page_num: int):
    view_selection = flor.arg("debugging", 1)
    if view_selection == 0:
        lattice = memoized_features[os.path.splitext(pdf_names[-1])[0], page_num]
        last_message = lattice[-1]
        assert "ocr-text" in last_message or "txt-text" in last_message
        if "ocr-text" in last_message:
            return jsonify([{f"ocr-page-{page_num+1}": last_message["ocr-text"]}])
        else:
            return jsonify([{f"txt-page-{page_num+1}": last_message["txt-text"]}])
    elif view_selection == 1:
        # Retrieve metadata for the specified page number
        metadata: List[Dict[str, Any]] = [{"page_num": page_num + 1}]
        # Identify the PDF that we're working with
        metadata += memoized_features[os.path.splitext(pdf_names[-1])[0], page_num]
        # Retrieve metadata for the specified page number
        return jsonify(metadata)
    else:
        pass


if __name__ == "__main__":
    app.run(debug=True)
