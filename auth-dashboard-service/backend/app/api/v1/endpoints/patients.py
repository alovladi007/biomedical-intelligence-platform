"""
Patient Management Endpoints

Endpoints:
- GET /api/patients - List all patients
- GET /api/patients/{patient_id} - Get patient by ID
- POST /api/patients - Create new patient
- PUT /api/patients/{patient_id} - Update patient
- DELETE /api/patients/{patient_id} - Delete patient
- POST /api/patients/search - Search patients
"""

from __future__ import annotations

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../../../'))

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Dict, List, Optional
from datetime import datetime, date

from infrastructure.database.src.database import get_db
from infrastructure.database.src.models import Patient
from infrastructure.authentication.src.auth_service import get_current_user
from infrastructure.authentication.src.rbac_service import RBACService, AuditLogger

from app.schemas.patient_schemas import (
    PatientCreate, PatientUpdate, PatientResponse,
    PatientListResponse, PatientSearchRequest
)

router = APIRouter()


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all patients

    Requires 'patient_read' permission.
    """
    rbac = RBACService(db)
    audit_logger = AuditLogger(db)

    # Check permission
    rbac.require_permission(current_user["user_id"], "patient", "read")

    # Query patients
    query = db.query(Patient).filter(Patient.is_active == True)
    total = query.count()
    patients = query.order_by(Patient.created_at.desc()).limit(limit).offset(offset).all()

    # Log access
    audit_logger.log_event(
        user_id=current_user["user_id"],
        action="list_patients",
        resource_type="patient",
        method="GET",
        endpoint="/api/patients",
        status_code=200,
        severity="info"
    )

    return PatientListResponse(
        total=total,
        patients=[PatientResponse.from_orm(p) for p in patients]
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    request: Request,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient by ID

    Requires 'patient_read' permission.
    Logs PHI access.
    """
    rbac = RBACService(db)
    audit_logger = AuditLogger(db)

    # Check permission
    rbac.require_permission(current_user["user_id"], "patient", "read")

    # Get patient
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.is_active == True).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Log PHI access
    audit_logger.log_phi_access(
        user_id=current_user["user_id"],
        patient_id=patient_id,
        action="view_patient",
        access_reason="Patient record access",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return PatientResponse.from_orm(patient)


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    request_data: PatientCreate,
    request: Request,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new patient

    Requires 'patient_write' permission.
    """
    rbac = RBACService(db)
    audit_logger = AuditLogger(db)

    # Check permission
    rbac.require_permission(current_user["user_id"], "patient", "write")

    # Check if MRN already exists
    existing = db.query(Patient).filter(Patient.mrn == request_data.mrn).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient with this MRN already exists"
        )

    # Create patient
    new_patient = Patient(
        mrn=request_data.mrn,
        external_id=request_data.external_id,
        first_name=request_data.first_name,
        last_name=request_data.last_name,
        date_of_birth=request_data.date_of_birth,
        sex=request_data.sex,
        gender_identity=request_data.gender_identity,
        email=request_data.email,
        phone=request_data.phone,
        address=request_data.address,
        city=request_data.city,
        state=request_data.state,
        zip_code=request_data.zip_code,
        country=request_data.country,
        blood_type=request_data.blood_type,
        allergies=request_data.allergies,
        chronic_conditions=request_data.chronic_conditions,
        medications=request_data.medications,
        emergency_contact_name=request_data.emergency_contact_name,
        emergency_contact_phone=request_data.emergency_contact_phone,
        emergency_contact_relationship=request_data.emergency_contact_relationship,
        consent_to_research=request_data.consent_to_research,
        consent_to_data_sharing=request_data.consent_to_data_sharing,
        is_active=True
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    # Log creation
    audit_logger.log_event(
        user_id=current_user["user_id"],
        action="create_patient",
        resource_type="patient",
        resource_id=new_patient.id,
        method="POST",
        endpoint="/api/patients",
        status_code=201,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        phi_accessed=True,
        patient_id=new_patient.id,
        access_reason="Patient record creation",
        severity="info"
    )

    return PatientResponse.from_orm(new_patient)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    request_data: PatientUpdate,
    request: Request,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update patient

    Requires 'patient_write' permission.
    """
    rbac = RBACService(db)
    audit_logger = AuditLogger(db)

    # Check permission
    rbac.require_permission(current_user["user_id"], "patient", "write")

    # Get patient
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.is_active == True).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Update fields
    update_data = request_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(patient)

    # Log update
    audit_logger.log_event(
        user_id=current_user["user_id"],
        action="update_patient",
        resource_type="patient",
        resource_id=patient_id,
        method="PUT",
        endpoint=f"/api/patients/{patient_id}",
        status_code=200,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        phi_accessed=True,
        patient_id=patient_id,
        access_reason="Patient record update",
        severity="info"
    )

    return PatientResponse.from_orm(patient)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    request: Request,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete patient (soft delete)

    Requires 'patient_delete' permission.
    """
    rbac = RBACService(db)
    audit_logger = AuditLogger(db)

    # Check permission
    rbac.require_permission(current_user["user_id"], "patient", "delete")

    # Get patient
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Soft delete
    patient.is_active = False
    patient.updated_at = datetime.utcnow()
    db.commit()

    # Log deletion
    audit_logger.log_event(
        user_id=current_user["user_id"],
        action="delete_patient",
        resource_type="patient",
        resource_id=patient_id,
        method="DELETE",
        endpoint=f"/api/patients/{patient_id}",
        status_code=204,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        phi_accessed=True,
        patient_id=patient_id,
        access_reason="Patient record deletion",
        severity="warning"
    )


@router.post("/search", response_model=PatientListResponse)
async def search_patients(
    search_request: PatientSearchRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search patients

    Requires 'patient_read' permission.
    Supports search by name, MRN, demographics.
    """
    rbac = RBACService(db)
    audit_logger = AuditLogger(db)

    # Check permission
    rbac.require_permission(current_user["user_id"], "patient", "read")

    # Build query
    query = db.query(Patient).filter(Patient.is_active == True)

    # Search by query string (name or MRN)
    if search_request.query:
        query = query.filter(
            or_(
                Patient.first_name.ilike(f"%{search_request.query}%"),
                Patient.last_name.ilike(f"%{search_request.query}%"),
                Patient.mrn.ilike(f"%{search_request.query}%")
            )
        )

    # Filter by sex
    if search_request.sex:
        query = query.filter(Patient.sex == search_request.sex)

    # Filter by age
    if search_request.min_age or search_request.max_age:
        today = date.today()
        if search_request.min_age:
            max_dob = today.replace(year=today.year - search_request.min_age)
            query = query.filter(Patient.date_of_birth <= max_dob)
        if search_request.max_age:
            min_dob = today.replace(year=today.year - search_request.max_age - 1)
            query = query.filter(Patient.date_of_birth >= min_dob)

    # Filter by location
    if search_request.city:
        query = query.filter(Patient.city.ilike(f"%{search_request.city}%"))
    if search_request.state:
        query = query.filter(Patient.state.ilike(f"%{search_request.state}%"))

    # Get total and paginated results
    total = query.count()
    patients = query.order_by(Patient.last_name, Patient.first_name)\
        .limit(search_request.limit)\
        .offset(search_request.offset)\
        .all()

    # Log search
    audit_logger.log_event(
        user_id=current_user["user_id"],
        action="search_patients",
        resource_type="patient",
        method="POST",
        endpoint="/api/patients/search",
        status_code=200,
        request_data={"query": search_request.query},
        severity="info"
    )

    return PatientListResponse(
        total=total,
        patients=[PatientResponse.from_orm(p) for p in patients]
    )
