"""Initial database schema

Revision ID: 001_initial
Revises:
Create Date: 2025-01-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('super_admin', 'admin', 'physician', 'radiologist', 'nurse', 'researcher', 'patient', 'auditor')")

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('role', postgresql.ENUM('super_admin', 'admin', 'physician', 'radiologist', 'nurse', 'researcher', 'patient', 'auditor', name='userrole'), nullable=False),
        sa.Column('department', sa.String(length=100)),
        sa.Column('phone', sa.String(length=20)),
        sa.Column('mfa_enabled', sa.Boolean(), default=False),
        sa.Column('mfa_secret', sa.String(length=32)),
        sa.Column('backup_codes', sa.JSON()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('email_verified_at', sa.DateTime()),
        sa.Column('failed_login_attempts', sa.Integer(), default=0),
        sa.Column('locked_until', sa.DateTime()),
        sa.Column('password_changed_at', sa.DateTime()),
        sa.Column('must_change_password', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('last_login_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_username', 'users', ['username'], unique=True)
    op.create_index('idx_user_email', 'users', ['email'], unique=True)
    op.create_index('idx_user_role', 'users', ['role'])
    op.create_index('idx_user_active', 'users', ['is_active'])

    # Permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('resource', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_permission_resource_action', 'permissions', ['resource', 'action'])

    # Role Permissions table
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', postgresql.ENUM('super_admin', 'admin', 'physician', 'radiologist', 'nurse', 'researcher', 'patient', 'auditor', name='userrole'), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_role_permission', 'role_permissions', ['role', 'permission_id'])

    # User Sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('refresh_token', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45)),
        sa.Column('user_agent', sa.String(length=500)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('last_activity_at', sa.DateTime()),
        sa.Column('revoked_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token'),
        sa.UniqueConstraint('refresh_token')
    )
    op.create_index('idx_session_token', 'user_sessions', ['session_token'], unique=True)
    op.create_index('idx_session_expires', 'user_sessions', ['expires_at'])
    op.create_index('idx_session_user', 'user_sessions', ['user_id'])

    # Patients table
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mrn', sa.String(length=50), nullable=False),
        sa.Column('external_id', sa.String(length=100)),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('date_of_birth', sa.DateTime(), nullable=False),
        sa.Column('sex', sa.String(length=20), nullable=False),
        sa.Column('gender_identity', sa.String(length=50)),
        sa.Column('email', sa.String(length=255)),
        sa.Column('phone', sa.String(length=20)),
        sa.Column('address', sa.Text()),
        sa.Column('city', sa.String(length=100)),
        sa.Column('state', sa.String(length=50)),
        sa.Column('zip_code', sa.String(length=20)),
        sa.Column('country', sa.String(length=100), default='USA'),
        sa.Column('blood_type', sa.String(length=10)),
        sa.Column('allergies', sa.JSON()),
        sa.Column('chronic_conditions', sa.JSON()),
        sa.Column('medications', sa.JSON()),
        sa.Column('emergency_contact_name', sa.String(length=200)),
        sa.Column('emergency_contact_phone', sa.String(length=20)),
        sa.Column('emergency_contact_relationship', sa.String(length=50)),
        sa.Column('consent_to_research', sa.Boolean(), default=False),
        sa.Column('consent_to_data_sharing', sa.Boolean(), default=False),
        sa.Column('privacy_preferences', sa.JSON()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('deceased_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('mrn'),
        sa.UniqueConstraint('external_id')
    )
    op.create_index('idx_patient_mrn', 'patients', ['mrn'], unique=True)
    op.create_index('idx_patient_name', 'patients', ['last_name', 'first_name'])
    op.create_index('idx_patient_dob', 'patients', ['date_of_birth'])
    op.create_index('idx_patient_active', 'patients', ['is_active'])

    # Imaging Studies table
    op.create_table(
        'imaging_studies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('study_uid', sa.String(length=100), nullable=False),
        sa.Column('study_type', sa.String(length=50), nullable=False),
        sa.Column('modality', sa.String(length=20), nullable=False),
        sa.Column('body_part', sa.String(length=100), nullable=False),
        sa.Column('study_date', sa.DateTime(), nullable=False),
        sa.Column('accession_number', sa.String(length=50)),
        sa.Column('referring_physician', sa.String(length=200)),
        sa.Column('performing_physician', sa.String(length=200)),
        sa.Column('institution', sa.String(length=200)),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size_mb', sa.Float()),
        sa.Column('num_images', sa.Integer(), default=1),
        sa.Column('status', sa.String(length=50), default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('study_uid')
    )
    op.create_index('idx_imaging_study_uid', 'imaging_studies', ['study_uid'], unique=True)
    op.create_index('idx_imaging_patient', 'imaging_studies', ['patient_id'])
    op.create_index('idx_imaging_date', 'imaging_studies', ['study_date'])
    op.create_index('idx_imaging_type', 'imaging_studies', ['study_type'])

    # Model Predictions table
    op.create_table(
        'model_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer()),
        sa.Column('imaging_study_id', sa.Integer()),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('prediction_type', sa.String(length=50), nullable=False),
        sa.Column('input_data', sa.JSON(), nullable=False),
        sa.Column('predictions', sa.JSON(), nullable=False),
        sa.Column('confidence_score', sa.Float()),
        sa.Column('risk_level', sa.String(length=20)),
        sa.Column('clinical_indication', sa.Text()),
        sa.Column('findings', sa.JSON()),
        sa.Column('recommendations', sa.Text()),
        sa.Column('reviewed_by_clinician', sa.Boolean(), default=False),
        sa.Column('clinician_id', sa.Integer()),
        sa.Column('clinician_feedback', sa.Text()),
        sa.Column('clinician_agreement', sa.Boolean()),
        sa.Column('processing_time_ms', sa.Float()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id']),
        sa.ForeignKeyConstraint(['imaging_study_id'], ['imaging_studies.id']),
        sa.ForeignKeyConstraint(['clinician_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_prediction_patient', 'model_predictions', ['patient_id'])
    op.create_index('idx_prediction_model', 'model_predictions', ['model_name', 'model_version'])
    op.create_index('idx_prediction_date', 'model_predictions', ['created_at'])
    op.create_index('idx_prediction_reviewed', 'model_predictions', ['reviewed_by_clinician'])

    # Diagnostic Reports table
    op.create_table(
        'diagnostic_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('input_symptoms', sa.JSON()),
        sa.Column('input_medications', sa.JSON()),
        sa.Column('input_lab_results', sa.JSON()),
        sa.Column('differential_diagnoses', sa.JSON()),
        sa.Column('primary_diagnosis', sa.String(length=200)),
        sa.Column('icd10_codes', sa.JSON()),
        sa.Column('urgency_level', sa.String(length=20)),
        sa.Column('drug_interactions', sa.JSON()),
        sa.Column('interaction_severity', sa.String(length=20)),
        sa.Column('abnormal_results', sa.JSON()),
        sa.Column('critical_values', sa.JSON()),
        sa.Column('recommendations', sa.Text()),
        sa.Column('specialist_referral', sa.String(length=200)),
        sa.Column('follow_up_required', sa.Boolean(), default=False),
        sa.Column('reviewed_by_clinician', sa.Boolean(), default=False),
        sa.Column('clinician_id', sa.Integer()),
        sa.Column('clinician_notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id']),
        sa.ForeignKeyConstraint(['clinician_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_diagnostic_patient', 'diagnostic_reports', ['patient_id'])
    op.create_index('idx_diagnostic_type', 'diagnostic_reports', ['report_type'])
    op.create_index('idx_diagnostic_urgency', 'diagnostic_reports', ['urgency_level'])
    op.create_index('idx_diagnostic_date', 'diagnostic_reports', ['created_at'])

    # Genomic Reports table
    op.create_table(
        'genomic_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('vcf_file_path', sa.String(length=500)),
        sa.Column('variants', sa.JSON()),
        sa.Column('pharmacogenes', sa.JSON()),
        sa.Column('pathogenic_variants', sa.JSON()),
        sa.Column('drug_recommendations', sa.JSON()),
        sa.Column('dosing_adjustments', sa.JSON()),
        sa.Column('clinical_actionability', sa.String(length=20)),
        sa.Column('genetic_risk_score', sa.Float()),
        sa.Column('interpretation', sa.Text()),
        sa.Column('recommendations', sa.Text()),
        sa.Column('reviewed_by_geneticist', sa.Boolean(), default=False),
        sa.Column('geneticist_id', sa.Integer()),
        sa.Column('geneticist_notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id']),
        sa.ForeignKeyConstraint(['geneticist_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_genomic_patient', 'genomic_reports', ['patient_id'])
    op.create_index('idx_genomic_type', 'genomic_reports', ['report_type'])
    op.create_index('idx_genomic_date', 'genomic_reports', ['created_at'])

    # Audit Logs table (HIPAA 6-year retention)
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer()),
        sa.Column('username', sa.String(length=100)),
        sa.Column('user_role', sa.String(length=50)),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100)),
        sa.Column('resource_id', sa.Integer()),
        sa.Column('method', sa.String(length=10)),
        sa.Column('endpoint', sa.String(length=500)),
        sa.Column('status_code', sa.Integer()),
        sa.Column('ip_address', sa.String(length=45)),
        sa.Column('user_agent', sa.String(length=500)),
        sa.Column('session_id', sa.String(length=255)),
        sa.Column('request_data', sa.JSON()),
        sa.Column('response_data', sa.JSON()),
        sa.Column('error_message', sa.Text()),
        sa.Column('phi_accessed', sa.Boolean(), default=False),
        sa.Column('patient_id', sa.Integer()),
        sa.Column('access_reason', sa.String(length=200)),
        sa.Column('is_security_event', sa.Boolean(), default=False),
        sa.Column('security_event_type', sa.String(length=100)),
        sa.Column('severity', sa.String(length=20)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])
    op.create_index('idx_audit_date', 'audit_logs', ['created_at'])
    op.create_index('idx_audit_patient', 'audit_logs', ['patient_id'])
    op.create_index('idx_audit_security', 'audit_logs', ['is_security_event', 'severity'])

    # HIPAA Compliance Checks table
    op.create_table(
        'hipaa_compliance_checks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('audit_date', sa.DateTime(), nullable=False),
        sa.Column('auditor_id', sa.Integer()),
        sa.Column('audit_type', sa.String(length=50), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('administrative_score', sa.Float()),
        sa.Column('physical_score', sa.Float()),
        sa.Column('technical_score', sa.Float()),
        sa.Column('compliance_status', sa.String(length=50), nullable=False),
        sa.Column('findings', sa.JSON()),
        sa.Column('recommendations', sa.JSON()),
        sa.Column('remediation_required', sa.Boolean(), default=False),
        sa.Column('evidence_files', sa.JSON()),
        sa.Column('remediation_plan', sa.Text()),
        sa.Column('remediation_deadline', sa.DateTime()),
        sa.Column('remediation_completed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['auditor_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_hipaa_audit_date', 'hipaa_compliance_checks', ['audit_date'])
    op.create_index('idx_hipaa_status', 'hipaa_compliance_checks', ['compliance_status'])

    # System Configuration table
    op.create_table(
        'system_configuration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('data_type', sa.String(length=20), default='string'),
        sa.Column('description', sa.Text()),
        sa.Column('is_encrypted', sa.Boolean(), default=False),
        sa.Column('is_sensitive', sa.Boolean(), default=False),
        sa.Column('category', sa.String(length=50)),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index('idx_config_key', 'system_configuration', ['key'], unique=True)
    op.create_index('idx_config_category', 'system_configuration', ['category'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('system_configuration')
    op.drop_table('hipaa_compliance_checks')
    op.drop_table('audit_logs')
    op.drop_table('genomic_reports')
    op.drop_table('diagnostic_reports')
    op.drop_table('model_predictions')
    op.drop_table('imaging_studies')
    op.drop_table('patients')
    op.drop_table('user_sessions')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('users')

    # Drop enum types
    op.execute("DROP TYPE userrole")
