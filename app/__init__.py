from typing import Any, Dict, List
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import flor
import warnings

from . import config
from .constants import PDF_DIR, IMGS_DIR

app = Flask(__name__)
pdf_names = []
feat_names = [
    "txt-headings",
    "txt-page_numbers",
    "ocr-headings",
    "ocr-page_numbers",
    "merge-source",
    "merged-text",
]
memoized_features = None


def get_colors():
    # TODO: this method may also be called by apply_split
    df = flor.dataframe(config.first_page, config.page_color)
    if not df.empty:
        df = df[df["document_value"] == os.path.splitext(pdf_names[-1])[0]]
        if not df.empty:
            if df[config.page_color].notna().any():
                df = flor.utils.latest(df[df.page_color.notna()])
                return df[config.page_color].astype(int).tolist()
            else:
                df = flor.utils.latest(df)
                return (df[config.first_page].astype(int).cumsum() - 1).tolist()


def get_coordinates():
    # TODO: To be implemented
    data = flor.dataframe("c_left", "c_top", "c_width", "c_height")
    return jsonify(data)


@app.route("/")
def index():
    global memoized_features, feat_names
    if memoized_features is None:
        memoized_features = flor.utils.latest(flor.dataframe(*feat_names))

    pdf_files = [
        os.path.splitext(f)[0] for f in os.listdir(PDF_DIR) if f.endswith(".pdf")
    ]
    by_page = [each.split("_to_") for each in pdf_files if "_to_" in each]
    by_page = sorted([(n, int(p)) for n, p in by_page])
    reservoir = sorted([each for each in pdf_files if "_to_" not in each])
    pdf_files = [f"{n}_to_{p}" for n, p in by_page] + reservoir

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
        # TODO: NER
        labeling = flor.arg("labeling", 0)
        if labeling == 0:
            return render_template(
                "label_pdf.html", pdf_name=pdf_name, colors=get_colors()
            )
        elif labeling == 1:
            return render_template("ner_pdf.html", pdf_name=pdf_name)
        else:
            raise
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


@app.route("/metadata-for-page/<int:page_num>")
def metadata_for_page(page_num: int):
    view_selection = 0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        record = memoized_features[
            memoized_features["document_value"] == os.path.splitext(pdf_names[-1])[0]
        ][memoized_features["page"] == page_num + 1].to_dict(orient="records")[0]
    if view_selection == 0:
        if record["merge-source"] == "ocr":
            return jsonify([{f"ocr-page-{page_num+1}": record["merged-text"]}])
        else:
            return jsonify([{f"txt-page-{page_num+1}": record["merged-text"]}])
    elif view_selection == 1:
        # Retrieve metadata for the specified page number
        metadata: List[Dict[str, Any]] = [{"page_num": page_num + 1}]
        # Identify the PDF that we're working with
        for k in record:
            if k in feat_names:
                try:
                    obj = eval(record[k])
                    if isinstance(obj, list):
                        obj = [str(each).strip() for each in obj]
                        metadata.append({k: obj})
                    else:
                        print("unknown type", k, ":", type(obj))
                except:
                    metadata.append({k: str(record[k])})
        # Retrieve metadata for the specified page number
        return jsonify(metadata)
    else:
        pass


if __name__ == "__main__":
    app.run(debug=True)
