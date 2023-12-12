.PHONY: run install clean  infer apply_split process_pdfs train install_tesseract

# Set the FLASK_APP environment variable
export FLASK_APP=run.py
export FLASK_ENV=development

PDFS := $(wildcard app/static/private/pdfs/*.pdf)

# Detect OS
UNAME_S := $(shell uname -s)

process_pdfs: $(PDFS)
	@echo "Processing PDF files..."
	@python pdf_demux.py

model.pth: get_best_ckpt.py
	@echo "Generating model..."
	@python get_best_ckpt.py

infer: model.pth
	@echo "Inferencing..."
	@python infer.py

train: process_pdfs
	@echo "Training..."
	@python train.py

apply_split:
	@echo "Applying split..."
	@python apply_split.py

# A dummy file to track when inferencing was last run
last_inference: infer
	@touch last_inference

# Run the Flask development server
run: process_pdfs last_inference
	@echo "Starting Flask development server..."
	@flask run

# Tesseract installation depending on the OS
install_tesseract:
	@echo "Installing Tesseract OCR..."
ifeq ($(UNAME_S),Linux)
	sudo apt-get update
	sudo apt-get install tesseract-ocr
endif
ifeq ($(UNAME_S),Darwin)
	brew install tesseract
endif
ifeq ($(UNAME_S),Windows_NT)
	@echo "Please install Tesseract OCR manually from https://github.com/UB-Mannheim/tesseract/wiki"
endif

# Install dependencies from requirements.txt
install: install_tesseract
	@echo "Installing dependencies..."
	@pip install -r requirements.txt
 
# Clean up pyc files and __pycache__ directories
clean:
	@echo "Cleaning up..."
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete
	@find app/static/private/imgs -mindepth 1 -delete
	@find app/static/private/txts -mindepth 1 -delete