"""
Chest X-ray Pathology Classification Service
Uses DenseNet-121 for multi-label classification of chest X-ray pathologies
Based on NIH ChestX-ray14 dataset (14 pathology classes)
"""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import densenet121
from PIL import Image
import numpy as np
from typing import Dict, List, Tuple
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChestXrayClassifier:
    """
    Multi-label chest X-ray pathology classifier

    Pathologies (14 classes from NIH ChestX-ray14):
    - Atelectasis, Cardiomegaly, Effusion, Infiltration
    - Mass, Nodule, Pneumonia, Pneumothorax
    - Consolidation, Edema, Emphysema, Fibrosis
    - Pleural_Thickening, Hernia
    """

    PATHOLOGY_CLASSES = [
        'Atelectasis', 'Cardiomegaly', 'Effusion', 'Infiltration',
        'Mass', 'Nodule', 'Pneumonia', 'Pneumothorax',
        'Consolidation', 'Edema', 'Emphysema', 'Fibrosis',
        'Pleural_Thickening', 'Hernia'
    ]

    def __init__(self, model_path: str = None, device: str = None):
        """
        Initialize chest X-ray classifier

        Args:
            model_path: Path to pre-trained model weights
            device: 'cuda', 'mps', or 'cpu'
        """
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device('cuda')
            elif torch.backends.mps.is_available():
                self.device = torch.device('mps')
            else:
                self.device = torch.device('cpu')
        else:
            self.device = torch.device(device)

        logger.info(f"Using device: {self.device}")

        # Build model
        self.model = self._build_model()

        # Load pre-trained weights if provided
        if model_path:
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                logger.info(f"Loaded model weights from {model_path}")
            except FileNotFoundError:
                logger.warning(f"Model weights not found at {model_path}, using untrained model")

        self.model.to(self.device)
        self.model.eval()

        # Image preprocessing transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.Grayscale(num_output_channels=3),  # Convert grayscale to 3-channel
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _build_model(self) -> nn.Module:
        """Build DenseNet-121 model for multi-label classification"""
        model = densenet121(pretrained=True)

        # Replace final layer for 14-class multi-label classification
        num_features = model.classifier.in_features
        model.classifier = nn.Linear(num_features, len(self.PATHOLOGY_CLASSES))

        return model

    def preprocess_image(self, image_data: bytes) -> torch.Tensor:
        """
        Preprocess chest X-ray image

        Args:
            image_data: Raw image bytes (JPEG, PNG, DICOM)

        Returns:
            Preprocessed image tensor
        """
        # Load image
        image = Image.open(io.BytesIO(image_data))

        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Apply transforms
        image_tensor = self.transform(image)

        # Add batch dimension
        image_tensor = image_tensor.unsqueeze(0)

        return image_tensor

    def predict(self, image_data: bytes, threshold: float = 0.5) -> Dict:
        """
        Predict pathologies from chest X-ray image

        Args:
            image_data: Raw image bytes
            threshold: Probability threshold for positive prediction (default: 0.5)

        Returns:
            Dictionary with predictions and metadata
        """
        try:
            # Preprocess image
            image_tensor = self.preprocess_image(image_data)
            image_tensor = image_tensor.to(self.device)

            # Inference
            with torch.no_grad():
                logits = self.model(image_tensor)
                probabilities = torch.sigmoid(logits)

            # Move to CPU and convert to numpy
            probs = probabilities.cpu().numpy()[0]

            # Extract predictions
            predictions = []
            for i, pathology in enumerate(self.PATHOLOGY_CLASSES):
                prob = float(probs[i])
                if prob >= threshold:
                    predictions.append({
                        'pathology': pathology,
                        'probability': prob,
                        'confidence': 'high' if prob >= 0.8 else 'medium' if prob >= 0.6 else 'low'
                    })

            # Sort by probability
            predictions = sorted(predictions, key=lambda x: x['probability'], reverse=True)

            # Calculate overall risk score
            risk_score = self._calculate_risk_score(probs)

            return {
                'predictions': predictions,
                'all_probabilities': {
                    pathology: float(probs[i])
                    for i, pathology in enumerate(self.PATHOLOGY_CLASSES)
                },
                'risk_score': risk_score,
                'num_findings': len(predictions),
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def _calculate_risk_score(self, probabilities: np.ndarray) -> Dict:
        """
        Calculate overall risk score based on detected pathologies

        Critical pathologies (higher weight):
        - Pneumonia, Pneumothorax, Edema, Consolidation

        Moderate pathologies:
        - Mass, Nodule, Effusion, Cardiomegaly

        Mild pathologies:
        - Others
        """
        critical_indices = [6, 7, 9, 8]  # Pneumonia, Pneumothorax, Edema, Consolidation
        moderate_indices = [4, 5, 2, 1]  # Mass, Nodule, Effusion, Cardiomegaly

        critical_score = np.max(probabilities[critical_indices]) if critical_indices else 0.0
        moderate_score = np.max(probabilities[moderate_indices]) if moderate_indices else 0.0
        overall_max = np.max(probabilities)

        # Weighted risk score
        risk = (critical_score * 3.0 + moderate_score * 1.5 + overall_max) / 5.5

        # Categorize risk
        if risk >= 0.7:
            category = 'high'
            recommendation = 'Immediate radiologist review recommended'
        elif risk >= 0.4:
            category = 'moderate'
            recommendation = 'Radiologist review recommended within 24 hours'
        else:
            category = 'low'
            recommendation = 'Routine follow-up'

        return {
            'score': float(risk),
            'category': category,
            'recommendation': recommendation
        }

    def batch_predict(self, image_data_list: List[bytes], threshold: float = 0.5) -> List[Dict]:
        """
        Batch prediction for multiple images

        Args:
            image_data_list: List of raw image bytes
            threshold: Probability threshold

        Returns:
            List of prediction dictionaries
        """
        results = []
        for image_data in image_data_list:
            result = self.predict(image_data, threshold)
            results.append(result)

        return results


# Training utilities (for future model fine-tuning)
class ChestXrayTrainer:
    """Trainer for fine-tuning chest X-ray classifier"""

    def __init__(self, model: nn.Module, device: torch.device):
        self.model = model
        self.device = device
        self.criterion = nn.BCEWithLogitsLoss()
        self.optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

    def train_epoch(self, dataloader) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0

        for batch_idx, (images, labels) in enumerate(dataloader):
            images = images.to(self.device)
            labels = labels.to(self.device)

            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)

            # Backward pass
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(dataloader)

    def evaluate(self, dataloader) -> Dict:
        """Evaluate model on validation set"""
        self.model.eval()
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for images, labels in dataloader:
                images = images.to(self.device)
                outputs = self.model(images)
                probs = torch.sigmoid(outputs)

                all_preds.append(probs.cpu().numpy())
                all_labels.append(labels.cpu().numpy())

        all_preds = np.vstack(all_preds)
        all_labels = np.vstack(all_labels)

        # Calculate metrics (AUC-ROC, etc.)
        from sklearn.metrics import roc_auc_score

        auc_scores = []
        for i in range(all_labels.shape[1]):
            try:
                auc = roc_auc_score(all_labels[:, i], all_preds[:, i])
                auc_scores.append(auc)
            except:
                auc_scores.append(0.0)

        return {
            'mean_auc': np.mean(auc_scores),
            'per_class_auc': auc_scores
        }


if __name__ == "__main__":
    # Demo usage
    classifier = ChestXrayClassifier()
    print("Chest X-ray Classifier initialized")
    print(f"Device: {classifier.device}")
    print(f"Number of pathology classes: {len(classifier.PATHOLOGY_CLASSES)}")
    print(f"Classes: {classifier.PATHOLOGY_CLASSES}")
