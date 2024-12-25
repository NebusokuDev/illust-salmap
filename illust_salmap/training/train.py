from typing import cast

import torch
from pytorch_lightning import LightningDataModule
from torch import Tensor
from torch.nn import Module
from torch.optim import Optimizer
from torch.utils.data import DataLoader
from tqdm import tqdm


def train(model: Module, criterion: Module, dataloader: DataLoader, optimizer: Optimizer, device) -> dict:
    model.train()
    epoch_loss = 0.0
    for batch_idx, batch in enumerate(tqdm(dataloader, desc="Training")):
        image, ground_truth = cast(tuple[Tensor, Tensor], batch)
        image, ground_truth = image.to(device), ground_truth.to(device)

        optimizer.zero_grad()
        predict = model(image)
        loss = criterion(predict, ground_truth)
        epoch_loss += loss.item()

        loss.backward()
        optimizer.step()

    return {"loss": epoch_loss / len(dataloader)}


@torch.no_grad()
def validation(model: Module, criterion: Module, dataloader: DataLoader, device) -> dict:
    model.eval()
    epoch_loss = 0.0
    for batch_idx, batch in enumerate(tqdm(dataloader, desc="Validation")):
        image, ground_truth = cast(tuple[Tensor, Tensor], batch)
        image, ground_truth = image.to(device), ground_truth.to(device)
        predict = model(image)
        loss = criterion(predict, ground_truth)
        epoch_loss += loss.item()

    return {"loss": epoch_loss / len(dataloader)}


@torch.no_grad()
def visualize(model, dataloader, device):
    image, ground_truth = next(iter(dataloader))
    image, ground_truth = image.to(device), ground_truth.to(device)
    predict = model(image)


@torch.no_grad()
def test(model: Module, criterion: Module, dataloader: DataLoader, device="cuda") -> dict:
    model.to(device)
    model.eval()
    epoch_loss = 0.0

    for batch_idx, batch in enumerate(tqdm(dataloader, desc="Testing")):
        image, ground_truth = cast(tuple[Tensor, Tensor], batch)
        image, ground_truth = image.to(device), ground_truth.to(device)
        predict = model(image)
        loss = criterion(predict, ground_truth)
        epoch_loss += loss.item()

    return {"loss": epoch_loss / len(dataloader)}


def fit(model: Module, criterion: Module, datamodule: LightningDataModule, optimizer: Optimizer, epochs: int = 100,
        device="cuda"):
    datamodule.prepare_data()
    datamodule.setup("fit")

    for epoch in range(epochs):
        print(f"Epoch {epoch + 1}/{epochs}")
        print("-" * 100)

        train_metrics = train(model, criterion, datamodule.train_dataloader(), optimizer, device)
        val_metrics = validation(model, criterion, datamodule.val_dataloader(), device)
        visualize(model, datamodule.val_dataloader(), device)

        print(f"Training Loss: {train_metrics['loss']:.4f}")
        print(f"Validation Loss: {val_metrics['loss']:.4f}")
