"""Prediction schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PredictionResponse(BaseModel):
    """AI prediction response schema"""
    id: int
    patient_id: Optional[int]
    imaging_study_id: Optional[int]
    model_name: str
    model_version: str
    service_name: str
    prediction_type: str
    input_data: Dict[str, Any]
    predictions: Dict[str, Any]
    confidence_score: Optional[float]
    risk_level: Optional[str]
    clinical_indication: Optional[str]
    findings: Optional[Dict[str, Any]]
    recommendations: Optional[str]
    reviewed_by_clinician: bool
    clinician_id: Optional[int]
    clinician_feedback: Optional[str]
    clinician_agreement: Optional[bool]
    processing_time_ms: Optional[float]
    created_at: datetime
    reviewed_at: Optional[datetime]

    class Config:
        from_attributes = True


class PredictionListResponse(BaseModel):
    """Prediction list response schema"""
    total: int
    predictions: List[PredictionResponse]


class PredictionFilterRequest(BaseModel):
    """Prediction filter request schema"""
    patient_id: Optional[int] = None
    model_name: Optional[str] = None
    prediction_type: Optional[str] = None
    risk_level: Optional[str] = None
    reviewed_by_clinician: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class ClinicianReviewRequest(BaseModel):
    """Clinician review request schema"""
    feedback: Optional[str] = Field(None, description="Clinician feedback")
    agreement: bool = Field(..., description="Does clinician agree with prediction?")


class ClinicianReviewResponse(BaseModel):
    """Clinician review response schema"""
    success: bool
    message: str
    prediction_id: int


class PredictionStatsResponse(BaseModel):
    """Prediction statistics response schema"""
    total_predictions: int
    predictions_by_model: Dict[str, int]
    predictions_by_risk: Dict[str, int]
    average_confidence: float
    reviewed_percentage: float
    agreement_percentage: float
