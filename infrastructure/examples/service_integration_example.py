"""
Example: Integrating Existing Services with Infrastructure

This example shows how to integrate Medical Imaging AI service with:
- Database (PostgreSQL)
- Authentication (JWT + MFA)
- Monitoring (Prometheus metrics)
- Logging (Centralized JSON logging)
"""

import sys
import os
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Dict, Optional
import time
import logging

# Add infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import infrastructure components
from infrastructure.database.src.database import init_database, get_db
from infrastructure.database.src.models import (
    Patient, ImagingStudy, ModelPrediction, User
)
from infrastructure.authentication.src.auth_service import (
    AuthService, get_current_user, require_role
)
from infrastructure.authentication.src.rbac_service import RBACService, AuditLogger
from infrastructure.monitoring.src.monitoring_service import (
    MonitoringService, MonitoringMiddleware, track_prediction_time
)
from infrastructure.monitoring.src.logging_config import (
    init_logging, log_with_context
)

# ============================================================================
# Initialize Infrastructure
# ============================================================================

# Initialize database
db_manager = init_database(
    database_url="postgresql://postgres:postgres@localhost:5432/biomedical_platform",
    echo=False  # Set to True for SQL query logging
)

# Initialize monitoring
monitoring = MonitoringService(
    service_name="medical-imaging-ai",
    slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
    pagerduty_api_key=os.getenv("PAGERDUTY_API_KEY")
)

# Initialize logging
logger = init_logging(
    service_name="medical-imaging-ai",
    log_level="INFO",
    enable_json=True,
    enable_cloudwatch=False,  # Set to True for AWS CloudWatch
    enable_elasticsearch=False  # Set to True for ELK stack
)

# ============================================================================
# Create FastAPI App
# ============================================================================

app = FastAPI(
    title="Medical Imaging AI Service",
    description="AI-powered medical image analysis with full infrastructure integration",
    version="1.0.0"
)

# Add monitoring middleware (automatically tracks all HTTP requests)
app.add_middleware(MonitoringMiddleware, monitoring_service=monitoring)

# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    logger.info("Starting Medical Imaging AI service")

    # Set service health to healthy
    monitoring.set_service_health(is_healthy=True)

    logger.info("Service started successfully")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down Medical Imaging AI service")

    # Set service health to unhealthy
    monitoring.set_service_health(is_healthy=False)


