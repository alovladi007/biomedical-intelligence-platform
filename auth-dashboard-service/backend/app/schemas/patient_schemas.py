"""Patient management schemas"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class PatientCreate(BaseModel):
    """Create patient request schema"""
    mrn: str = Field(..., min_length=1, max_length=50, description="Medical Record Number")
    external_id: Optional[str] = Field(None, max_length=100, description="External EHR ID")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    sex: str = Field(..., description="Sex (male, female, other, unknown)")
    gender_identity: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: str = Field("USA", max_length=100)
    blood_type: Optional[str] = Field(None, max_length=10)
    allergies: Optional[List[str]] = Field(None, description="List of allergies")
    chronic_conditions: Optional[List[str]] = Field(None, description="List of chronic conditions")
    medications: Optional[List[Dict[str, Any]]] = Field(None, description="Current medications")
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    consent_to_research: bool = False
    consent_to_data_sharing: bool = False


class PatientUpdate(BaseModel):
    """Update patient request schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    blood_type: Optional[str] = Field(None, max_length=10)
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    medications: Optional[List[Dict[str, Any]]] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)


class PatientResponse(BaseModel):
    """Patient response schema"""
    id: int
    mrn: str
    external_id: Optional[str]
    first_name: str
    last_name: str
    date_of_birth: datetime
    sex: str
    gender_identity: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: str
    blood_type: Optional[str]
    allergies: Optional[List[str]]
    chronic_conditions: Optional[List[str]]
    medications: Optional[List[Dict[str, Any]]]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relationship: Optional[str]
    consent_to_research: bool
    consent_to_data_sharing: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    """Patient list response schema"""
    total: int
    patients: List[PatientResponse]


class PatientSearchRequest(BaseModel):
    """Patient search request schema"""
    query: Optional[str] = Field(None, description="Search by name or MRN")
    sex: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
