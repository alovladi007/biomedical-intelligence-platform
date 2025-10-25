"""
Chest X-ray Classifier Training Pipeline
Trains DenseNet-121 on NIH ChestX-ray14 dataset

Dataset: https://nihcc.app.box.com/v/ChestXray-NIHCC
Papers: Wang et al. 2017, "ChestX-ray8: Hospital-scale Chest X-ray Database"
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from torchvision.models import densenet121
import pandas as pd
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, confusion_matrix
import os
import logging
from tqdm import tqdm
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChestXrayDataset(Dataset):
    """NIH ChestX-ray14 Dataset"""

    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert('RGB')

        if self.transform:
            image = self.transform(image)

        label = torch.tensor(self.labels[idx], dtype=torch.float32)

        return image, label


class ChestXrayTrainer:
    """Training pipeline for chest X-ray classifier"""

    PATHOLOGY_CLASSES = [
        'Atelectasis', 'Cardiomegaly', 'Effusion', 'Infiltration',
        'Mass', 'Nodule', 'Pneumonia', 'Pneumothorax',
        'Consolidation', 'Edema', 'Emphysema', 'Fibrosis',
        'Pleural_Thickening', 'Hernia'
    ]

    def __init__(
        self,
        data_dir: str,
        output_dir: str,
        batch_size: int = 32,
        num_epochs: int = 50,
        learning_rate: float = 1e-4,
        device: str = None
    ):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.learning_rate = learning_rate

        # Device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        logger.info(f"Using device: {self.device}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Transforms
        self.train_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        self.val_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def load_data(self, csv_path: str, train_split: float = 0.8):
        """Load NIH ChestX-ray14 dataset"""
        logger.info("Loading dataset...")

        # Load CSV with image labels
        df = pd.read_csv(csv_path)

        # Parse labels (multi-label classification)
        image_paths = []
        labels = []

        for idx, row in df.iterrows():
            image_path = os.path.join(self.data_dir, 'images', row['Image Index'])
            if os.path.exists(image_path):
                image_paths.append(image_path)

                # Parse finding labels
                finding_labels = row['Finding Labels'].split('|')
                label_vector = [1 if cls in finding_labels else 0 for cls in self.PATHOLOGY_CLASSES]
                labels.append(label_vector)

        # Train/val split
        train_paths, val_paths, train_labels, val_labels = train_test_split(
            image_paths, labels, train_size=train_split, random_state=42
        )

        logger.info(f"Training samples: {len(train_paths)}")
        logger.info(f"Validation samples: {len(val_paths)}")

        # Create datasets
        train_dataset = ChestXrayDataset(train_paths, train_labels, self.train_transform)
        val_dataset = ChestXrayDataset(val_paths, val_labels, self.val_transform)

        # Create dataloaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=True
        )

        return train_loader, val_loader

    def build_model(self):
        """Build DenseNet-121 model"""
        model = densenet121(pretrained=True)

        # Replace classifier for multi-label classification
        num_features = model.classifier.in_features
        model.classifier = nn.Linear(num_features, len(self.PATHOLOGY_CLASSES))

        model = model.to(self.device)

        return model

    def train_epoch(self, model, train_loader, criterion, optimizer):
        """Train for one epoch"""
        model.train()
        total_loss = 0.0

        for images, labels in tqdm(train_loader, desc="Training"):
            images = images.to(self.device)
            labels = labels.to(self.device)

            # Forward pass
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)

            # Backward pass
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        return avg_loss

    def validate(self, model, val_loader, criterion):
        """Validate model"""
        model.eval()
        total_loss = 0.0
        all_labels = []
        all_predictions = []

        with torch.no_grad():
            for images, labels in tqdm(val_loader, desc="Validation"):
                images = images.to(self.device)
                labels = labels.to(self.device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                total_loss += loss.item()

                # Sigmoid for probabilities
                probs = torch.sigmoid(outputs)

                all_labels.append(labels.cpu().numpy())
                all_predictions.append(probs.cpu().numpy())

        avg_loss = total_loss / len(val_loader)

        # Concatenate all batches
        all_labels = np.vstack(all_labels)
        all_predictions = np.vstack(all_predictions)

        # Calculate AUC-ROC per class
        auc_scores = []
        for i in range(len(self.PATHOLOGY_CLASSES)):
            try:
                auc = roc_auc_score(all_labels[:, i], all_predictions[:, i])
                auc_scores.append(auc)
            except:
                auc_scores.append(0.0)

        mean_auc = np.mean(auc_scores)

        return avg_loss, mean_auc, auc_scores

    def train(self, csv_path: str):
        """Full training pipeline"""
        logger.info("="*60)
        logger.info("Chest X-ray Classifier Training")
        logger.info("="*60)

        # Load data
        train_loader, val_loader = self.load_data(csv_path)

        # Build model
        model = self.build_model()

        # Loss and optimizer
        criterion = nn.BCEWithLogitsLoss()
        optimizer = optim.Adam(model.parameters(), lr=self.learning_rate)

        # Learning rate scheduler
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='max', patience=5, factor=0.5
        )

        # Training loop
        best_auc = 0.0
        training_history = []

        for epoch in range(self.num_epochs):
            logger.info(f"\nEpoch {epoch+1}/{self.num_epochs}")

            # Train
            train_loss = self.train_epoch(model, train_loader, criterion, optimizer)

            # Validate
            val_loss, mean_auc, auc_scores = self.validate(model, val_loader, criterion)

            # Log metrics
            logger.info(f"Train Loss: {train_loss:.4f}")
            logger.info(f"Val Loss: {val_loss:.4f}")
            logger.info(f"Mean AUC-ROC: {mean_auc:.4f}")

            # Per-class AUC
            for i, pathology in enumerate(self.PATHOLOGY_CLASSES):
                logger.info(f"  {pathology}: {auc_scores[i]:.4f}")

            # Save history
            training_history.append({
                'epoch': epoch + 1,
                'train_loss': train_loss,
                'val_loss': val_loss,
                'mean_auc': mean_auc,
                'per_class_auc': dict(zip(self.PATHOLOGY_CLASSES, auc_scores))
            })

            # Save best model
            if mean_auc > best_auc:
                best_auc = mean_auc
                model_path = os.path.join(self.output_dir, 'best_model.pth')
                torch.save(model.state_dict(), model_path)
                logger.info(f"✓ Saved best model (AUC: {best_auc:.4f})")

            # Learning rate scheduling
            scheduler.step(mean_auc)

            # Save checkpoint
            checkpoint_path = os.path.join(self.output_dir, f'checkpoint_epoch_{epoch+1}.pth')
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'mean_auc': mean_auc,
            }, checkpoint_path)

        # Save training history
        history_path = os.path.join(self.output_dir, 'training_history.json')
        with open(history_path, 'w') as f:
            json.dump(training_history, f, indent=2)

        logger.info("\n" + "="*60)
        logger.info(f"Training Complete! Best AUC: {best_auc:.4f}")
        logger.info("="*60)

        return model, training_history


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train Chest X-ray Classifier")
    parser.add_argument("--data_dir", required=True, help="Path to NIH ChestX-ray14 dataset")
    parser.add_argument("--csv_path", required=True, help="Path to Data_Entry_2017.csv")
    parser.add_argument("--output_dir", default="./models/chest_xray", help="Output directory")
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--num_epochs", type=int, default=50)
    parser.add_argument("--learning_rate", type=float, default=1e-4)

    args = parser.parse_args()

    trainer = ChestXrayTrainer(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        num_epochs=args.num_epochs,
        learning_rate=args.learning_rate
    )

    trainer.train(args.csv_path)
