"""
Role-Based Access Control (RBAC) Service

Implements fine-grained permission management for HIPAA compliance
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class RBACService:
    """Role-Based Access Control service"""

    def __init__(self, db_session: Session):
        self.db = db_session

    # ========================================================================
    # Permission Management
    # ========================================================================

    def create_permission(
        self,
        name: str,
        resource: str,
        action: str,
        description: str = None
    ) -> Dict:
        """
        Create a new permission

        Args:
            name: Permission name (e.g., 'patient_read')
            resource: Resource type (e.g., 'patient', 'imaging', 'genomics')
            action: Action (e.g., 'read', 'write', 'delete', 'execute')
            description: Optional description

        Returns:
            Created permission dict
        """
        from database.src.models import Permission

        # Check if permission already exists
        existing = self.db.query(Permission).filter(Permission.name == name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission '{name}' already exists"
            )

        permission = Permission(
            name=name,
            resource=resource,
            action=action,
            description=description
        )

        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)

        logger.info(f"Created permission: {name}")

        return {
            "id": permission.id,
            "name": permission.name,
            "resource": permission.resource,
            "action": permission.action,
            "description": permission.description
        }

    def assign_permission_to_role(self, role: str, permission_name: str):
        """Assign a permission to a role"""
        from database.src.models import Permission, RolePermission, UserRole

        # Get permission
        permission = self.db.query(Permission).filter(
            Permission.name == permission_name
        ).first()

        if not permission:
            raise HTTPException(
                status_code=404,
                detail=f"Permission '{permission_name}' not found"
            )

        # Check if already assigned
        existing = self.db.query(RolePermission).filter(
            RolePermission.role == UserRole[role.upper()],
            RolePermission.permission_id == permission.id
        ).first()

        if existing:
            logger.warning(f"Permission '{permission_name}' already assigned to role '{role}'")
            return

        # Create assignment
        role_permission = RolePermission(
            role=UserRole[role.upper()],
            permission_id=permission.id
        )

        self.db.add(role_permission)
        self.db.commit()

        logger.info(f"Assigned permission '{permission_name}' to role '{role}'")

    def get_role_permissions(self, role: str) -> List[Dict]:
        """Get all permissions for a role"""
        from database.src.models import Permission, RolePermission, UserRole

        permissions = self.db.query(Permission).join(
            RolePermission
        ).filter(
            RolePermission.role == UserRole[role.upper()]
        ).all()

        return [
            {
                "id": p.id,
                "name": p.name,
                "resource": p.resource,
                "action": p.action,
                "description": p.description
            }
            for p in permissions
        ]

    # ========================================================================
    # Permission Checking
    # ========================================================================

    def has_permission(
        self,
        user_id: int,
        resource: str,
        action: str
    ) -> bool:
        """
        Check if user has permission for resource/action

        Args:
            user_id: User ID
            resource: Resource type (e.g., 'patient')
            action: Action (e.g., 'read', 'write')

        Returns:
            True if user has permission, False otherwise
        """
        from database.src.models import User, Permission, RolePermission

        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        # Super admin has all permissions
        if user.role.value == 'super_admin':
            return True

        # Check role permissions
        permission_exists = self.db.query(Permission).join(
            RolePermission
        ).filter(
            RolePermission.role == user.role,
            Permission.resource == resource,
            Permission.action == action
        ).first()

        return permission_exists is not None

    def require_permission(
        self,
        user_id: int,
        resource: str,
        action: str
    ):
        """
        Require user to have permission (raises exception if not)

        Args:
            user_id: User ID
            resource: Resource type
            action: Action

        Raises:
            HTTPException: If user doesn't have permission
        """
        if not self.has_permission(user_id, resource, action):
            from database.src.models import User
            user = self.db.query(User).filter(User.id == user_id).first()

            logger.warning(
                f"Permission denied: User {user.username} (role: {user.role.value}) "
                f"attempted {action} on {resource}"
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions to {action} {resource}"
            )

    # ========================================================================
    # Initialize Default Permissions
    # ========================================================================

    def initialize_default_permissions(self):
        """Initialize default permissions for the platform"""

        default_permissions = [
            # Patient permissions
            {"name": "patient_read", "resource": "patient", "action": "read",
             "description": "View patient demographic and health information"},
            {"name": "patient_write", "resource": "patient", "action": "write",
             "description": "Create and update patient records"},
            {"name": "patient_delete", "resource": "patient", "action": "delete",
             "description": "Delete patient records"},

            # Imaging permissions
            {"name": "imaging_read", "resource": "imaging", "action": "read",
             "description": "View medical imaging studies"},
            {"name": "imaging_write", "resource": "imaging", "action": "write",
             "description": "Upload and modify imaging studies"},
            {"name": "imaging_analyze", "resource": "imaging", "action": "execute",
             "description": "Run AI analysis on imaging studies"},

            # Diagnostic permissions
            {"name": "diagnostic_read", "resource": "diagnostic", "action": "read",
             "description": "View diagnostic reports"},
            {"name": "diagnostic_write", "resource": "diagnostic", "action": "write",
             "description": "Create and modify diagnostic reports"},
            {"name": "diagnostic_analyze", "resource": "diagnostic", "action": "execute",
             "description": "Run AI diagnostic analysis"},

            # Genomic permissions
            {"name": "genomic_read", "resource": "genomic", "action": "read",
             "description": "View genomic reports"},
            {"name": "genomic_write", "resource": "genomic", "action": "write",
             "description": "Upload and modify genomic data"},
            {"name": "genomic_analyze", "resource": "genomic", "action": "execute",
             "description": "Run genomic analysis"},

            # User management permissions
            {"name": "user_read", "resource": "user", "action": "read",
             "description": "View user accounts"},
            {"name": "user_write", "resource": "user", "action": "write",
             "description": "Create and modify user accounts"},
            {"name": "user_delete", "resource": "user", "action": "delete",
             "description": "Delete user accounts"},

            # Audit permissions
            {"name": "audit_read", "resource": "audit", "action": "read",
             "description": "View audit logs"},
            {"name": "audit_write", "resource": "audit", "action": "write",
             "description": "Modify audit log settings"},

            # System configuration permissions
            {"name": "config_read", "resource": "config", "action": "read",
             "description": "View system configuration"},
            {"name": "config_write", "resource": "config", "action": "write",
             "description": "Modify system configuration"},

            # HIPAA compliance permissions
            {"name": "hipaa_read", "resource": "hipaa", "action": "read",
             "description": "View HIPAA compliance reports"},
            {"name": "hipaa_audit", "resource": "hipaa", "action": "execute",
             "description": "Conduct HIPAA compliance audits"},
        ]

        for perm in default_permissions:
            try:
                self.create_permission(**perm)
            except HTTPException:
                # Permission already exists
                pass

        logger.info("Default permissions initialized")

    def initialize_default_role_permissions(self):
        """Assign default permissions to roles"""

        role_permissions = {
            "SUPER_ADMIN": [
                "patient_read", "patient_write", "patient_delete",
                "imaging_read", "imaging_write", "imaging_analyze",
                "diagnostic_read", "diagnostic_write", "diagnostic_analyze",
                "genomic_read", "genomic_write", "genomic_analyze",
                "user_read", "user_write", "user_delete",
                "audit_read", "audit_write",
                "config_read", "config_write",
                "hipaa_read", "hipaa_audit"
            ],
            "ADMIN": [
                "patient_read", "patient_write",
                "imaging_read", "imaging_write",
                "diagnostic_read", "diagnostic_write",
                "genomic_read", "genomic_write",
                "user_read", "user_write",
                "audit_read",
                "config_read",
                "hipaa_read"
            ],
            "PHYSICIAN": [
                "patient_read", "patient_write",
                "imaging_read", "imaging_analyze",
                "diagnostic_read", "diagnostic_write", "diagnostic_analyze",
                "genomic_read", "genomic_analyze"
            ],
            "RADIOLOGIST": [
                "patient_read",
                "imaging_read", "imaging_write", "imaging_analyze",
                "diagnostic_read"
            ],
            "NURSE": [
                "patient_read",
                "imaging_read",
                "diagnostic_read",
                "genomic_read"
            ],
            "RESEARCHER": [
                "patient_read",
                "imaging_read", "imaging_analyze",
                "diagnostic_read", "diagnostic_analyze",
                "genomic_read", "genomic_analyze"
            ],
            "PATIENT": [
                "patient_read",
                "imaging_read",
                "diagnostic_read",
                "genomic_read"
            ],
            "AUDITOR": [
                "audit_read",
                "hipaa_read", "hipaa_audit"
            ]
        }

        for role, permissions in role_permissions.items():
            for permission_name in permissions:
                try:
                    self.assign_permission_to_role(role, permission_name)
                except Exception as e:
                    logger.error(f"Error assigning {permission_name} to {role}: {str(e)}")

        logger.info("Default role permissions initialized")


# ============================================================================
# Audit Logging
# ============================================================================

class AuditLogger:
    """HIPAA-compliant audit logging"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def log_event(
        self,
        user_id: Optional[int],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        method: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        request_data: Optional[Dict] = None,
        response_data: Optional[Dict] = None,
        error_message: Optional[str] = None,
        phi_accessed: bool = False,
        patient_id: Optional[int] = None,
        access_reason: Optional[str] = None,
        is_security_event: bool = False,
        security_event_type: Optional[str] = None,
        severity: str = "info"
    ):
        """
        Log an audit event

        Required for HIPAA compliance - all PHI access must be logged
        """
        from database.src.models import AuditLog, User

        # Get user details if user_id provided
        username = None
        user_role = None
        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                username = user.username
                user_role = user.role.value

        audit_log = AuditLog(
            user_id=user_id,
            username=username,
            user_role=user_role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            request_data=request_data,
            response_data=response_data,
            error_message=error_message,
            phi_accessed=phi_accessed,
            patient_id=patient_id,
            access_reason=access_reason,
            is_security_event=is_security_event,
            security_event_type=security_event_type,
            severity=severity
        )

        self.db.add(audit_log)
        self.db.commit()

        # Log to application logger as well
        log_level = getattr(logging, severity.upper(), logging.INFO)
        logger.log(
            log_level,
            f"AUDIT: {action} by {username or 'anonymous'} - "
            f"{resource_type}:{resource_id} - Status: {status_code}"
        )

    def log_phi_access(
        self,
        user_id: int,
        patient_id: int,
        action: str,
        access_reason: str,
        ip_address: str = None,
        user_agent: str = None
    ):
        """
        Log PHI access (required by HIPAA)

        All access to Protected Health Information must be logged
        """
        self.log_event(
            user_id=user_id,
            action=action,
            resource_type="patient",
            resource_id=patient_id,
            phi_accessed=True,
            patient_id=patient_id,
            access_reason=access_reason,
            ip_address=ip_address,
            user_agent=user_agent,
            severity="info"
        )

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        """
        Log security event (failed logins, unauthorized access, etc.)
        """
        self.log_event(
            user_id=user_id,
            action=event_type,
            is_security_event=True,
            security_event_type=event_type,
            severity=severity,
            ip_address=ip_address,
            request_data=details
        )
