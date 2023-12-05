.PHONY: run install lint clean pdf2png infer retrain

# Set the FLASK_APP environment variable
export FLASK_APP=run.py
export FLASK_ENV=development

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

pdf2png:
	@echo "Preparing data..."
	@python pdf2png.py

infer: 
	@echo "Inferencing..."
	@python infer.py

retrain: 
	@echo "Retraining..."
	@python retrain.py

apply_split:
	@echo "Applying split..."
	@python apply_split.py

# Run the Flask development server
run:
	@echo "Starting Flask development server..."
	@flask run