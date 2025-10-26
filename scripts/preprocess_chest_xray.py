"""
NIH ChestX-ray14 Preprocessing Pipeline

This script preprocesses the NIH ChestX-ray14 dataset for model training:
1. Load metadata and images
2. Normalize pixel values
3. Resize to target dimensions
4. Apply data augmentation
5. Split into train/val/test sets
6. Save processed data

Usage:
    python preprocess_chest_xray.py --data_dir data/raw/chest-xray \
                                     --output_dir data/processed/chest-xray \
                                     --image_size 224 \
                                     --augment
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import logging
from typing import Tuple, List, Dict
import json

# Image processing
try:
    from PIL import Image
    import cv2
except ImportError:
    print("Error: Required packages not installed")
    print("Install with: pip install pillow opencv-python pandas tqdm")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChestXrayPreprocessor:
    """Preprocessor for NIH ChestX-ray14 dataset"""

    # 14 disease labels
    DISEASE_LABELS = [
        'Atelectasis', 'Cardiomegaly', 'Effusion', 'Infiltration',
        'Mass', 'Nodule', 'Pneumonia', 'Pneumothorax',
        'Consolidation', 'Edema', 'Emphysema', 'Fibrosis',
        'Pleural_Thickening', 'Hernia'
    ]

    def __init__(self, data_dir: str, output_dir: str, image_size: int = 224):
        """
        Initialize preprocessor

        Args:
            data_dir: Path to raw data directory
            output_dir: Path to output processed data
            image_size: Target image size (default: 224x224)
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.image_size = image_size

        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'train').mkdir(exist_ok=True)
        (self.output_dir / 'val').mkdir(exist_ok=True)
        (self.output_dir / 'test').mkdir(exist_ok=True)

        # Load metadata
        self.metadata_df = None
        self.bbox_df = None

    def load_metadata(self):
        """Load dataset metadata"""
        logger.info("Loading metadata...")

        metadata_path = self.data_dir / 'Data_Entry_2017.csv'
        bbox_path = self.data_dir / 'BBox_List_2017.csv'

        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")

        self.metadata_df = pd.read_csv(metadata_path)
        logger.info(f"Loaded {len(self.metadata_df)} image records")

        if bbox_path.exists():
            self.bbox_df = pd.read_csv(bbox_path)
            logger.info(f"Loaded {len(self.bbox_df)} bounding box annotations")

        # Parse labels
        self.metadata_df['labels'] = self.metadata_df['Finding Labels'].apply(
            lambda x: x.split('|') if x != 'No Finding' else ['No Finding']
        )

        # Create binary label columns
        for label in self.DISEASE_LABELS:
            self.metadata_df[label] = self.metadata_df['labels'].apply(
                lambda x: 1 if label in x else 0
            )

        logger.info("Metadata loaded successfully")

    def normalize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize image to [0, 1] range

        Args:
            image: Input image array

        Returns:
            Normalized image
        """
        image = image.astype(np.float32)
        image = (image - image.min()) / (image.max() - image.min() + 1e-8)
        return image

    def resize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Resize image to target size

        Args:
            image: Input image array

        Returns:
            Resized image
        """
        return cv2.resize(image, (self.image_size, self.image_size))

    def augment_image(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Apply data augmentation

        Args:
            image: Input image array

        Returns:
            List of augmented images
        """
        augmented = [image]  # Original

        # Horizontal flip
        augmented.append(cv2.flip(image, 1))

        # Rotation (small angles)
        for angle in [-10, 10]:
            M = cv2.getRotationMatrix2D(
                (self.image_size // 2, self.image_size // 2),
                angle,
                1.0
            )
            rotated = cv2.warpAffine(image, M, (self.image_size, self.image_size))
            augmented.append(rotated)

        # Brightness adjustment
        for factor in [0.9, 1.1]:
            adjusted = np.clip(image * factor, 0, 1)
            augmented.append(adjusted)

        return augmented

    def process_image(
        self,
        image_path: Path,
        augment: bool = False
    ) -> Tuple[List[np.ndarray], bool]:
        """
        Process single image

        Args:
            image_path: Path to image file
            augment: Whether to apply augmentation

        Returns:
            Tuple of (processed images list, success flag)
        """
        try:
            # Load image
            image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

            if image is None:
                logger.warning(f"Failed to load image: {image_path}")
                return [], False

            # Resize
            image = self.resize_image(image)

            # Normalize
            image = self.normalize_image(image)

            # Augment
            if augment:
                images = self.augment_image(image)
            else:
                images = [image]

            return images, True

        except Exception as e:
            logger.error(f"Error processing {image_path}: {str(e)}")
            return [], False

    def split_dataset(
        self,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15
    ) -> Dict[str, pd.DataFrame]:
        """
        Split dataset into train/val/test

        Args:
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio

        Returns:
            Dictionary with train/val/test DataFrames
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
            "Ratios must sum to 1.0"

        # Shuffle dataset
        df = self.metadata_df.sample(frac=1, random_state=42).reset_index(drop=True)

        # Calculate split indices
        n = len(df)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)

        splits = {
            'train': df[:train_end],
            'val': df[train_end:val_end],
            'test': df[val_end:]
        }

        logger.info(f"Dataset split: train={len(splits['train'])}, "
                   f"val={len(splits['val'])}, test={len(splits['test'])}")

        return splits

    def process_dataset(
        self,
        augment_train: bool = True,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15
    ):
        """
        Process entire dataset

        Args:
            augment_train: Whether to augment training data
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
        """
        # Load metadata
        self.load_metadata()

        # Split dataset
        splits = self.split_dataset(train_ratio, val_ratio, test_ratio)

        # Process each split
        for split_name, split_df in splits.items():
            logger.info(f"Processing {split_name} set...")

            augment = augment_train and (split_name == 'train')

            processed_count = 0
            failed_count = 0

            for idx, row in tqdm(split_df.iterrows(), total=len(split_df)):
                image_name = row['Image Index']
                image_path = self.data_dir / 'images' / image_name

                if not image_path.exists():
                    logger.warning(f"Image not found: {image_path}")
                    failed_count += 1
                    continue

                # Process image
                images, success = self.process_image(image_path, augment)

                if not success:
                    failed_count += 1
                    continue

                # Save processed images
                for i, img in enumerate(images):
                    suffix = f"_aug{i}" if i > 0 else ""
                    output_path = self.output_dir / split_name / f"{image_name.replace('.png', '')}{suffix}.npy"
                    np.save(output_path, img)

                processed_count += 1

            logger.info(f"{split_name}: Processed {processed_count} images, "
                       f"Failed {failed_count}")

            # Save split metadata
            metadata_path = self.output_dir / split_name / 'metadata.csv'
            split_df.to_csv(metadata_path, index=False)

        # Save preprocessing config
        config = {
            'image_size': self.image_size,
            'disease_labels': self.DISEASE_LABELS,
            'train_ratio': train_ratio,
            'val_ratio': val_ratio,
            'test_ratio': test_ratio,
            'augment_train': augment_train
        }

        config_path = self.output_dir / 'preprocessing_config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info(f"Preprocessing complete! Config saved to {config_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess NIH ChestX-ray14 dataset"
    )
    parser.add_argument(
        '--data_dir',
        type=str,
        default='data/raw/chest-xray',
        help='Path to raw data directory'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        default='data/processed/chest-xray',
        help='Path to output directory'
    )
    parser.add_argument(
        '--image_size',
        type=int,
        default=224,
        help='Target image size (default: 224)'
    )
    parser.add_argument(
        '--augment',
        action='store_true',
        help='Apply data augmentation to training set'
    )
    parser.add_argument(
        '--train_ratio',
        type=float,
        default=0.7,
        help='Training set ratio (default: 0.7)'
    )
    parser.add_argument(
        '--val_ratio',
        type=float,
        default=0.15,
        help='Validation set ratio (default: 0.15)'
    )
    parser.add_argument(
        '--test_ratio',
        type=float,
        default=0.15,
        help='Test set ratio (default: 0.15)'
    )

    args = parser.parse_args()

    # Create preprocessor
    preprocessor = ChestXrayPreprocessor(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        image_size=args.image_size
    )

    # Process dataset
    preprocessor.process_dataset(
        augment_train=args.augment,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio
    )

    logger.info("All done!")


if __name__ == '__main__':
    main()
