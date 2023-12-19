import os
from app import IMGS_DIR
import flor
import torch
from PIL import Image

if __name__ == "__main__":
    from constants import device
    from train import model, transform

    device = torch.device(flor.arg("device", device))

    if os.path.exists("model.pth"):
        # Load model
        state_dict = torch.load("model.pth", map_location=device)
        model.load_state_dict(state_dict)

    model = model.to(device)
    model.eval()

    if os.path.exists(IMGS_DIR):
        imgs_dir = [
            os.path.join(os.path.abspath(IMGS_DIR), fn) for fn in os.listdir(IMGS_DIR)
        ]
        imgs_dir = [fp for fp in imgs_dir if os.path.isdir(fp)]
        for abs_path in flor.loop("document", sorted(imgs_dir)):
            pages_dir = [os.path.join(abs_path, pn) for pn in os.listdir(abs_path)]
            pages_dir = sorted(
                pages_dir,
                key=lambda fn: int((os.path.splitext(fn)[0]).replace("page_", "")),
            )
            for i, image_path in flor.loop("page", enumerate(pages_dir)):
                print("Predicting...")
                flor.log("page_path", image_path)
                image = Image.open(image_path)
                input_tensor = transform(image).unsqueeze(0).to(device)  # type: ignore
                # TODO: inference in batches
                with torch.no_grad():
                    output = model(input_tensor)
                    _, predicted = torch.max(output.data, 1)
                    predicted_label = predicted.item()
                flor.log("first_page", 1 if i == 0 else int(predicted_label))
