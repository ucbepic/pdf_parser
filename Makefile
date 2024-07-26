.PHONY: run install clean apply_split train install_tesseract

                                                 
#  _____ __    _____ _____ _____ __    _____ _____ 
# |   __|  |  |     | __  |  _  |  |  |  _  |   | |
# |   __|  |__|  |  |    -|   __|  |__|     | | | |
# |__|  |_____|_____|__|__|__|  |_____|__|__|_|___|
#                                                 


# Set the FLASK_APP environment variable
export FLASK_APP=run.py
export FLASK_ENV=development

UNAME_S := $(shell uname -s)
GIT_COMMIT := $(shell git rev-parse HEAD | cut -c 1-6)
PDFS := $(wildcard app/static/private/pdfs/*.pdf)

pdf_links: $(wildcard public/*.pdf)
	@echo "Creating softlinks to PDF files..."
	@for pdf in public/*.pdf; do \
		echo $$pdf; \
		mkdir -p app/static/private/pdfs; \
		ln -sf $$(realpath $$pdf) app/static/private/pdfs/$$(basename $$pdf); \
	done
	@touch pdf_links

process_pdfs: pdf_links pdf_demux.py 
	@echo "Processing PDF files..."
	@python pdf_demux.py
	@touch process_pdfs

featurize: process_pdfs featurize.py
	@echo "Featurizing Data..."
	@python featurize.py
	@touch featurize

model.pth: export_ckpt.py
	@echo "Generating model..."
	@python export_ckpt.py

infer: model.pth infer.py
	@echo "Inferencing..."
	@python infer.py
	@touch infer

hand_label: label_by_hand.py featurize
	@echo "Labeling by hand"
	@python label_by_hand.py
	@touch hand_label

train: featurize hand_label train.py
	@echo "Training..."
	@python train.py

apply_split: split.py clean
	@echo "Applying split..."
	@python split.py
	
ner_parse:
	@if [ -f ~/.flor/court-records-processing.db ]; then \
		mv ~/.flor/court-records-processing.db ~/.flor/court-records-processing.db.bak; \
	fi
	@if [ -f ~/.flor/pdf_parser.db ]; then \
		mv ~/.flor/pdf_parser.db ~/.flor/court-records-processing.db; \
	fi
	@ls -lagh ~/.flor
	@if [ -d ../court_records ]; then \
		mv ../court_records ../court_records.bak; \
	fi
	@ln -sf $(realpath app/static/private/pdfs) ../court_records

	@cd ../court-records-processing && (git checkout flor.pdf_parser$(GIT_COMMIT) || git checkout -b flor.pdf_parser$(GIT_COMMIT)) && make case_file_processer

	@rm -f ../court_records
	@if [ -d ../court_records.bak ]; then \
		mv ../court_records.bak ../court_records; \
	fi
	@mv ~/.flor/court-records-processing.db ~/.flor/pdf_parser.db
	@if [ -f ~/.flor/court-records-processing.db.bak ]; then \
		mv ~/.flor/court-records-processing.db.bak ~/.flor/court-records-processing.db; \
	fi
	@ls -lagh ~/.flor
	@touch ner_parse


# Run the Flask development server
run_infer: featurize infer
	@echo "Starting Flask development server..."
	# @flask run --port 5000
	@python run.py

run_hand: hand_label
	@echo "Starting Flask development server..."
	# @flask run --port 5000
	@python run.py

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
	@rm -f hand_label
	@rm -f featurize
	@rm -f ner_parse
	@rm -f pdf_links
