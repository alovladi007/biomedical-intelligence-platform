"""
CT Scan Preprocessing Pipeline

This script preprocesses CT scans for segmentation tasks:
1. Load DICOM/NIfTI files
2. Normalize intensities (Hounsfield units)
3. Resize/resample to target spacing
4. Apply windowing
5. Extract 2D slices or 3D volumes
6. Save processed data

Usage:
    python preprocess_ct_scans.py --data_dir data/raw/ct-segmentation \
                                   --output_dir data/processed/ct-segmentation \
                                   --dataset kits19
"""

import os
import sys
import argparse
import numpy as np
from pathlib import Path
from tqdm import tqdm
import logging
from typing import Tuple, Optional
import json

# Medical imaging
try:
    import nibabel as nib
    import pydicom
    from scipy import ndimage
except ImportError:
    print("Error: Required packages not installed")
    print("Install with: pip install nibabel pydicom scipy")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CTScanPreprocessor:
    """Preprocessor for CT scans"""

    def __init__(
        self,
        data_dir: str,
        output_dir: str,
        target_spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    ):
        """
        Initialize preprocessor

        Args:
            data_dir: Path to raw data directory
            output_dir: Path to output processed data
            target_spacing: Target voxel spacing (mm) in (x, y, z)
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.target_spacing = target_spacing

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def normalize_hounsfield(
        self,
        image: np.ndarray,
        window_center: int = 40,
        window_width: int = 400
    ) -> np.ndarray:
        """
        Normalize CT image using Hounsfield units windowing

        Args:
            image: Input CT image
            window_center: Window center (HU)
            window_width: Window width (HU)

        Returns:
            Normalized image [0, 1]
        """
        min_hu = window_center - window_width // 2
        max_hu = window_center + window_width // 2

        # Clip values
        image = np.clip(image, min_hu, max_hu)

        # Normalize to [0, 1]
        image = (image - min_hu) / (max_hu - min_hu)

        return image.astype(np.float32)

    def resample_volume(
        self,
        volume: np.ndarray,
        original_spacing: Tuple[float, float, float]
    ) -> np.ndarray:
        """
        Resample volume to target spacing

        Args:
            volume: Input volume
            original_spacing: Original voxel spacing (mm)

        Returns:
            Resampled volume
        """
        # Calculate resize factors
        resize_factor = np.array(original_spacing) / np.array(self.target_spacing)

        # Calculate new shape
        new_shape = np.round(volume.shape * resize_factor).astype(int)

        # Resample using scipy
        resampled = ndimage.zoom(
            volume,
            resize_factor,
            order=3,  # Cubic interpolation
            mode='nearest'
        )

        return resampled

    def load_nifti(self, nifti_path: Path) -> Tuple[np.ndarray, dict]:
        """
        Load NIfTI file

        Args:
            nifti_path: Path to NIfTI file

        Returns:
            Tuple of (volume array, metadata dict)
        """
        try:
            nii = nib.load(str(nifti_path))
            volume = nii.get_fdata()

            # Get spacing from header
            spacing = nii.header.get_zooms()[:3]

            metadata = {
                'spacing': spacing,
                'shape': volume.shape,
                'affine': nii.affine.tolist()
            }

            return volume, metadata

        except Exception as e:
            logger.error(f"Error loading NIfTI {nifti_path}: {str(e)}")
            return None, None

    def load_dicom_series(self, dicom_dir: Path) -> Tuple[np.ndarray, dict]:
        """
        Load DICOM series from directory

        Args:
            dicom_dir: Directory containing DICOM slices

        Returns:
            Tuple of (volume array, metadata dict)
        """
        try:
            # Get all DICOM files
            dicom_files = sorted(dicom_dir.glob('*.dcm'))

            if not dicom_files:
                logger.warning(f"No DICOM files found in {dicom_dir}")
                return None, None

            # Read first slice to get metadata
            ref_slice = pydicom.dcmread(str(dicom_files[0]))

            # Get pixel spacing
            pixel_spacing = ref_slice.PixelSpacing
            slice_thickness = ref_slice.SliceThickness if hasattr(ref_slice, 'SliceThickness') else 1.0

            spacing = (float(pixel_spacing[0]), float(pixel_spacing[1]), float(slice_thickness))

            # Load all slices
            slices = []
            for dcm_file in tqdm(dicom_files, desc="Loading DICOM slices"):
                ds = pydicom.dcmread(str(dcm_file))
                slices.append(ds.pixel_array)

            # Stack into 3D volume
            volume = np.stack(slices, axis=-1)

            metadata = {
                'spacing': spacing,
                'shape': volume.shape
            }

            return volume, metadata

        except Exception as e:
            logger.error(f"Error loading DICOM series from {dicom_dir}: {str(e)}")
            return None, None

    def extract_2d_slices(
        self,
        volume: np.ndarray,
        axis: int = 2,
        skip_empty: bool = True,
        empty_threshold: float = 0.01
    ) -> list:
        """
        Extract 2D slices from 3D volume

        Args:
            volume: Input 3D volume
            axis: Axis to slice along (0=x, 1=y, 2=z)
            skip_empty: Whether to skip empty slices
            empty_threshold: Threshold for considering slice empty

        Returns:
            List of 2D slices
        """
        slices = []

        for i in range(volume.shape[axis]):
            if axis == 0:
                slice_2d = volume[i, :, :]
            elif axis == 1:
                slice_2d = volume[:, i, :]
            else:  # axis == 2
                slice_2d = volume[:, :, i]

            # Skip empty slices
            if skip_empty:
                if np.mean(slice_2d > 0) < empty_threshold:
                    continue

            slices.append(slice_2d)

        return slices

    def process_kits19(self):
        """Process KiTS19 dataset"""
        logger.info("Processing KiTS19 dataset...")

        kits_dir = self.data_dir / 'kits19' / 'kits19' / 'data'

        if not kits_dir.exists():
            logger.error(f"KiTS19 data not found: {kits_dir}")
            return

        # Get all case directories
        case_dirs = sorted([d for d in kits_dir.iterdir() if d.is_dir() and d.name.startswith('case_')])

        logger.info(f"Found {len(case_dirs)} cases")

        for case_dir in tqdm(case_dirs, desc="Processing cases"):
            case_name = case_dir.name

            # Load imaging and segmentation
            imaging_path = case_dir / 'imaging.nii.gz'
            segmentation_path = case_dir / 'segmentation.nii.gz'

            if not imaging_path.exists() or not segmentation_path.exists():
                logger.warning(f"Missing files for {case_name}")
                continue

            # Load volumes
            image_vol, img_metadata = self.load_nifti(imaging_path)
            seg_vol, seg_metadata = self.load_nifti(segmentation_path)

            if image_vol is None or seg_vol is None:
                continue

            # Normalize
            image_vol = self.normalize_hounsfield(image_vol)

            # Resample
            image_vol = self.resample_volume(image_vol, img_metadata['spacing'])
            seg_vol = self.resample_volume(seg_vol, seg_metadata['spacing'])

            # Save processed volumes
            output_case_dir = self.output_dir / 'kits19' / case_name
            output_case_dir.mkdir(parents=True, exist_ok=True)

            np.save(output_case_dir / 'image.npy', image_vol)
            np.save(output_case_dir / 'segmentation.npy', seg_vol)

            # Save metadata
            with open(output_case_dir / 'metadata.json', 'w') as f:
                json.dump({
                    'case': case_name,
                    'original_spacing': img_metadata['spacing'],
                    'original_shape': img_metadata['shape'],
                    'processed_shape': image_vol.shape,
                    'target_spacing': self.target_spacing
                }, f, indent=2)

        logger.info("KiTS19 processing complete!")

    def process_decathlon(self, task_name: str):
        """
        Process Medical Segmentation Decathlon task

        Args:
            task_name: Task name (e.g., 'Task01_BrainTumour')
        """
        logger.info(f"Processing {task_name}...")

        task_dir = self.data_dir / 'decathlon' / task_name

        if not task_dir.exists():
            logger.error(f"Task directory not found: {task_dir}")
            return

        # Process imagesTr and labelsTr
        images_dir = task_dir / 'imagesTr'
        labels_dir = task_dir / 'labelsTr'

        if not images_dir.exists():
            logger.error(f"Images directory not found: {images_dir}")
            return

        image_files = sorted(images_dir.glob('*.nii.gz'))

        logger.info(f"Found {len(image_files)} images")

        for img_file in tqdm(image_files, desc="Processing images"):
            # Load image
            image_vol, img_metadata = self.load_nifti(img_file)

            if image_vol is None:
                continue

            # Load corresponding label if exists
            label_file = labels_dir / img_file.name
            seg_vol = None

            if label_file.exists():
                seg_vol, _ = self.load_nifti(label_file)

            # Normalize
            image_vol = self.normalize_hounsfield(image_vol)

            # Resample
            image_vol = self.resample_volume(image_vol, img_metadata['spacing'])

            if seg_vol is not None:
                seg_vol = self.resample_volume(seg_vol, img_metadata['spacing'])

            # Save
            output_dir = self.output_dir / 'decathlon' / task_name / img_file.stem
            output_dir.mkdir(parents=True, exist_ok=True)

            np.save(output_dir / 'image.npy', image_vol)

            if seg_vol is not None:
                np.save(output_dir / 'segmentation.npy', seg_vol)

        logger.info(f"{task_name} processing complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess CT scan datasets"
    )
    parser.add_argument(
        '--data_dir',
        type=str,
        default='data/raw/ct-segmentation',
        help='Path to raw data directory'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        default='data/processed/ct-segmentation',
        help='Path to output directory'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        choices=['kits19', 'decathlon', 'all'],
        default='kits19',
        help='Dataset to process'
    )
    parser.add_argument(
        '--task',
        type=str,
        help='Decathlon task name (e.g., Task01_BrainTumour)'
    )
    parser.add_argument(
        '--spacing',
        type=float,
        nargs=3,
        default=[1.0, 1.0, 1.0],
        help='Target voxel spacing (mm) in x y z'
    )

    args = parser.parse_args()

    # Create preprocessor
    preprocessor = CTScanPreprocessor(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        target_spacing=tuple(args.spacing)
    )

    # Process dataset
    if args.dataset == 'kits19':
        preprocessor.process_kits19()
    elif args.dataset == 'decathlon':
        if not args.task:
            logger.error("Please specify --task for decathlon dataset")
            sys.exit(1)
        preprocessor.process_decathlon(args.task)
    elif args.dataset == 'all':
        preprocessor.process_kits19()
        # Process all decathlon tasks
        logger.info("Processing all decathlon tasks...")

    logger.info("All done!")


if __name__ == '__main__':
    main()
