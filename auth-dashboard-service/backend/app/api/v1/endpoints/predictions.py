"""
Prediction Endpoints

Endpoints:
- GET /api/predictions - List all predictions
- GET /api/predictions/{prediction_id} - Get prediction by ID
- GET /api/predictions/patient/{patient_id} - Get predictions for patient
- POST /api/predictions/{prediction_id}/review - Submit clinician review
- GET /api/predictions/stats - Get prediction statistics
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../../../'))

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Optional
from datetime import datetime

from infrastructure.database.src.database import get_db
from infrastructure.database.src.models import ModelPrediction
from infrastructure.authentication.src.auth_service import get_current_user
from infrastructure.authentication.src.rbac_service import RBACService, AuditLogger

from app.schemas.prediction_schemas import (
    PredictionResponse, PredictionListResponse,
    PredictionFilterRequest,
    ClinicianReviewRequest, ClinicianReviewResponse,
    PredictionStatsResponse
)

router = APIRouter()


@router.get("/", response_model=PredictionListResponse)
async def list_predictions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    model_name: Optional[str] = Query(None),
    prediction_type: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all predictions

    Supports filtering by model_name, prediction_type, risk_level.
    """
    rbac = RBACService(db)
    audit_logger = AuditLogger(db)

    # Check permission (can view predictions for their specialization)
    # For simplicity, allowing all authenticated users to view predictions
    # In production, you might want to restrict based on role

    # Build query
    query = db.query(ModelPrediction)

    # Apply filters
    if model_name:
        query = query.filter(ModelPrediction.model_name == model_name)
    if prediction_type:
        query = query.filter(ModelPrediction.prediction_type == prediction_type)
    if risk_level:
        query = query.filter(ModelPrediction.risk_level == risk_level)

    # Get total and paginated results
    total = query.count()
    predictions = query.order_by(ModelPrediction.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()

    # Log access
    audit_logger.log_event(
        user_id=current_user["user_id"],
        action="list_predictions",
        resource_type="prediction",
        method="GET",
        endpoint="/api/predictions",
        status_code=200,
        severity="info"
    )

    return PredictionListResponse(
        total=total,
        predictions=[PredictionResponse.from_orm(p) for p in predictions]
    )


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    request: Request,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get prediction by ID

    Returns detailed prediction information.
    """
    audit_logger = AuditLogger(db)

    # Get prediction
    prediction = db.query(ModelPrediction).filter(ModelPrediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    # Log PHI access if prediction is linked to a patient
    if prediction.patient_id:
        audit_logger.log_phi_access(
            user_id=current_user["user_id"],
            patient_id=prediction.patient_id,
            action="view_prediction",
            access_reason="Prediction review",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

    return PredictionResponse.from_orm(prediction)


@router.get("/patient/{patient_id}", response_model=PredictionListResponse)
async def get_patient_predictions(
    patient_id: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    request: Request,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all predictions for a specific patient

    Returns all AI predictions associated with the patient.
    """
    rbac = RBACService(db)
    audit_logger = AuditLogger(db)

    # Check permission
    rbac.require_permission(current_user["user_id"], "patient", "read")

    # Query predictions for patient
    query = db.query(ModelPrediction).filter(ModelPrediction.patient_id == patient_id)
    total = query.count()
    predictions = query.order_by(ModelPrediction.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()

    # Log PHI access
    audit_logger.log_phi_access(
        user_id=current_user["user_id"],
        patient_id=patient_id,
        action="view_patient_predictions",
        access_reason="Patient predictions review",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return PredictionListResponse(
        total=total,
        predictions=[PredictionResponse.from_orm(p) for p in predictions]
    )


@router.post("/{prediction_id}/review", response_model=ClinicianReviewResponse)
async def review_prediction(
    prediction_id: int,
    review_data: ClinicianReviewRequest,
    request: Request,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit clinician review for prediction

    Allows clinicians to provide feedback on AI predictions.
    Requires appropriate clinical role (physician, radiologist).
    """
    audit_logger = AuditLogger(db)

    # Check if user has clinical role
    allowed_roles = ["physician", "radiologist", "admin", "super_admin"]
    if current_user["role"] not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clinicians can review predictions"
        )

    # Get prediction
    prediction = db.query(ModelPrediction).filter(ModelPrediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    # Update review fields
    prediction.reviewed_by_clinician = True
    prediction.clinician_id = current_user["user_id"]
    prediction.clinician_feedback = review_data.feedback
    prediction.clinician_agreement = review_data.agreement
    prediction.reviewed_at = datetime.utcnow()

    db.commit()

    # Log review
    audit_logger.log_event(
        user_id=current_user["user_id"],
        action="review_prediction",
        resource_type="prediction",
        resource_id=prediction_id,
        method="POST",
        endpoint=f"/api/predictions/{prediction_id}/review",
        status_code=200,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        phi_accessed=prediction.patient_id is not None,
        patient_id=prediction.patient_id,
        access_reason="Clinician prediction review",
        severity="info"
    )

    return ClinicianReviewResponse(
        success=True,
        message="Review submitted successfully",
        prediction_id=prediction_id
    )


@router.post("/filter", response_model=PredictionListResponse)
async def filter_predictions(
    filter_request: PredictionFilterRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Filter predictions with advanced criteria

    Supports filtering by patient, model, type, risk level, review status, date range.
    """
    audit_logger = AuditLogger(db)

    # Build query
    query = db.query(ModelPrediction)

    # Apply filters
    if filter_request.patient_id:
        query = query.filter(ModelPrediction.patient_id == filter_request.patient_id)
    if filter_request.model_name:
        query = query.filter(ModelPrediction.model_name == filter_request.model_name)
    if filter_request.prediction_type:
        query = query.filter(ModelPrediction.prediction_type == filter_request.prediction_type)
    if filter_request.risk_level:
        query = query.filter(ModelPrediction.risk_level == filter_request.risk_level)
    if filter_request.reviewed_by_clinician is not None:
        query = query.filter(ModelPrediction.reviewed_by_clinician == filter_request.reviewed_by_clinician)
    if filter_request.start_date:
        query = query.filter(ModelPrediction.created_at >= filter_request.start_date)
    if filter_request.end_date:
        query = query.filter(ModelPrediction.created_at <= filter_request.end_date)

    # Get total and paginated results
    total = query.count()
    predictions = query.order_by(ModelPrediction.created_at.desc())\
        .limit(filter_request.limit)\
        .offset(filter_request.offset)\
        .all()

    # Log access
    audit_logger.log_event(
        user_id=current_user["user_id"],
        action="filter_predictions",
        resource_type="prediction",
        method="POST",
        endpoint="/api/predictions/filter",
        status_code=200,
        severity="info"
    )

    return PredictionListResponse(
        total=total,
        predictions=[PredictionResponse.from_orm(p) for p in predictions]
    )


@router.get("/stats", response_model=PredictionStatsResponse)
async def get_prediction_stats(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get prediction statistics

    Returns aggregate statistics about AI predictions.
    """
    audit_logger = AuditLogger(db)

    # Total predictions
    total_predictions = db.query(ModelPrediction).count()

    # Predictions by model
    predictions_by_model = {}
    model_counts = db.query(
        ModelPrediction.model_name,
        func.count(ModelPrediction.id)
    ).group_by(ModelPrediction.model_name).all()

    for model_name, count in model_counts:
        predictions_by_model[model_name] = count

    # Predictions by risk level
    predictions_by_risk = {}
    risk_counts = db.query(
        ModelPrediction.risk_level,
        func.count(ModelPrediction.id)
    ).group_by(ModelPrediction.risk_level).all()

    for risk_level, count in risk_counts:
        if risk_level:
            predictions_by_risk[risk_level] = count

    # Average confidence score
    avg_confidence = db.query(func.avg(ModelPrediction.confidence_score)).scalar() or 0.0

    # Review statistics
    total_reviewed = db.query(ModelPrediction).filter(
        ModelPrediction.reviewed_by_clinician == True
    ).count()
    reviewed_percentage = (total_reviewed / total_predictions * 100) if total_predictions > 0 else 0.0

    # Agreement statistics
    total_agreed = db.query(ModelPrediction).filter(
        ModelPrediction.clinician_agreement == True
    ).count()
    agreement_percentage = (total_agreed / total_reviewed * 100) if total_reviewed > 0 else 0.0

    # Log access
    audit_logger.log_event(
        user_id=current_user["user_id"],
        action="view_prediction_stats",
        resource_type="prediction",
        method="GET",
        endpoint="/api/predictions/stats",
        status_code=200,
        severity="info"
    )

    return PredictionStatsResponse(
        total_predictions=total_predictions,
        predictions_by_model=predictions_by_model,
        predictions_by_risk=predictions_by_risk,
        average_confidence=round(avg_confidence, 3),
        reviewed_percentage=round(reviewed_percentage, 1),
        agreement_percentage=round(agreement_percentage, 1)
    )