# ============================================================================
# Public Endpoints (No Authentication)
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_healthy = db_manager.health_check()

    if db_healthy:
        return {"status": "healthy", "database": "connected"}
    else:
        raise HTTPException(status_code=503, detail="Database unavailable")


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return monitoring.get_metrics()


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/auth/login")
async def login(
    credentials: Dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    User login with JWT authentication

    Request body:
    {
        "username": "user@example.com",
        "password": "password",
        "mfa_token": "123456"  # Optional, required if MFA enabled
    }
    """
    auth_service = AuthService(db)

    try:
        result = auth_service.authenticate_user(
            username=credentials["username"],
            password=credentials["password"],
            mfa_token=credentials.get("mfa_token"),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

        # Record successful authentication
        monitoring.record_auth_attempt(method="password", status="success")

        log_with_context(
            logger,
            logging.INFO,
            f"User logged in: {credentials['username']}",
            user_id=result["user_id"],
            ip_address=request.client.host
        )

        return result

    except HTTPException as e:
        # Record failed authentication
        monitoring.record_auth_attempt(method="password", status="failed")

        log_with_context(
            logger,
            logging.WARNING,
            f"Failed login attempt: {credentials['username']}",
            ip_address=request.client.host,
            error=str(e.detail)
        )

        raise


@app.post("/auth/logout")
async def logout(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout (revoke session)"""
    auth_service = AuthService(db)

    # Revoke all sessions for user
    auth_service.revoke_all_user_sessions(current_user["user_id"])

    logger.info(f"User logged out: {current_user['username']}")

    return {"message": "Logged out successfully"}


# ============================================================================
# Protected Endpoints (Require Authentication)
# ============================================================================

@app.post("/predict/chest-xray")
async def predict_chest_xray(
    data: Dict,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chest X-ray classification with full infrastructure integration

    Demonstrates:
    - Authentication (JWT)
    - Authorization (RBAC)
    - Database integration (save predictions)
    - Monitoring (Prometheus metrics)
    - Audit logging (HIPAA compliance)
    """
    # Initialize services
    rbac = RBACService(db)
    audit_logger = AuditLogger(db)

    # Check permission
    rbac.require_permission(
        user_id=current_user["user_id"],
        resource="imaging",
        action="execute"
    )

    # Get patient
    patient_id = data.get("patient_id")
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Log PHI access (HIPAA requirement)
    audit_logger.log_phi_access(
        user_id=current_user["user_id"],
        patient_id=patient_id,
        action="predict_chest_xray",
        access_reason=data.get("access_reason", "AI diagnosis")
    )

    # Record PHI access metric
    monitoring.record_phi_access(
        user_role=current_user["role"],
        resource_type="imaging"
    )

    # ========================================================================
    # MODEL PREDICTION (with monitoring)
    # ========================================================================

    start_time = time.time()

    try:
        # Track prediction time
        with track_prediction_time(monitoring, "chest_xray_classifier", "v1.0"):
            # *** YOUR ACTUAL MODEL CODE HERE ***
            # Example:
            # predictions = model.predict(data["image"])
            # confidence_score = predictions["confidence"]

            # Mock prediction for example
            predictions = {
                "Atelectasis": 0.12,
                "Cardiomegaly": 0.89,  # High confidence
                "Effusion": 0.05,
                "Pneumonia": 0.15
            }
            confidence_score = 0.89
            risk_level = "high" if confidence_score > 0.7 else "moderate"

        processing_time_ms = (time.time() - start_time) * 1000

        # Record model prediction metrics
        monitoring.record_model_prediction(
            model_name="chest_xray_classifier",
            model_version="v1.0",
            duration_seconds=processing_time_ms / 1000,
            confidence_score=confidence_score,
            status="success"
        )

        # ====================================================================
        # SAVE TO DATABASE
        # ====================================================================

        # Create imaging study record
        imaging_study = ImagingStudy(
            patient_id=patient_id,
            study_uid=data.get("study_uid", f"STUDY-{patient_id}-{int(time.time())}"),
            study_type="chest_xray",
            modality="CR",
            body_part="CHEST",
            study_date=data.get("study_date"),
            file_path=data.get("image_path", "/encrypted/storage/path"),
            status="completed"
        )
        db.add(imaging_study)
        db.flush()  # Get imaging_study.id

        # Save model prediction
        prediction_record = ModelPrediction(
            patient_id=patient_id,
            imaging_study_id=imaging_study.id,
            model_name="chest_xray_classifier",
            model_version="v1.0",
            service_name="medical-imaging-ai",
            prediction_type="classification",
            input_data={"image_path": data.get("image_path")},
            predictions=predictions,
            confidence_score=confidence_score,
            risk_level=risk_level,
            findings=[
                {"finding": "Cardiomegaly", "confidence": 0.89, "severity": "moderate"}
            ],
            recommendations="Follow-up with cardiology. Consider echocardiogram.",
            processing_time_ms=processing_time_ms
        )
        db.add(prediction_record)
        db.commit()

        # ====================================================================
        # LOGGING
        # ====================================================================

        log_with_context(
            logger,
            logging.INFO,
            "Chest X-ray prediction completed",
            user_id=current_user["user_id"],
            patient_id=patient_id,
            model_name="chest_xray_classifier",
            confidence=confidence_score,
            risk_level=risk_level,
            processing_time_ms=processing_time_ms
        )

        # ====================================================================
        # RETURN RESPONSE
        # ====================================================================

        return {
            "prediction_id": prediction_record.id,
            "patient_id": patient_id,
            "predictions": predictions,
            "confidence_score": confidence_score,
            "risk_level": risk_level,
            "recommendations": "Follow-up with cardiology. Consider echocardiogram.",
            "processing_time_ms": processing_time_ms
        }

    except Exception as e:
        # Record error
        monitoring.record_error(error_type=type(e).__name__, severity="error")

        log_with_context(
            logger,
            logging.ERROR,
            f"Prediction failed: {str(e)}",
            user_id=current_user["user_id"],
            patient_id=patient_id,
            error=str(e)
        )

        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# ============================================================================
# Admin Endpoints (Require Admin Role)
# ============================================================================

@app.get("/admin/predictions")
async def get_all_predictions(
    current_user: Dict = Depends(get_current_user),
    _: None = Depends(require_role(["admin", "super_admin"])),
    db: Session = Depends(get_db)
):
    """Get all model predictions (admin only)"""

    predictions = db.query(ModelPrediction).all()

    return {
        "total": len(predictions),
        "predictions": [
            {
                "id": p.id,
                "patient_id": p.patient_id,
                "model_name": p.model_name,
                "confidence_score": p.confidence_score,
                "created_at": p.created_at.isoformat()
            }
            for p in predictions
        ]
    }


# ============================================================================
# Database Query Examples
# ============================================================================

@app.get("/patients/{patient_id}/predictions")
async def get_patient_predictions(
    patient_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all predictions for a specific patient"""

    # Check permission
    rbac = RBACService(db)
    rbac.require_permission(
        user_id=current_user["user_id"],
        resource="patient",
        action="read"
    )

    # Log PHI access
    audit_logger = AuditLogger(db)
    audit_logger.log_phi_access(
        user_id=current_user["user_id"],
        patient_id=patient_id,
        action="view_patient_predictions",
        access_reason="Clinical review"
    )

    # Query predictions
    predictions = db.query(ModelPrediction).filter(
        ModelPrediction.patient_id == patient_id
    ).order_by(ModelPrediction.created_at.desc()).all()

    return {
        "patient_id": patient_id,
        "total_predictions": len(predictions),
        "predictions": [
            {
                "id": p.id,
                "model_name": p.model_name,
                "confidence_score": p.confidence_score,
                "risk_level": p.risk_level,
                "created_at": p.created_at.isoformat()
            }
            for p in predictions
        ]
    }


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Medical Imaging AI service on port 5001")

    uvicorn.run(
        "service_integration_example:app",
        host="0.0.0.0",
        port=5001,
        reload=False,  # Set to True for development
        log_config=None  # Use our custom logging
    )
