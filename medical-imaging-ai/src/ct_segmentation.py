"""
CT Segmentation Service
Uses 3D U-Net for multi-organ segmentation in CT scans
Segments: Liver, Kidney (L/R), Spleen, Pancreas
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Optional
import nibabel as nib
import logging
from scipy import ndimage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UNet3D(nn.Module):
    """3D U-Net for CT organ segmentation"""

    def __init__(self, in_channels=1, num_classes=6):
        """
        Args:
            in_channels: Input channels (1 for CT)
            num_classes: Number of segmentation classes (background + 5 organs)
        """
        super(UNet3D, self).__init__()

        # Encoder (downsampling)
        self.enc1 = self._conv_block(in_channels, 16)
        self.enc2 = self._conv_block(16, 32)
        self.enc3 = self._conv_block(32, 64)
        self.enc4 = self._conv_block(64, 128)

        # Bottleneck
        self.bottleneck = self._conv_block(128, 256)

        # Decoder (upsampling)
        self.upconv4 = nn.ConvTranspose3d(256, 128, kernel_size=2, stride=2)
        self.dec4 = self._conv_block(256, 128)

        self.upconv3 = nn.ConvTranspose3d(128, 64, kernel_size=2, stride=2)
        self.dec3 = self._conv_block(128, 64)

        self.upconv2 = nn.ConvTranspose3d(64, 32, kernel_size=2, stride=2)
        self.dec2 = self._conv_block(64, 32)

        self.upconv1 = nn.ConvTranspose3d(32, 16, kernel_size=2, stride=2)
        self.dec1 = self._conv_block(32, 16)

        # Output layer
        self.out_conv = nn.Conv3d(16, num_classes, kernel_size=1)

        # Pooling
        self.pool = nn.MaxPool3d(kernel_size=2, stride=2)

    def _conv_block(self, in_channels, out_channels):
        """3D convolutional block with batch norm and ReLU"""
        return nn.Sequential(
            nn.Conv3d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv3d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        # Encoder
        enc1 = self.enc1(x)
        enc2 = self.enc2(self.pool(enc1))
        enc3 = self.enc3(self.pool(enc2))
        enc4 = self.enc4(self.pool(enc3))

        # Bottleneck
        bottleneck = self.bottleneck(self.pool(enc4))

        # Decoder with skip connections
        dec4 = self.upconv4(bottleneck)
        dec4 = torch.cat([dec4, enc4], dim=1)
        dec4 = self.dec4(dec4)

        dec3 = self.upconv3(dec4)
        dec3 = torch.cat([dec3, enc3], dim=1)
        dec3 = self.dec3(dec3)

        dec2 = self.upconv2(dec3)
        dec2 = torch.cat([dec2, enc2], dim=1)
        dec2 = self.dec2(dec2)

        dec1 = self.upconv1(dec2)
        dec1 = torch.cat([dec1, enc1], dim=1)
        dec1 = self.dec1(dec1)

        # Output
        out = self.out_conv(dec1)

        return out


class CTSegmentationService:
    """
    CT organ segmentation service

    Organs (6 classes):
    0: Background
    1: Liver
    2: Right Kidney
    3: Left Kidney
    4: Spleen
    5: Pancreas
    """

    ORGAN_CLASSES = {
        0: 'Background',
        1: 'Liver',
        2: 'Right Kidney',
        3: 'Left Kidney',
        4: 'Spleen',
        5: 'Pancreas'
    }

    # Normal organ volume ranges (in mL)
    NORMAL_VOLUME_RANGES = {
        'Liver': (1200, 1800),
        'Right Kidney': (120, 200),
        'Left Kidney': (120, 200),
        'Spleen': (100, 250),
        'Pancreas': (50, 100)
    }

    def __init__(self, model_path: str = None, device: str = None):
        """
        Initialize CT segmentation service

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
        self.model = UNet3D(in_channels=1, num_classes=len(self.ORGAN_CLASSES))

        # Load pre-trained weights if provided
        if model_path:
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                logger.info(f"Loaded model weights from {model_path}")
            except FileNotFoundError:
                logger.warning(f"Model weights not found at {model_path}, using untrained model")

        self.model.to(self.device)
        self.model.eval()

    def preprocess_ct(self, ct_volume: np.ndarray) -> torch.Tensor:
        """
        Preprocess CT volume

        Args:
            ct_volume: 3D numpy array (D, H, W)

        Returns:
            Preprocessed tensor (1, 1, D, H, W)
        """
        # Normalize to [-1, 1] using CT window
        ct_volume = np.clip(ct_volume, -200, 300)  # Soft tissue window
        ct_volume = (ct_volume - 50) / 250.0

        # Convert to tensor
        ct_tensor = torch.from_numpy(ct_volume).float()

        # Add batch and channel dimensions
        ct_tensor = ct_tensor.unsqueeze(0).unsqueeze(0)

        return ct_tensor

    def segment(self, ct_volume: np.ndarray, spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)) -> Dict:
        """
        Segment organs in CT volume

        Args:
            ct_volume: 3D numpy array (D, H, W) with CT intensity values
            spacing: Voxel spacing (z, y, x) in mm

        Returns:
            Dictionary with segmentation masks and analysis
        """
        try:
            # Preprocess
            ct_tensor = self.preprocess_ct(ct_volume)
            ct_tensor = ct_tensor.to(self.device)

            # Inference
            with torch.no_grad():
                logits = self.model(ct_tensor)
                probs = torch.softmax(logits, dim=1)
                segmentation = torch.argmax(probs, dim=1)

            # Move to CPU and convert to numpy
            seg_mask = segmentation.cpu().numpy()[0]
            probs_np = probs.cpu().numpy()[0]

            # Analyze segmentation
            analysis = self._analyze_segmentation(seg_mask, spacing)

            # Generate visualization coordinates (for 3D rendering)
            organ_contours = self._extract_contours(seg_mask)

            return {
                'segmentation_mask': seg_mask.tolist(),
                'probabilities': {
                    organ: float(probs_np[i].max())
                    for i, organ in self.ORGAN_CLASSES.items()
                },
                'analysis': analysis,
                'organ_contours': organ_contours,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Segmentation error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def _analyze_segmentation(self, seg_mask: np.ndarray, spacing: Tuple[float, float, float]) -> Dict:
        """
        Analyze segmentation results

        Calculate:
        - Organ volumes
        - Abnormality detection (volume outside normal range)
        - Organ locations (centroids)
        """
        voxel_volume = spacing[0] * spacing[1] * spacing[2] / 1000.0  # Convert mm³ to mL

        analysis = {}

        for organ_id, organ_name in self.ORGAN_CLASSES.items():
            if organ_id == 0:  # Skip background
                continue

            # Extract organ mask
            organ_mask = (seg_mask == organ_id)
            voxel_count = np.sum(organ_mask)

            if voxel_count == 0:
                analysis[organ_name] = {
                    'detected': False,
                    'volume_ml': 0.0,
                    'status': 'not_detected'
                }
                continue

            # Calculate volume
            volume_ml = voxel_count * voxel_volume

            # Check if volume is in normal range
            normal_range = self.NORMAL_VOLUME_RANGES.get(organ_name)
            if normal_range:
                min_vol, max_vol = normal_range
                if volume_ml < min_vol:
                    status = 'abnormal_small'
                    alert = f"Volume ({volume_ml:.1f} mL) below normal range ({min_vol}-{max_vol} mL)"
                elif volume_ml > max_vol:
                    status = 'abnormal_large'
                    alert = f"Volume ({volume_ml:.1f} mL) above normal range ({min_vol}-{max_vol} mL)"
                else:
                    status = 'normal'
                    alert = None
            else:
                status = 'unknown'
                alert = None

            # Calculate centroid
            centroid = ndimage.center_of_mass(organ_mask)

            analysis[organ_name] = {
                'detected': True,
                'volume_ml': float(volume_ml),
                'voxel_count': int(voxel_count),
                'status': status,
                'alert': alert,
                'centroid': {
                    'z': float(centroid[0]),
                    'y': float(centroid[1]),
                    'x': float(centroid[2])
                }
            }

        return analysis

    def _extract_contours(self, seg_mask: np.ndarray, sample_rate: int = 5) -> Dict:
        """
        Extract organ contours for 3D visualization
        Sample slices to reduce data size

        Args:
            seg_mask: 3D segmentation mask
            sample_rate: Sample every Nth slice

        Returns:
            Dictionary with contour coordinates per organ
        """
        contours = {}

        for organ_id, organ_name in self.ORGAN_CLASSES.items():
            if organ_id == 0:  # Skip background
                continue

            organ_mask = (seg_mask == organ_id)

            # Sample slices
            slice_indices = range(0, seg_mask.shape[0], sample_rate)
            organ_contours = []

            for z in slice_indices:
                slice_mask = organ_mask[z, :, :]
                if np.any(slice_mask):
                    # Find boundaries (simplified - just get coordinates)
                    coords = np.argwhere(slice_mask)
                    if len(coords) > 0:
                        organ_contours.append({
                            'z': int(z),
                            'points': coords.tolist()[:100]  # Limit points for API response
                        })

            contours[organ_name] = organ_contours

        return contours

    def save_segmentation(self, seg_mask: np.ndarray, output_path: str, affine: np.ndarray = None):
        """
        Save segmentation mask as NIfTI file

        Args:
            seg_mask: 3D segmentation mask
            output_path: Output file path (.nii.gz)
            affine: Affine transformation matrix
        """
        if affine is None:
            affine = np.eye(4)

        nifti_img = nib.Nifti1Image(seg_mask.astype(np.uint8), affine)
        nib.save(nifti_img, output_path)
        logger.info(f"Segmentation saved to {output_path}")


# Dice coefficient for evaluation
def dice_coefficient(pred: np.ndarray, target: np.ndarray, organ_id: int) -> float:
    """
    Calculate Dice coefficient for specific organ

    Args:
        pred: Predicted segmentation mask
        target: Ground truth segmentation mask
        organ_id: Organ class ID

    Returns:
        Dice coefficient (0-1)
    """
    pred_mask = (pred == organ_id)
    target_mask = (target == organ_id)

    intersection = np.sum(pred_mask & target_mask)
    union = np.sum(pred_mask) + np.sum(target_mask)

    if union == 0:
        return 1.0 if intersection == 0 else 0.0

    dice = 2.0 * intersection / union
    return dice


if __name__ == "__main__":
    # Demo usage
    segmenter = CTSegmentationService()
    print("CT Segmentation Service initialized")
    print(f"Device: {segmenter.device}")
    print(f"Number of organ classes: {len(segmenter.ORGAN_CLASSES)}")
    print(f"Organs: {list(segmenter.ORGAN_CLASSES.values())}")

    # Demo with synthetic CT volume
    demo_ct = np.random.randn(64, 256, 256) * 100 + 50
    result = segmenter.segment(demo_ct, spacing=(2.5, 0.7, 0.7))
    print(f"\nDemo segmentation status: {result['status']}")
