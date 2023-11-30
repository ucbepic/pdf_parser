# PDF Parser

This project is a Flask web application that parses PDFs and uses machine learning to infer and train data. The application is built with Python, Flask, Flor, and PyTorch.

## Flask Web Application

The Flask application is responsible for handling PDF files and converting them into images for further processing. The application has two main routes:

- `/` (index): This route lists all the PDF files in the PDF_DIR directory and displays a preview of each PDF file. The previews are PNG images that are resized to a standard size for display.

- `/view-pdf`: This route takes a PDF file name as a parameter and displays the PDF file if it exists in the PDF_DIR directory.

The application uses the PIL library to handle image resizing and the werkzeug library to handle file security.

## Infer Pipeline

The infer pipeline is implemented in `infer.py`. It uses the Flor library to manage the experiment and the PyTorch library to load the trained model and make predictions. The pipeline processes all the images in the IMGS_DIR directory and makes a prediction for each image. The prediction results are logged with Flor.

## Train Pipeline

The train pipeline is implemented in `train.py`. It uses the Flor library to manage the experiment and the PyTorch library to define the model, loss function, optimizer, and learning rate scheduler. The pipeline uses a ResNet18 model with a modified final layer for binary classification. The model is trained on a dataset of images and their labels, which are loaded using a custom PDFPagesDataset class. The training process includes both a training phase and a validation phase for each epoch.

## Getting Started

To get started with this project, you need to install the required Python packages. You can do this by running the following command:

```
make install
```

After installing the dependencies, you can start the Flask application by running the following command:

```
flask run
```

You can also run the infer and train pipelines by running the following commands:

```
python infer.py
python train.py
```

## Contributing

Contributions are welcome. Please open an issue to discuss your ideas or open a pull request with your changes.

## License

This project is licensed under the terms of the MIT license.
