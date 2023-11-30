.PHONY: run install lint clean data_prep

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

data_prep:
	@echo "Preparing data..."
	@python pdf2png.py

infer: data_prep
	@echo "Inferencing..."
	@python infer.py

retrain: data_prep
	@echo "Retraining..."
	@python retrain.py

# Run the Flask development server
run: infer
	@echo "Starting Flask development server..."
	@flask run