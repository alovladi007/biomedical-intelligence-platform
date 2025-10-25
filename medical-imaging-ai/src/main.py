"""
Medical Imaging AI Service - FastAPI Application
Provides REST API for chest X-ray classification and CT segmentation
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uvicorn
import logging
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chest_xray_classifier import ChestXrayClassifier
from ct_segmentation import CTSegmentationService
import numpy as np

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Medical Imaging AI Service",
    description="AI-powered chest X-ray classification and CT segmentation",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models (lazy loading)
chest_xray_classifier = None
ct_segmenter = None


def get_chest_xray_classifier():
    """Lazy load chest X-ray classifier"""
    global chest_xray_classifier
    if chest_xray_classifier is None:
        chest_xray_classifier = ChestXrayClassifier()
        logger.info("Chest X-ray classifier loaded")
    return chest_xray_classifier


def get_ct_segmenter():
    """Lazy load CT segmentation service"""
    global ct_segmenter
    if ct_segmenter is None:
        ct_segmenter = CTSegmentationService()
        logger.info("CT segmentation service loaded")
    return ct_segmenter


# Pydantic models
class XrayPredictionResponse(BaseModel):
    predictions: List[Dict]
    all_probabilities: Dict[str, float]
    risk_score: Dict
    num_findings: int
    status: str
    timestamp: str


class CTSegmentationResponse(BaseModel):
    analysis: Dict
    probabilities: Dict[str, float]
    status: str
    timestamp: str
    message: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    models_loaded: Dict[str, bool]
    timestamp: str


# Routes
@app.get("/", response_model=Dict)
async def root():
    """Root endpoint"""
    return {
        "service": "Medical Imaging AI",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/health",
            "/classify/chest-xray",
            "/segment/ct",
            "/docs"
        ]
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Medical Imaging AI",
        "version": "1.0.0",
        "models_loaded": {
            "chest_xray_classifier": chest_xray_classifier is not None,
            "ct_segmenter": ct_segmenter is not None
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/classify/chest-xray", response_model=XrayPredictionResponse)
async def classify_chest_xray(
    file: UploadFile = File(..., description="Chest X-ray image (JPEG, PNG, DICOM)"),
    threshold: float = Form(0.5, description="Probability threshold for predictions")
):
    """
    Classify chest X-ray for 14 pathologies

    Pathologies:
    - Atelectasis, Cardiomegaly, Effusion, Infiltration
    - Mass, Nodule, Pneumonia, Pneumothorax
    - Consolidation, Edema, Emphysema, Fibrosis
    - Pleural_Thickening, Hernia

    Args:
        file: Chest X-ray image file
        threshold: Probability threshold (0.0-1.0)

    Returns:
        Predictions with probabilities and risk assessment
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read image data
        image_data = await file.read()

        # Get classifier
        classifier = get_chest_xray_classifier()

        # Predict
        result = classifier.predict(image_data, threshold=threshold)

        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['error'])

        # Add timestamp
        result['timestamp'] = datetime.utcnow().isoformat()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chest X-ray classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify/chest-xray/batch")
async def classify_chest_xray_batch(
    files: List[UploadFile] = File(..., description="Multiple chest X-ray images"),
    threshold: float = Form(0.5)
):
    """
    Batch classification for multiple chest X-rays

    Args:
        files: List of chest X-ray image files
        threshold: Probability threshold

    Returns:
        List of prediction results
    """
    try:
        if len(files) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 images per batch")

        # Read all images
        image_data_list = []
        for file in files:
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} must be an image")
            image_data = await file.read()
            image_data_list.append(image_data)

        # Get classifier
        classifier = get_chest_xray_classifier()

        # Batch predict
        results = classifier.batch_predict(image_data_list, threshold=threshold)

        # Add timestamps
        for result in results:
            result['timestamp'] = datetime.utcnow().isoformat()

        return {
            "num_images": len(files),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/segment/ct", response_model=CTSegmentationResponse)
async def segment_ct(
    file: UploadFile = File(..., description="CT scan file (NIfTI .nii.gz or numpy .npy)"),
    spacing_z: float = Form(2.5, description="Voxel spacing in z direction (mm)"),
    spacing_y: float = Form(0.7, description="Voxel spacing in y direction (mm)"),
    spacing_x: float = Form(0.7, description="Voxel spacing in x direction (mm)")
):
    """
    Segment organs in CT scan

    Organs:
    - Liver, Right Kidney, Left Kidney, Spleen, Pancreas

    Args:
        file: CT scan file (NIfTI or numpy array)
        spacing_z, spacing_y, spacing_x: Voxel spacing in mm

    Returns:
        Organ segmentation with volume analysis
    """
    try:
        # Read CT volume
        file_content = await file.read()

        # Parse based on file extension
        if file.filename.endswith('.npy'):
            import io
            ct_volume = np.load(io.BytesIO(file_content))
        elif file.filename.endswith('.nii') or file.filename.endswith('.nii.gz'):
            import nibabel as nib
            import io
            nifti_file = nib.FileHolder(fileobj=io.BytesIO(file_content))
            nifti_img = nib.Nifti1Image.from_file_map({'header': nifti_file, 'image': nifti_file})
            ct_volume = nifti_img.get_fdata()
        else:
            raise HTTPException(status_code=400, detail="File must be .npy or .nii/.nii.gz format")

        # Validate volume
        if ct_volume.ndim != 3:
            raise HTTPException(status_code=400, detail="CT volume must be 3D")

        # Get segmenter
        segmenter = get_ct_segmenter()

        # Segment
        spacing = (spacing_z, spacing_y, spacing_x)
        result = segmenter.segment(ct_volume, spacing=spacing)

        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['error'])

        # Remove large segmentation mask from response (too large for API)
        # Store it separately or provide download link in production
        if 'segmentation_mask' in result:
            result['message'] = "Segmentation mask available (contact for download)"
            del result['segmentation_mask']

        if 'organ_contours' in result:
            # Simplify contours for API response
            result['message'] = "Organ contours simplified for API response"
            del result['organ_contours']

        # Add timestamp
        result['timestamp'] = datetime.utcnow().isoformat()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CT segmentation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/info")
async def model_info():
    """Get information about loaded models"""
    return {
        "chest_xray_classifier": {
            "name": "DenseNet-121",
            "classes": ChestXrayClassifier.PATHOLOGY_CLASSES if chest_xray_classifier else [],
            "num_classes": len(ChestXrayClassifier.PATHOLOGY_CLASSES),
            "loaded": chest_xray_classifier is not None
        },
        "ct_segmenter": {
            "name": "3D U-Net",
            "organs": list(CTSegmentationService.ORGAN_CLASSES.values()) if ct_segmenter else [],
            "num_classes": len(CTSegmentationService.ORGAN_CLASSES),
            "loaded": ct_segmenter is not None
        }
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Medical Imaging AI Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=5001, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    logger.info(f"Starting Medical Imaging AI Service on {args.host}:{args.port}")

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )
