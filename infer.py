import os
from app import IMGS_DIR
import flor
import torch
from PIL import Image


def parse_page(filename):
    fn, _ = os.path.splitext(filename)
    return int(fn.replace("page_", ""))


def list_files_in_directory(directory, key=None):
    if key:
        return sorted(os.listdir(directory), key=key)
    else:
        return sorted(os.listdir(directory))


def is_directory(path):
    return os.path.isdir(path)


def get_full_path(directory, file):
    return os.path.join(os.path.abspath(directory), file)


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
        # Loop through all files in directory
        for file in flor.loop("docs", list_files_in_directory(IMGS_DIR)):
            full_path = get_full_path(IMGS_DIR, file)
            if not is_directory(full_path):
                continue
            for i, file2 in flor.loop(
                "pages", enumerate(list_files_in_directory(full_path, key=parse_page))
            ):
                image_path = os.path.join(full_path, file2)
                flor.log("page_path", image_path)
                if model:
                    print("Predicting...")
                    image = Image.open(image_path)
                    input_tensor = transform(image).unsqueeze(0).to(device)  # type: ignore
                    with torch.no_grad():
                        output = model(input_tensor)
                        _, predicted = torch.max(output.data, 1)
                        predicted_label = predicted.item()
                        print(predicted_label)
                    flor.log("first_page", 1 if i == 0 else int(predicted_label))
                else:
                    print("Defaulting...")
                    flor.log("first_page", 1 if i == 0 else 0)
