import os
import time
import copy
import flor
import torch
import torch.optim as optim
from torch.optim import lr_scheduler
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import pandas as pd
from torchvision import transforms, models
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score


class PDFPagesDataset(Dataset):
    def __init__(self, dataframe, transform=None):
        """
        Args:
            dataframe (Pandas DataFrame): DataFrame with image paths and labels.
            transform (callable, optional): Optional transform to be applied on a sample.
        """
        self.dataframe = dataframe
        self.columns = [each for each in dataframe.columns.values]
        self.transform = transform

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        img_name = self.dataframe.iloc[
            idx, self.columns.index("page_path")
        ]  # adjust column index based on your DataFrame structure
        image = Image.open(img_name)
        label = int(
            self.dataframe.iloc[idx, self.columns.index("first_page")]
        )  # adjust column index for labels

        if self.transform:
            image = self.transform(image)

        return image, label
    
# Model
model = models.resnet18(pretrained=True)

# Modify the final layer of ResNet18 Model for our binary classification problem
num_ftrs = model.fc.in_features
model.fc = torch.nn.Linear(num_ftrs, 2)

# Move the model to GPU if available
device = flor.arg("device", "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
device = torch.device(device)
model = model.to(device)

# Freeze early layers of the model
for param in model.parameters():
    param.requires_grad = False

for param in model.fc.parameters():
    param.requires_grad = True
    
# Define your transformations
transform = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.RandomCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)

if __name__ == "__main__":

    training_data = flor.pivot("page_path", "first_page")
    training_data["page_path"] = training_data["page_path"].apply(os.path.relpath)
    training_data = training_data[training_data["filename"] == "infer.py"]
    training_data = training_data[training_data["tstamp"] == training_data["tstamp"].max()]
    # print(training_data.head(n=len(training_data)))

    test_size = flor.arg("test_size", 0.2)
    train_data, val_data = train_test_split(training_data, test_size=test_size)
    print(val_data.head(n=len(val_data)))



    train_dataset = PDFPagesDataset(dataframe=train_data, transform=transform)
    val_dataset = PDFPagesDataset(dataframe=val_data, transform=transform)

    # Data loaders
    batch_size = flor.arg("batch_size", 4)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    # Loss function and optimizer
    w = torch.tensor([1.0, 10.0]).to(device)
    criterion = nn.CrossEntropyLoss(weight=w)
    optimizer = optim.Adam(model.fc.parameters(), lr=flor.arg("lr", 0.001))
    exp_lr_scheduler = lr_scheduler.StepLR(
        optimizer, step_size=flor.arg("lr_step_size", 7), gamma=flor.arg("lr_gamma", 0.1)
    )

    num_epochs = flor.arg("num_epochs", 25)
    best_acc = 0.0
    with flor.checkpointing(
        model=model, optimizer=optimizer, lr_scheduler=exp_lr_scheduler
    ):
        # Training
        for epoch in flor.loop("epochs", range(num_epochs)):
            # Each epoch has a training and validation phase
            # do train
            model.train()
            running_loss = 0.0
            running_corrects = 0
            all_labels = []
            all_preds = []
            for inputs, labels in flor.loop("steps", train_loader):
                inputs = inputs.to(device)
                labels = labels.to(device)

                # Zero the parameter gradients
                optimizer.zero_grad()

                # Forward
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)

                # Backward + optimize
                loss.backward()
                optimizer.step()

                # Statistics
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

                all_labels.extend(labels.cpu().numpy())
                all_preds.extend(preds.cpu().numpy())


            epoch_loss = running_loss / len(train_dataset)
            flor.log("train_loss", float(epoch_loss))
            epoch_acc = running_corrects.float() / len(train_dataset)  # type: ignore
            flor.log("train_acc", float(epoch_acc))
            train_recall = recall_score(all_labels, all_preds)
            flor.log("train_recall", float(train_recall))

            # do validate
            model.eval()
            running_loss = 0.0
            running_corrects = 0
            all_labels = []
            all_preds = []

            # Iterate over data.
            for inputs, labels in val_loader:
                inputs = inputs.to(device)
                labels = labels.to(device)

                # Zero the parameter gradients
                optimizer.zero_grad()

                # Forward
                with torch.no_grad():
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                # Statistics
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
                all_labels.extend(labels.cpu().numpy())
                all_preds.extend(preds.cpu().numpy())


            epoch_loss = running_loss / len(val_dataset)
            flor.log("val_loss", float(epoch_loss))
            epoch_acc = running_corrects.float() / len(val_dataset)  # type: ignore
            flor.log("val_acc", float(epoch_acc))

            # Calculate recall at the end of the epoch
            val_recall = recall_score(all_labels, all_preds)
            flor.log("val_recall", float(val_recall))

            exp_lr_scheduler.step()
