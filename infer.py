import os
from app import IMGS_DIR
import flor
import torch
from PIL import Image

if __name__ == "__main__":
    from app.config import device, page_path, first_page
    from train import model, transform

    # Set the device for running the model
    device = torch.device(flor.arg("device", device))

    # Check if the model file exists and load it
    if os.path.exists("model.pth"):
        # Load the saved model state
        state_dict = torch.load("model.pth", map_location=device)
        model.load_state_dict(state_dict)

    # Check if the directory with images exists
    if os.path.exists(IMGS_DIR):
        # Preparing the model for inference
        model = model.to(device)
        model.eval()
        # Construct a list of directories in IMGS_DIR
        imgs_dir = [
            os.path.join(os.path.abspath(IMGS_DIR), fn) for fn in os.listdir(IMGS_DIR)
        ]
        # Filter to retain only directories
        imgs_dir = [fp for fp in imgs_dir if os.path.isdir(fp)]
        # Iterate over each directory for inference
        for abs_path in flor.loop("document", sorted(imgs_dir)):
            # Process each page within the directory
            pages_dir = [os.path.join(abs_path, pn) for pn in os.listdir(abs_path)]
            # Sort the pages to maintain the correct order
            pages_dir = sorted(
                pages_dir,
                key=lambda fn: int(
                    (os.path.splitext(os.path.basename(fn))[0]).replace("page_", "")
                ),
            )
            for i, image_path in flor.loop("page", enumerate(pages_dir)):
                flor.log(page_path, image_path)  # Logging the path of each image/page
                # Open the image and apply transformations
                image = Image.open(image_path)
                # Convert image to tensor
                input_tensor = transform(image).unsqueeze(0).to(device)  # type: ignore
                # TODO: inference in batches
                # Perform inference on the image
                with torch.no_grad():
                    output = model(input_tensor)
                    logits, predicted = torch.max(
                        output.data, 1
                    )  # Obtain the most likely prediction
                    predicted_label = (
                        predicted.item()
                    )  # Extract the predicted label (integer index)
                # Log the predicted label, with special handling for the first page
                flor.log(first_page, 1 if i == 0 else int(predicted_label))
