.PHONY: run install lint clean  infer apply_split images train

# Set the FLASK_APP environment variable
export FLASK_APP=run.py

export FLASK_ENV=development

PDFS := $(wildcard app/static/private/pdfs/*.pdf)
IMAGES := $(patsubst app/static/private/pdfs/%.pdf,app/static/private/imgs/%.png,$(PDFS))

images: $(IMAGES)

$(IMAGES): app/static/private/imgs/%.png : app/static/private/pdfs/%.pdf
	@echo "Preparing data..."
	@python pdf2png.py

# Install dependencies from requirements.txt
install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt
 
# Clean up pyc files and __pycache__ directories
clean:
	@echo "Cleaning up..."
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete
	@find app/static/private/imgs -mindepth 1 -delete

model.pth: get_best_ckpt.py
	@echo "Generating model..."
	@python get_best_ckpt.py

infer: model.pth
	@echo "Inferencing..."
	@python infer.py

train:
	@echo "Training..."
	@python train.py

apply_split:
	@echo "Applying split..."
	@python apply_split.py

# Run the Flask development server
run:
	@echo "Starting Flask development server..."
	@flask run