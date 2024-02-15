.PHONY: run install clean apply_split train install_tesseract

                                                 
#  _____ __    _____ _____ _____ __    _____ _____ 
# |   __|  |  |     | __  |  _  |  |  |  _  |   | |
# |   __|  |__|  |  |    -|   __|  |__|     | | | |
# |__|  |_____|_____|__|__|__|  |_____|__|__|_|___|
#                                                 


# Set the FLASK_APP environment variable
export FLASK_APP=run.py
export FLASK_ENV=development

PDFS := $(wildcard app/static/private/pdfs/*.pdf)

# Detect OS
UNAME_S := $(shell uname -s)

process_pdfs: $(PDFS) pdf_demux.py
	@echo "Processing PDF files..."
	@python pdf_demux.py
	@touch process_pdfs

model.pth: export_ckpt.py
	@echo "Generating model..."
	@python export_ckpt.py

infer: label_by_hand.py
	@echo "Inferencing..."
	@python label_by_hand.py
	@touch infer

train: process_pdfs train.py
	@echo "Training..."
	@python train.py

apply_split: split.py clean
	@echo "Applying split..."
	@python split.py
	

# Run the Flask development server
run: process_pdfs infer
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
install: install_tesseract requirements.txt
	@echo "Installing dependencies..."
	@pip install -r requirements.txt
 
# Clean up pyc files and __pycache__ directories
clean:
	@echo "Cleaning up..."
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete
	@find app/static/private/imgs -mindepth 1 -delete
	@find app/static/private/txts -mindepth 1 -delete
	@find app/static/private/ocr -mindepth 1 -delete
	@rm -f infer
	@rm -f process_pdfs
