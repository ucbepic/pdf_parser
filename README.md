# PDF Parser
This project presents a Flask-based web application with a focus on user interface and optional AI integration. The primary command, `make run`, initiates the web server and provides access to the core functionalities. Advanced users can optionally enhance the application by training a model or updating it with the best version.

## Running the Web Application

### Prerequisites
- Python 3.x
- Flask
- Other dependencies in `requirements.txt`

### Quick Start
To quickly start the web application:
```bash
git clone git@github.com:ucbepic/pdf_parser.git
cd pdf_parser
make install
make run
```
This command sets up the environment and launches the Flask web server, ready for use.

## Storing PDFs for Processing

For privacy and organization, this application processes PDFs stored in a specific directory: `app/static/private/pdfs`. This directory is excluded from version control via `.gitignore` to ensure privacy and data security.


## Optional AI Integration

### Training the Model
For users interested in AI functionalities:
- Train the model with:
  ```bash
  make train
  ```

### Updating the Model
- Update the repository with the best model using:
  ```bash
  make model.pth
  ```
  This command enhances the application's AI capabilities by using the most effective model.

### Cleaning Up
Remove generated files and clean up:
```bash
make clean
```

## Project Structure
- `run.py`: Flask application entry point.
- `get_best_ckpt.py`: Script to generate `model.pth`.
- `Makefile`: Manages the build, run, and AI integration process.

## Contributing
Contributions are welcome. Please use standard fork-and-pull request workflow for any contributions.

## License
This project is licensed under the Apache License, Version 2.0 