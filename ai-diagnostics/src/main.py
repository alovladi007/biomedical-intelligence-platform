"""
AI Diagnostics Service - FastAPI Application
Provides REST API for symptom checking, drug interactions, and lab interpretation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uvicorn
import logging
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from symptom_checker import SymptomChecker
from drug_interaction_checker import DrugInteractionChecker
from lab_interpreter import LabInterpreter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Diagnostics Service",
    description="AI-powered symptom checking, drug interactions, and lab interpretation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
symptom_checker = SymptomChecker()
drug_checker = DrugInteractionChecker()
lab_interpreter = LabInterpreter()

# Pydantic models
class SymptomCheckRequest(BaseModel):
    symptoms: List[str] = Field(..., description="List of symptom names")
    duration_days: Optional[int] = Field(None, description="Duration in days")
    severity: Optional[str] = Field(None, description="mild, moderate, or severe")
    age: Optional[int] = Field(None, description="Patient age")
    sex: Optional[str] = Field(None, description="male or female")

class DrugInteractionRequest(BaseModel):
    medications: List[str] = Field(..., description="List of medication names")

class LabInterpretationRequest(BaseModel):
    test_name: str = Field(..., description="Lab test name")
    value: float = Field(..., description="Test result value")
    sex: Optional[str] = Field(None, description="male or female")
    age: Optional[int] = Field(None, description="Patient age")

class LabPanelRequest(BaseModel):
    results: Dict[str, float] = Field(..., description="Dictionary of test_name: value")
    sex: Optional[str] = Field(None)
    age: Optional[int] = Field(None)

@app.get("/")
async def root():
    return {
        "service": "AI Diagnostics",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": ["/health", "/symptom-check", "/drug-interactions", "/lab-interpret", "/docs"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Diagnostics",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/symptom-check")
async def check_symptoms(request: SymptomCheckRequest):
    """Check symptoms and return differential diagnoses"""
    try:
        result = symptom_checker.check_symptoms(
            symptoms=request.symptoms,
            duration_days=request.duration_days,
            severity=request.severity,
            age=request.age,
            sex=request.sex
        )
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['error'])
        result['timestamp'] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Symptom check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/symptoms/list")
async def list_symptoms(category: Optional[str] = None):
    """List available symptoms"""
    symptoms = symptom_checker.list_symptoms(category)
    return {"symptoms": symptoms, "count": len(symptoms)}

@app.post("/drug-interactions")
async def check_drug_interactions(request: DrugInteractionRequest):
    """Check for drug-drug interactions"""
    try:
        result = drug_checker.check_interactions(request.medications)
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['error'])
        result['timestamp'] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Drug interaction check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/drug-interactions/food/{medication}")
async def check_food_interactions(medication: str):
    """Check drug-food interactions"""
    result = drug_checker.check_food_interactions(medication)
    result['timestamp'] = datetime.utcnow().isoformat()
    return result

@app.post("/lab-interpret/single")
async def interpret_single_result(request: LabInterpretationRequest):
    """Interpret a single lab result"""
    try:
        result = lab_interpreter.interpret_result(
            test_name=request.test_name,
            value=request.value,
            sex=request.sex,
            age=request.age
        )
        if result.get('status') == 'error':
            raise HTTPException(status_code=400, detail=result['error'])
        result['timestamp'] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lab interpretation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lab-interpret/panel")
async def interpret_panel(request: LabPanelRequest):
    """Interpret complete lab panel"""
    try:
        result = lab_interpreter.interpret_panel(
            results=request.results,
            sex=request.sex,
            age=request.age
        )
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['error'])
        result['timestamp'] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Panel interpretation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lab-interpret/tests")
async def list_lab_tests():
    """List all available lab tests"""
    tests = lab_interpreter.list_available_tests()
    return {"tests": tests, "count": len(tests)}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Diagnostics Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=8001, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    logger.info(f"Starting AI Diagnostics Service on {args.host}:{args.port}")
    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload, log_level="info")
