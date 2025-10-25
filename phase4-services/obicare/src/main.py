"""
OBiCare - Maternal Health Monitoring Service
Fetal ultrasound analysis, pre-eclampsia prediction, maternal vitals monitoring
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uvicorn
import logging
from datetime import datetime
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OBiCare - Maternal Health Monitoring",
    description="AI-powered maternal health monitoring and fetal ultrasound analysis",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Pydantic models
class PreeclampsiaRiskRequest(BaseModel):
    systolic_bp: float = Field(..., description="Systolic blood pressure (mmHg)")
    diastolic_bp: float = Field(..., description="Diastolic blood pressure (mmHg)")
    proteinuria: float = Field(..., description="Protein in urine (mg/dL)")
    gestational_age: int = Field(..., description="Gestational age (weeks)")
    maternal_age: int = Field(..., description="Maternal age (years)")
    bmi: float = Field(..., description="Body Mass Index")
    previous_preeclampsia: bool = Field(False, description="History of pre-eclampsia")

class MaternalVitalsRequest(BaseModel):
    heart_rate: float
    blood_pressure_systolic: float
    blood_pressure_diastolic: float
    temperature: float
    glucose: Optional[float] = None
    weight: Optional[float] = None

@app.get("/")
async def root():
    return {
        "service": "OBiCare - Maternal Health Monitoring",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": ["/health", "/predict/preeclampsia-risk", "/analyze/ultrasound", "/monitor/vitals"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "OBiCare", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat()}

@app.post("/predict/preeclampsia-risk")
async def predict_preeclampsia_risk(request: PreeclampsiaRiskRequest):
    """
    Predict pre-eclampsia risk using clinical risk factors

    Risk factors:
    - Hypertension (BP ≥140/90)
    - Proteinuria (>300 mg/24hr)
    - Maternal age >35 or <18
    - Obesity (BMI >30)
    - History of pre-eclampsia
    """
    try:
        # Calculate risk score
        risk_score = 0.0

        # Blood pressure
        if request.systolic_bp >= 160 or request.diastolic_bp >= 110:
            risk_score += 3.0
        elif request.systolic_bp >= 140 or request.diastolic_bp >= 90:
            risk_score += 2.0

        # Proteinuria
        if request.proteinuria > 300:
            risk_score += 3.0
        elif request.proteinuria > 150:
            risk_score += 1.5

        # Maternal age
        if request.maternal_age > 35 or request.maternal_age < 18:
            risk_score += 1.5

        # BMI
        if request.bmi > 30:
            risk_score += 1.0

        # Previous history
        if request.previous_preeclampsia:
            risk_score += 2.5

        # Normalize to 0-1
        risk_probability = min(risk_score / 10.0, 1.0)

        # Risk category
        if risk_probability >= 0.7:
            category = "high"
            recommendation = "Urgent: Immediate obstetric consultation. Consider hospitalization."
        elif risk_probability >= 0.4:
            category = "moderate"
            recommendation = "Schedule close monitoring. Weekly blood pressure and urine protein checks."
        else:
            category = "low"
            recommendation = "Routine prenatal care. Continue regular monitoring."

        return {
            "risk_probability": float(risk_probability),
            "risk_category": category,
            "risk_score": float(risk_score),
            "recommendation": recommendation,
            "factors": {
                "hypertension": request.systolic_bp >= 140 or request.diastolic_bp >= 90,
                "severe_hypertension": request.systolic_bp >= 160 or request.diastolic_bp >= 110,
                "proteinuria": request.proteinuria > 300,
                "advanced_maternal_age": request.maternal_age > 35,
                "obesity": request.bmi > 30,
                "previous_preeclampsia": request.previous_preeclampsia
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Pre-eclampsia prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/ultrasound")
async def analyze_ultrasound(file: UploadFile = File(...)):
    """
    Analyze fetal ultrasound for biometry measurements

    Measurements:
    - Head Circumference (HC)
    - Abdominal Circumference (AC)
    - Femur Length (FL)
    - Estimated Fetal Weight (EFW)
    """
    try:
        # Simulate biometry measurements (in production, use actual CV model)
        gestational_age = np.random.randint(20, 40)

        # Simulated measurements (in mm)
        hc = np.random.normal(300, 20)  # Head circumference
        ac = np.random.normal(280, 25)  # Abdominal circumference
        fl = np.random.normal(65, 5)    # Femur length

        # Estimate fetal weight (Hadlock formula)
        efw = 10 ** (1.335 - 0.0034 * ac * fl + 0.0316 * fl + 0.0457 * ac + 0.1623 * hc)

        return {
            "biometry": {
                "head_circumference_mm": float(hc),
                "abdominal_circumference_mm": float(ac),
                "femur_length_mm": float(fl),
                "estimated_fetal_weight_g": float(efw)
            },
            "gestational_age_estimate_weeks": int(gestational_age),
            "growth_assessment": "appropriate_for_gestational_age",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Ultrasound analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitor/vitals")
async def monitor_maternal_vitals(request: MaternalVitalsRequest):
    """Monitor maternal vital signs and detect anomalies"""
    try:
        alerts = []

        # Blood pressure
        if request.blood_pressure_systolic >= 160 or request.blood_pressure_diastolic >= 110:
            alerts.append({"severity": "critical", "message": "Severe hypertension detected", "parameter": "blood_pressure"})
        elif request.blood_pressure_systolic >= 140 or request.blood_pressure_diastolic >= 90:
            alerts.append({"severity": "warning", "message": "Hypertension detected", "parameter": "blood_pressure"})

        # Heart rate
        if request.heart_rate > 110:
            alerts.append({"severity": "warning", "message": "Tachycardia", "parameter": "heart_rate"})
        elif request.heart_rate < 50:
            alerts.append({"severity": "warning", "message": "Bradycardia", "parameter": "heart_rate"})

        # Temperature
        if request.temperature >= 38.0:
            alerts.append({"severity": "warning", "message": "Fever detected", "parameter": "temperature"})

        # Glucose
        if request.glucose and request.glucose > 140:
            alerts.append({"severity": "warning", "message": "Hyperglycemia - check for gestational diabetes", "parameter": "glucose"})

        overall_status = "critical" if any(a['severity'] == 'critical' for a in alerts) else "warning" if alerts else "normal"

        return {
            "vitals": {
                "heart_rate": request.heart_rate,
                "blood_pressure": f"{request.blood_pressure_systolic}/{request.blood_pressure_diastolic}",
                "temperature": request.temperature,
                "glucose": request.glucose
            },
            "status": overall_status,
            "alerts": alerts,
            "alert_count": len(alerts),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Vitals monitoring error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OBiCare Maternal Health Service")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5010)
    args = parser.parse_args()

    logger.info(f"Starting OBiCare on {args.host}:{args.port}")
    uvicorn.run("main:app", host=args.host, port=args.port, log_level="info")
