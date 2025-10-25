"""
SQLAlchemy Database Models for Biomedical Intelligence Platform

HIPAA-compliant database schema with:
- Patient records
- Audit logs (6-year retention)
- Model predictions history
- User authentication/authorization
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, Float,
    ForeignKey, JSON, Enum as SQLEnum, Index, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


# ============================================================================
# User Authentication & Authorization
# ============================================================================

class UserRole(enum.Enum):
    """User roles for RBAC"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    PHYSICIAN = "physician"
    RADIOLOGIST = "radiologist"
    NURSE = "nurse"
    RESEARCHER = "researcher"
    PATIENT = "patient"
    AUDITOR = "auditor"


class User(Base):
    """User accounts with authentication"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt hash

    # Profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    department = Column(String(100))
    phone = Column(String(20))

    # MFA
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(32))  # TOTP secret (encrypted)
    backup_codes = Column(JSON)  # List of backup codes (encrypted)

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)

    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    must_change_password = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

    __table_args__ = (
        Index('idx_user_role', 'role'),
        Index('idx_user_active', 'is_active'),
    )


class Permission(Base):
    """Granular permissions for RBAC"""
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    resource = Column(String(100), nullable=False)  # e.g., 'patient', 'imaging', 'genomics'
    action = Column(String(50), nullable=False)  # e.g., 'read', 'write', 'delete'
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_permission_resource_action', 'resource', 'action'),
    )


class RolePermission(Base):
    """Mapping of roles to permissions"""
    __tablename__ = 'role_permissions'

    id = Column(Integer, primary_key=True)
    role = Column(SQLEnum(UserRole), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_role_permission', 'role', 'permission_id'),
    )


class UserSession(Base):
    """Active user sessions with JWT tokens"""
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Session data
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(String(500))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="sessions")

    __table_args__ = (
        Index('idx_session_expires', 'expires_at'),
        Index('idx_session_user', 'user_id'),
    )


# ============================================================================
# Patient Records (HIPAA-compliant)
# ============================================================================

class Patient(Base):
    """Patient demographic and health information"""
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)

    # Identifiers
    mrn = Column(String(50), unique=True, nullable=False, index=True)  # Medical Record Number
    external_id = Column(String(100), unique=True)  # EHR system ID

    # Demographics
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    sex = Column(String(20), nullable=False)  # male, female, other, unknown
    gender_identity = Column(String(50))

    # Contact
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(100), default='USA')

    # Medical
    blood_type = Column(String(10))
    allergies = Column(JSON)  # List of allergies
    chronic_conditions = Column(JSON)  # List of chronic conditions
    medications = Column(JSON)  # Current medications

    # Emergency contact
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relationship = Column(String(50))

    # Privacy
    consent_to_research = Column(Boolean, default=False)
    consent_to_data_sharing = Column(Boolean, default=False)
    privacy_preferences = Column(JSON)

    # Status
    is_active = Column(Boolean, default=True)
    deceased_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    imaging_studies = relationship("ImagingStudy", back_populates="patient", cascade="all, delete-orphan")
    diagnostic_reports = relationship("DiagnosticReport", back_populates="patient", cascade="all, delete-orphan")
    genomic_reports = relationship("GenomicReport", back_populates="patient", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_patient_name', 'last_name', 'first_name'),
        Index('idx_patient_dob', 'date_of_birth'),
        Index('idx_patient_active', 'is_active'),
    )


# ============================================================================
# Medical Imaging
# ============================================================================

class ImagingStudy(Base):
    """Medical imaging studies (X-ray, CT, MRI)"""
    __tablename__ = 'imaging_studies'

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)

    # Study information
    study_uid = Column(String(100), unique=True, nullable=False, index=True)  # DICOM Study UID
    study_type = Column(String(50), nullable=False)  # chest_xray, ct_scan, mri
    modality = Column(String(20), nullable=False)  # CR, CT, MR, etc.
    body_part = Column(String(100), nullable=False)

    # Study metadata
    study_date = Column(DateTime, nullable=False)
    accession_number = Column(String(50))
    referring_physician = Column(String(200))
    performing_physician = Column(String(200))
    institution = Column(String(200))

    # File information
    file_path = Column(String(500), nullable=False)  # Encrypted storage path
    file_size_mb = Column(Float)
    num_images = Column(Integer, default=1)

    # Status
    status = Column(String(50), default='pending')  # pending, processing, completed, failed

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="imaging_studies")
    predictions = relationship("ModelPrediction", back_populates="imaging_study", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_imaging_patient', 'patient_id'),
        Index('idx_imaging_date', 'study_date'),
        Index('idx_imaging_type', 'study_type'),
    )


# ============================================================================
# AI Model Predictions
# ============================================================================

class ModelPrediction(Base):
    """AI model predictions with full audit trail"""
    __tablename__ = 'model_predictions'

    id = Column(Integer, primary_key=True)

    # Links
    patient_id = Column(Integer, ForeignKey('patients.id'))
    imaging_study_id = Column(Integer, ForeignKey('imaging_studies.id'))

    # Model information
    model_name = Column(String(100), nullable=False)  # chest_xray_classifier, ct_segmentation, etc.
    model_version = Column(String(50), nullable=False)
    service_name = Column(String(100), nullable=False)  # medical-imaging-ai, ai-diagnostics, etc.

    # Prediction data
    prediction_type = Column(String(50), nullable=False)  # classification, segmentation, diagnosis
    input_data = Column(JSON, nullable=False)  # Input parameters
    predictions = Column(JSON, nullable=False)  # Full prediction output
    confidence_score = Column(Float)
    risk_level = Column(String(20))  # low, moderate, high

    # Clinical context
    clinical_indication = Column(Text)
    findings = Column(JSON)  # Structured findings
    recommendations = Column(Text)

    # Validation
    reviewed_by_clinician = Column(Boolean, default=False)
    clinician_id = Column(Integer, ForeignKey('users.id'))
    clinician_feedback = Column(Text)
    clinician_agreement = Column(Boolean)  # True/False if reviewed

    # Performance metrics
    processing_time_ms = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime)

    # Relationships
    imaging_study = relationship("ImagingStudy", back_populates="predictions")

    __table_args__ = (
        Index('idx_prediction_patient', 'patient_id'),
        Index('idx_prediction_model', 'model_name', 'model_version'),
        Index('idx_prediction_date', 'created_at'),
        Index('idx_prediction_reviewed', 'reviewed_by_clinician'),
    )


# ============================================================================
# Diagnostic Reports
# ============================================================================

class DiagnosticReport(Base):
    """AI-generated diagnostic reports (symptom checking, drug interactions, lab results)"""
    __tablename__ = 'diagnostic_reports'

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)

    # Report information
    report_type = Column(String(50), nullable=False)  # symptom_check, drug_interaction, lab_interpretation
    service_name = Column(String(100), nullable=False)

    # Input data
    input_symptoms = Column(JSON)
    input_medications = Column(JSON)
    input_lab_results = Column(JSON)

    # Diagnostic output
    differential_diagnoses = Column(JSON)  # List of possible diagnoses
    primary_diagnosis = Column(String(200))
    icd10_codes = Column(JSON)  # List of ICD-10 codes
    urgency_level = Column(String(20))  # low, moderate, high, emergency

    # Drug interactions
    drug_interactions = Column(JSON)
    interaction_severity = Column(String(20))  # minor, moderate, major, contraindicated

    # Lab results
    abnormal_results = Column(JSON)
    critical_values = Column(JSON)

    # Recommendations
    recommendations = Column(Text)
    specialist_referral = Column(String(200))
    follow_up_required = Column(Boolean, default=False)

    # Review
    reviewed_by_clinician = Column(Boolean, default=False)
    clinician_id = Column(Integer, ForeignKey('users.id'))
    clinician_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime)

    # Relationships
    patient = relationship("Patient", back_populates="diagnostic_reports")

    __table_args__ = (
        Index('idx_diagnostic_patient', 'patient_id'),
        Index('idx_diagnostic_type', 'report_type'),
        Index('idx_diagnostic_urgency', 'urgency_level'),
        Index('idx_diagnostic_date', 'created_at'),
    )


# ============================================================================
# Genomic Data
# ============================================================================

class GenomicReport(Base):
    """Genomic analysis reports (variant annotation, pharmacogenomics)"""
    __tablename__ = 'genomic_reports'

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)

    # Report information
    report_type = Column(String(50), nullable=False)  # variant_annotation, pharmacogenomics
    vcf_file_path = Column(String(500))  # Encrypted VCF file path

    # Variant information
    variants = Column(JSON)  # List of annotated variants
    pharmacogenes = Column(JSON)  # Pharmacogenomic genes detected
    pathogenic_variants = Column(JSON)  # Clinically significant variants

    # Pharmacogenomics
    drug_recommendations = Column(JSON)  # Drug-gene interactions
    dosing_adjustments = Column(JSON)  # Personalized dosing

    # Clinical significance
    clinical_actionability = Column(String(20))  # low, moderate, high
    genetic_risk_score = Column(Float)

    # Interpretation
    interpretation = Column(Text)
    recommendations = Column(Text)

    # Review
    reviewed_by_geneticist = Column(Boolean, default=False)
    geneticist_id = Column(Integer, ForeignKey('users.id'))
    geneticist_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime)

    # Relationships
    patient = relationship("Patient", back_populates="genomic_reports")

    __table_args__ = (
        Index('idx_genomic_patient', 'patient_id'),
        Index('idx_genomic_type', 'report_type'),
        Index('idx_genomic_date', 'created_at'),
    )


# ============================================================================
# Audit Logs (HIPAA 6-year retention)
# ============================================================================

class AuditLog(Base):
    """Comprehensive audit trail for HIPAA compliance"""
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)

    # Who
    user_id = Column(Integer, ForeignKey('users.id'))
    username = Column(String(100))  # Denormalized for retention
    user_role = Column(String(50))

    # What
    action = Column(String(100), nullable=False)  # login, logout, view_patient, update_patient, run_model, etc.
    resource_type = Column(String(100))  # patient, imaging_study, user, etc.
    resource_id = Column(Integer)

    # How
    method = Column(String(10))  # GET, POST, PUT, DELETE
    endpoint = Column(String(500))
    status_code = Column(Integer)

    # Context
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    session_id = Column(String(255))

    # Details
    request_data = Column(JSON)  # Sanitized request payload
    response_data = Column(JSON)  # Sanitized response (no PHI)
    error_message = Column(Text)

    # PHI access tracking
    phi_accessed = Column(Boolean, default=False)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    access_reason = Column(String(200))  # Required for PHI access

    # Security events
    is_security_event = Column(Boolean, default=False)
    security_event_type = Column(String(100))  # failed_login, unauthorized_access, etc.
    severity = Column(String(20))  # info, warning, error, critical

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_date', 'created_at'),
        Index('idx_audit_patient', 'patient_id'),
        Index('idx_audit_security', 'is_security_event', 'severity'),
        # Partition by month for efficient 6-year retention queries
    )


# ============================================================================
# HIPAA Compliance Tracking
# ============================================================================

class HIPAAComplianceCheck(Base):
    """HIPAA compliance audit results"""
    __tablename__ = 'hipaa_compliance_checks'

    id = Column(Integer, primary_key=True)

    # Audit information
    audit_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    auditor_id = Column(Integer, ForeignKey('users.id'))
    audit_type = Column(String(50), nullable=False)  # automated, manual, annual

    # Compliance scores
    overall_score = Column(Float, nullable=False)
    administrative_score = Column(Float)
    physical_score = Column(Float)
    technical_score = Column(Float)

    # Status
    compliance_status = Column(String(50), nullable=False)  # compliant, partially_compliant, non_compliant

    # Findings
    findings = Column(JSON)  # List of compliance findings
    recommendations = Column(JSON)  # List of recommendations
    remediation_required = Column(Boolean, default=False)

    # Evidence
    evidence_files = Column(JSON)  # List of evidence file paths

    # Follow-up
    remediation_plan = Column(Text)
    remediation_deadline = Column(DateTime)
    remediation_completed_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_hipaa_audit_date', 'audit_date'),
        Index('idx_hipaa_status', 'compliance_status'),
    )


# ============================================================================
# System Configuration
# ============================================================================

class SystemConfiguration(Base):
    """System-wide configuration settings"""
    __tablename__ = 'system_configuration'

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    data_type = Column(String(20), default='string')  # string, int, float, bool, json
    description = Column(Text)

    # Security
    is_encrypted = Column(Boolean, default=False)
    is_sensitive = Column(Boolean, default=False)

    # Metadata
    category = Column(String(50))  # security, logging, monitoring, models
    updated_by = Column(Integer, ForeignKey('users.id'))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_config_category', 'category'),
    )
