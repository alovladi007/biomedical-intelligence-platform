# Medical Dataset Storage

## Directory Structure

```
data/
├── raw/              # Original, unmodified datasets
│   ├── chest-xray/  # NIH ChestX-ray14 dataset (112,120 images, ~45GB)
│   ├── ct-segmentation/  # CT scan datasets for segmentation
│   └── genomic/     # Genomic data
├── processed/        # Preprocessed data ready for training
│   ├── chest-xray/  # Normalized, augmented X-ray data
│   ├── ct-segmentation/  # Processed CT scans
│   └── genomic/     # Processed genomic sequences
├── models/           # Trained model checkpoints and weights
│   ├── chest-xray/  # X-ray classification models
│   ├── ct-segmentation/  # Segmentation models
│   └── genomic/     # Genomic prediction models
└── logs/             # Training logs, metrics, tensorboard
    ├── chest-xray/
    ├── ct-segmentation/
    └── genomic/
```

## Datasets

### 1. NIH ChestX-ray14
- **Location**: `raw/chest-xray/`
- **Size**: ~45 GB
- **Images**: 112,120 frontal-view X-rays
- **Patients**: 30,805 unique patients
- **Labels**: 14 disease categories
- **Download**: See `scripts/download_chest_xray14.sh`
- **Source**: https://nihcc.app.box.com/v/ChestXray-NIHCC

### 2. CT Segmentation Datasets
- **Location**: `raw/ct-segmentation/`
- **Options**:
  - Medical Segmentation Decathlon
  - CHAOS Challenge
  - KiTS19 (Kidney Tumor Segmentation)
- **Download**: See `scripts/download_ct_datasets.sh`

### 3. Genomic Data
- **Location**: `raw/genomic/`
- **Planned datasets**: TBD

## Storage Requirements

| Dataset | Raw Size | Processed Size | Total |
|---------|----------|----------------|-------|
| NIH ChestX-ray14 | 45 GB | ~60 GB | 105 GB |
| CT Segmentation | ~50 GB | ~70 GB | 120 GB |
| Genomic | TBD | TBD | TBD |
| **Total** | **~95 GB** | **~130 GB** | **~225 GB** |

## Data Processing Pipeline

1. **Download** → `raw/`
2. **Preprocess** → `processed/`
   - Normalization
   - Augmentation
   - Format conversion
3. **Train** → `models/`
4. **Log** → `logs/`

## Usage

### Download Datasets

```bash
# NIH ChestX-ray14
./scripts/download_chest_xray14.sh

# CT Segmentation
./scripts/download_ct_datasets.sh
```

### Preprocess Data

```bash
# Chest X-ray
python scripts/preprocess_chest_xray.py

# CT Segmentation
python scripts/preprocess_ct_scans.py
```

## Data Privacy & HIPAA

⚠️ **IMPORTANT**: All datasets must be:
- De-identified
- HIPAA compliant
- Properly anonymized
- Access-controlled
- Encrypted at rest

See `HIPAA_COMPLIANCE.md` for details.

## .gitignore

Large dataset files are excluded from git. See `.gitignore`:

```
data/raw/
data/processed/
data/models/*.h5
data/models/*.pth
data/logs/
```

Only metadata and scripts are version-controlled.
