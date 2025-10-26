"""
Dataset Validation and Statistics

This script validates downloaded datasets and provides statistics:
1. Check file integrity
2. Verify dataset structure
3. Calculate statistics
4. Generate summary report

Usage:
    python validate_datasets.py --dataset chest-xray
    python validate_datasets.py --dataset ct-segmentation
    python validate_datasets.py --all
"""

import os
import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import json
from typing import Dict, List
import logging
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatasetValidator:
    """Validator for medical imaging datasets"""

    def __init__(self, data_dir: str):
        """
        Initialize validator

        Args:
            data_dir: Path to data directory
        """
        self.data_dir = Path(data_dir)
        self.report = {}

    def validate_chest_xray(self) -> Dict:
        """
        Validate NIH ChestX-ray14 dataset

        Returns:
            Validation report dictionary
        """
        logger.info("Validating NIH ChestX-ray14 dataset...")

        chest_xray_dir = self.data_dir / 'raw' / 'chest-xray'

        if not chest_xray_dir.exists():
            logger.error(f"ChestX-ray directory not found: {chest_xray_dir}")
            return {
                'status': 'not_found',
                'path': str(chest_xray_dir)
            }

        report = {
            'status': 'found',
            'path': str(chest_xray_dir),
            'errors': [],
            'warnings': []
        }

        # Check metadata
        metadata_path = chest_xray_dir / 'Data_Entry_2017.csv'
        bbox_path = chest_xray_dir / 'BBox_List_2017.csv'

        if metadata_path.exists():
            df = pd.read_csv(metadata_path)
            report['total_records'] = len(df)

            # Disease distribution
            all_labels = []
            for labels_str in df['Finding Labels']:
                labels = labels_str.split('|')
                all_labels.extend(labels)

            label_counts = Counter(all_labels)
            report['label_distribution'] = dict(label_counts)

            logger.info(f"Metadata: {len(df)} records")
        else:
            report['errors'].append("Data_Entry_2017.csv not found")

        if bbox_path.exists():
            bbox_df = pd.read_csv(bbox_path)
            report['bounding_boxes'] = len(bbox_df)
            logger.info(f"Bounding boxes: {len(bbox_df)} annotations")
        else:
            report['warnings'].append("BBox_List_2017.csv not found")

        # Check images directory
        images_dir = chest_xray_dir / 'images'

        if images_dir.exists():
            image_files = list(images_dir.glob('*.png'))
            report['image_count'] = len(image_files)

            if image_files:
                # Calculate total size
                total_size = sum(f.stat().st_size for f in image_files)
                report['total_size_gb'] = round(total_size / (1024**3), 2)

                logger.info(f"Images: {len(image_files)} files ({report['total_size_gb']} GB)")
            else:
                report['warnings'].append("No image files found")
        else:
            report['errors'].append("images/ directory not found")

        # Validation summary
        if report['errors']:
            report['status'] = 'invalid'
        elif report['warnings']:
            report['status'] = 'valid_with_warnings'
        else:
            report['status'] = 'valid'

        return report

    def validate_ct_segmentation(self) -> Dict:
        """
        Validate CT segmentation datasets

        Returns:
            Validation report dictionary
        """
        logger.info("Validating CT segmentation datasets...")

        ct_dir = self.data_dir / 'raw' / 'ct-segmentation'

        if not ct_dir.exists():
            logger.error(f"CT segmentation directory not found: {ct_dir}")
            return {
                'status': 'not_found',
                'path': str(ct_dir)
            }

        report = {
            'status': 'found',
            'path': str(ct_dir),
            'datasets': {}
        }

        # Check KiTS19
        kits_dir = ct_dir / 'kits19'
        if kits_dir.exists():
            kits_data_dir = kits_dir / 'kits19' / 'data'

            if kits_data_dir.exists():
                case_dirs = [d for d in kits_data_dir.iterdir() if d.is_dir() and d.name.startswith('case_')]

                kits_report = {
                    'status': 'found',
                    'case_count': len(case_dirs)
                }

                # Check for imaging and segmentation files
                valid_cases = 0
                for case_dir in case_dirs:
                    if (case_dir / 'imaging.nii.gz').exists() and \
                       (case_dir / 'segmentation.nii.gz').exists():
                        valid_cases += 1

                kits_report['valid_cases'] = valid_cases
                kits_report['status'] = 'valid' if valid_cases == len(case_dirs) else 'incomplete'

                logger.info(f"KiTS19: {valid_cases}/{len(case_dirs)} valid cases")
            else:
                kits_report = {'status': 'incomplete', 'message': 'Data directory not found'}
        else:
            kits_report = {'status': 'not_found'}

        report['datasets']['kits19'] = kits_report

        # Check Medical Segmentation Decathlon
        decathlon_dir = ct_dir / 'decathlon'
        if decathlon_dir.exists():
            tasks = [d for d in decathlon_dir.iterdir() if d.is_dir() and d.name.startswith('Task')]

            decathlon_report = {
                'status': 'found',
                'task_count': len(tasks),
                'tasks': {}
            }

            for task_dir in tasks:
                task_name = task_dir.name

                images_dir = task_dir / 'imagesTr'
                labels_dir = task_dir / 'labelsTr'

                if images_dir.exists():
                    image_count = len(list(images_dir.glob('*.nii.gz')))
                    label_count = len(list(labels_dir.glob('*.nii.gz'))) if labels_dir.exists() else 0

                    decathlon_report['tasks'][task_name] = {
                        'images': image_count,
                        'labels': label_count,
                        'status': 'valid' if image_count > 0 else 'empty'
                    }

                    logger.info(f"{task_name}: {image_count} images, {label_count} labels")

            report['datasets']['decathlon'] = decathlon_report
        else:
            report['datasets']['decathlon'] = {'status': 'not_found'}

        # Check CHAOS
        chaos_dir = ct_dir / 'chaos'
        if chaos_dir.exists():
            train_sets = chaos_dir / 'Train_Sets'
            test_sets = chaos_dir / 'Test_Sets'

            chaos_report = {
                'status': 'found',
                'has_train': train_sets.exists(),
                'has_test': test_sets.exists()
            }

            report['datasets']['chaos'] = chaos_report
        else:
            report['datasets']['chaos'] = {'status': 'not_found'}

        return report

    def validate_processed(self) -> Dict:
        """
        Validate processed datasets

        Returns:
            Validation report dictionary
        """
        logger.info("Validating processed datasets...")

        processed_dir = self.data_dir / 'processed'

        if not processed_dir.exists():
            logger.warning(f"Processed directory not found: {processed_dir}")
            return {'status': 'not_found'}

        report = {
            'status': 'found',
            'datasets': {}
        }

        # Check chest-xray processed
        chest_xray_processed = processed_dir / 'chest-xray'
        if chest_xray_processed.exists():
            train_dir = chest_xray_processed / 'train'
            val_dir = chest_xray_processed / 'val'
            test_dir = chest_xray_processed / 'test'

            chest_report = {
                'train_samples': len(list(train_dir.glob('*.npy'))) if train_dir.exists() else 0,
                'val_samples': len(list(val_dir.glob('*.npy'))) if val_dir.exists() else 0,
                'test_samples': len(list(test_dir.glob('*.npy'))) if test_dir.exists() else 0
            }

            # Load config if exists
            config_path = chest_xray_processed / 'preprocessing_config.json'
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    chest_report['config'] = config

            report['datasets']['chest-xray'] = chest_report
            logger.info(f"Chest X-ray processed: train={chest_report['train_samples']}, "
                       f"val={chest_report['val_samples']}, test={chest_report['test_samples']}")

        return report

    def generate_report(self, output_path: str = 'dataset_validation_report.json'):
        """
        Generate comprehensive validation report

        Args:
            output_path: Output file path
        """
        logger.info("Generating validation report...")

        report = {
            'data_directory': str(self.data_dir),
            'raw_datasets': {
                'chest-xray': self.validate_chest_xray(),
                'ct-segmentation': self.validate_ct_segmentation()
            },
            'processed_datasets': self.validate_processed()
        }

        # Save report
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to: {output_path}")

        # Print summary
        print("\n" + "="*70)
        print("DATASET VALIDATION SUMMARY")
        print("="*70)

        # Chest X-ray summary
        chest_report = report['raw_datasets']['chest-xray']
        print(f"\n📊 NIH ChestX-ray14: {chest_report.get('status', 'unknown').upper()}")
        if 'image_count' in chest_report:
            print(f"   Images: {chest_report['image_count']:,}")
            print(f"   Size: {chest_report.get('total_size_gb', 0)} GB")
            print(f"   Records: {chest_report.get('total_records', 0):,}")

        # CT segmentation summary
        ct_report = report['raw_datasets']['ct-segmentation']
        print(f"\n📊 CT Segmentation Datasets:")
        for dataset_name, dataset_info in ct_report.get('datasets', {}).items():
            status = dataset_info.get('status', 'unknown')
            print(f"   {dataset_name}: {status.upper()}")

        # Processed datasets summary
        processed_report = report['processed_datasets']
        print(f"\n📊 Processed Datasets:")
        for dataset_name, dataset_info in processed_report.get('datasets', {}).items():
            print(f"   {dataset_name}:")
            if 'train_samples' in dataset_info:
                print(f"      Train: {dataset_info['train_samples']:,} samples")
                print(f"      Val: {dataset_info['val_samples']:,} samples")
                print(f"      Test: {dataset_info['test_samples']:,} samples")

        print("\n" + "="*70 + "\n")

        return report


def main():
    parser = argparse.ArgumentParser(
        description="Validate medical imaging datasets"
    )
    parser.add_argument(
        '--data_dir',
        type=str,
        default='data',
        help='Path to data directory'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        choices=['chest-xray', 'ct-segmentation', 'all'],
        default='all',
        help='Dataset to validate'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='dataset_validation_report.json',
        help='Output report file'
    )

    args = parser.parse_args()

    # Create validator
    validator = DatasetValidator(data_dir=args.data_dir)

    # Generate report
    validator.generate_report(output_path=args.output)

    logger.info("Validation complete!")


if __name__ == '__main__':
    main()
