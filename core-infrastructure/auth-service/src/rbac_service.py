"""
Role-Based Access Control (RBAC) Service
Manages permissions and access control for biomedical platform
"""

import logging
from typing import Dict, List, Set, Optional
from enum import Enum
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Protected resource types"""
    PATIENT_DATA = "patient_data"
    DICOM_STUDY = "dicom_study"
    GENOMIC_DATA = "genomic_data"
    LAB_RESULTS = "lab_results"
    MEDICAL_RECORD = "medical_record"
    MODEL_PREDICTION = "model_prediction"
    AUDIT_LOG = "audit_log"
    USER_MANAGEMENT = "user_management"
    SYSTEM_CONFIG = "system_config"


class Permission(Enum):
    """Permission types"""
    READ = "read"
    WRITE = "write"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"


class Role(Enum):
    """Predefined roles"""
    # Clinical roles
    PHYSICIAN = "physician"
    NURSE = "nurse"
    RADIOLOGIST = "radiologist"
    LAB_TECHNICIAN = "lab_technician"
    PHARMACIST = "pharmacist"

    # Administrative roles
    ADMIN = "admin"
    SYSTEM_ADMIN = "system_admin"
    SECURITY_ADMIN = "security_admin"

    # Research roles
    RESEARCHER = "researcher"
    DATA_SCIENTIST = "data_scientist"

    # Technical roles
    API_USER = "api_user"
    ML_ENGINEER = "ml_engineer"

    # Audit roles
    AUDITOR = "auditor"
    COMPLIANCE_OFFICER = "compliance_officer"


@dataclass
class RoleDefinition:
    """Role with permissions"""
    role_name: str
    description: str
    permissions: Dict[ResourceType, Set[Permission]] = field(default_factory=dict)
    inherits_from: List[str] = field(default_factory=list)


class RBACService:
    """
    Role-Based Access Control Service

    Features:
    - Hierarchical role inheritance
    - Fine-grained permissions per resource
    - Dynamic permission checking
    - HIPAA-compliant access control
    - Audit trail integration
    """

    def __init__(self):
        """Initialize RBAC service"""
        self.roles: Dict[str, RoleDefinition] = {}
        self.user_roles: Dict[str, Set[str]] = {}  # user_id -> roles

        # Initialize default roles
        self._init_default_roles()

        logger.info("RBAC Service initialized")

    def _init_default_roles(self):
        """Initialize predefined roles with permissions"""

        # ==================== CLINICAL ROLES ====================

        # Physician - Full access to patient data
        self.roles[Role.PHYSICIAN.value] = RoleDefinition(
            role_name=Role.PHYSICIAN.value,
            description="Physician with full patient access",
            permissions={
                ResourceType.PATIENT_DATA: {Permission.READ, Permission.WRITE, Permission.UPDATE},
                ResourceType.DICOM_STUDY: {Permission.READ, Permission.WRITE},
                ResourceType.GENOMIC_DATA: {Permission.READ},
                ResourceType.LAB_RESULTS: {Permission.READ, Permission.WRITE},
                ResourceType.MEDICAL_RECORD: {Permission.READ, Permission.WRITE, Permission.UPDATE},
                ResourceType.MODEL_PREDICTION: {Permission.READ, Permission.EXECUTE}
            }
        )

        # Nurse - Read patient data, write observations
        self.roles[Role.NURSE.value] = RoleDefinition(
            role_name=Role.NURSE.value,
            description="Nurse with patient care access",
            permissions={
                ResourceType.PATIENT_DATA: {Permission.READ},
                ResourceType.LAB_RESULTS: {Permission.READ, Permission.WRITE},
                ResourceType.MEDICAL_RECORD: {Permission.READ, Permission.WRITE}
            }
        )

        # Radiologist - DICOM studies
        self.roles[Role.RADIOLOGIST.value] = RoleDefinition(
            role_name=Role.RADIOLOGIST.value,
            description="Radiologist with imaging access",
            permissions={
                ResourceType.PATIENT_DATA: {Permission.READ},
                ResourceType.DICOM_STUDY: {Permission.READ, Permission.WRITE, Permission.UPDATE},
                ResourceType.MODEL_PREDICTION: {Permission.READ, Permission.EXECUTE}
            }
        )

        # Lab Technician - Lab results
        self.roles[Role.LAB_TECHNICIAN.value] = RoleDefinition(
            role_name=Role.LAB_TECHNICIAN.value,
            description="Lab technician",
            permissions={
                ResourceType.PATIENT_DATA: {Permission.READ},
                ResourceType.LAB_RESULTS: {Permission.READ, Permission.WRITE, Permission.UPDATE},
                ResourceType.GENOMIC_DATA: {Permission.READ, Permission.WRITE}
            }
        )

        # Pharmacist - Medication access
        self.roles[Role.PHARMACIST.value] = RoleDefinition(
            role_name=Role.PHARMACIST.value,
            description="Pharmacist",
            permissions={
                ResourceType.PATIENT_DATA: {Permission.READ},
                ResourceType.MEDICAL_RECORD: {Permission.READ},
                ResourceType.GENOMIC_DATA: {Permission.READ}  # Pharmacogenomics
            }
        )

        # ==================== RESEARCH ROLES ====================

        # Researcher - De-identified data access
        self.roles[Role.RESEARCHER.value] = RoleDefinition(
            role_name=Role.RESEARCHER.value,
            description="Researcher with de-identified data access",
            permissions={
                ResourceType.PATIENT_DATA: {Permission.READ},  # De-identified only
                ResourceType.DICOM_STUDY: {Permission.READ},
                ResourceType.GENOMIC_DATA: {Permission.READ},
                ResourceType.LAB_RESULTS: {Permission.READ},
                ResourceType.MODEL_PREDICTION: {Permission.READ}
            }
        )

        # Data Scientist - Model access
        self.roles[Role.DATA_SCIENTIST.value] = RoleDefinition(
            role_name=Role.DATA_SCIENTIST.value,
            description="Data scientist with model access",
            permissions={
                ResourceType.PATIENT_DATA: {Permission.READ},
                ResourceType.DICOM_STUDY: {Permission.READ},
                ResourceType.GENOMIC_DATA: {Permission.READ},
                ResourceType.MODEL_PREDICTION: {Permission.READ, Permission.WRITE, Permission.EXECUTE}
            },
            inherits_from=[Role.RESEARCHER.value]
        )

        # ML Engineer - Full model management
        self.roles[Role.ML_ENGINEER.value] = RoleDefinition(
            role_name=Role.ML_ENGINEER.value,
            description="ML engineer with model management",
            permissions={
                ResourceType.MODEL_PREDICTION: {Permission.READ, Permission.WRITE, Permission.UPDATE, Permission.DELETE, Permission.EXECUTE}
            },
            inherits_from=[Role.DATA_SCIENTIST.value]
        )

        # ==================== ADMINISTRATIVE ROLES ====================

        # Admin - User and system management
        self.roles[Role.ADMIN.value] = RoleDefinition(
            role_name=Role.ADMIN.value,
            description="Administrator",
            permissions={
                ResourceType.USER_MANAGEMENT: {Permission.READ, Permission.WRITE, Permission.UPDATE, Permission.DELETE},
                ResourceType.AUDIT_LOG: {Permission.READ},
                ResourceType.SYSTEM_CONFIG: {Permission.READ, Permission.UPDATE}
            }
        )

        # System Admin - Full system access
        self.roles[Role.SYSTEM_ADMIN.value] = RoleDefinition(
            role_name=Role.SYSTEM_ADMIN.value,
            description="System administrator with full access",
            permissions={
                ResourceType.PATIENT_DATA: {Permission.ADMIN},
                ResourceType.DICOM_STUDY: {Permission.ADMIN},
                ResourceType.GENOMIC_DATA: {Permission.ADMIN},
                ResourceType.LAB_RESULTS: {Permission.ADMIN},
                ResourceType.MEDICAL_RECORD: {Permission.ADMIN},
                ResourceType.MODEL_PREDICTION: {Permission.ADMIN},
                ResourceType.AUDIT_LOG: {Permission.ADMIN},
                ResourceType.USER_MANAGEMENT: {Permission.ADMIN},
                ResourceType.SYSTEM_CONFIG: {Permission.ADMIN}
            },
            inherits_from=[Role.ADMIN.value]
        )

        # Security Admin - Security and audit
        self.roles[Role.SECURITY_ADMIN.value] = RoleDefinition(
            role_name=Role.SECURITY_ADMIN.value,
            description="Security administrator",
            permissions={
                ResourceType.AUDIT_LOG: {Permission.READ, Permission.WRITE},
                ResourceType.USER_MANAGEMENT: {Permission.READ, Permission.UPDATE},
                ResourceType.SYSTEM_CONFIG: {Permission.READ, Permission.UPDATE}
            }
        )

        # ==================== AUDIT ROLES ====================

        # Auditor - Read-only audit access
        self.roles[Role.AUDITOR.value] = RoleDefinition(
            role_name=Role.AUDITOR.value,
            description="Auditor with read-only access",
            permissions={
                ResourceType.AUDIT_LOG: {Permission.READ},
                ResourceType.PATIENT_DATA: {Permission.READ},
                ResourceType.USER_MANAGEMENT: {Permission.READ}
            }
        )

        # Compliance Officer - Compliance monitoring
        self.roles[Role.COMPLIANCE_OFFICER.value] = RoleDefinition(
            role_name=Role.COMPLIANCE_OFFICER.value,
            description="Compliance officer",
            permissions={
                ResourceType.AUDIT_LOG: {Permission.READ, Permission.WRITE},
                ResourceType.PATIENT_DATA: {Permission.READ},
                ResourceType.SYSTEM_CONFIG: {Permission.READ}
            },
            inherits_from=[Role.AUDITOR.value]
        )

        # ==================== API ROLES ====================

        # API User - Programmatic access
        self.roles[Role.API_USER.value] = RoleDefinition(
            role_name=Role.API_USER.value,
            description="API user with limited access",
            permissions={
                ResourceType.MODEL_PREDICTION: {Permission.READ, Permission.EXECUTE}
            }
        )

        logger.info(f"Initialized {len(self.roles)} default roles")

    # ==================== PERMISSION CHECKING ====================

    def check_permission(
        self,
        user_id: str,
        resource_type: ResourceType,
        permission: Permission
    ) -> bool:
        """
        Check if user has permission for resource

        Args:
            user_id: User identifier
            resource_type: Type of resource
            permission: Required permission

        Returns:
            True if user has permission
        """
        if user_id not in self.user_roles:
            logger.warning(f"User not found: {user_id}")
            return False

        user_role_names = self.user_roles[user_id]

        # Get all permissions from all roles (including inherited)
        all_permissions = self._get_effective_permissions(user_role_names)

        # Check if user has permission
        if resource_type in all_permissions:
            if permission in all_permissions[resource_type] or Permission.ADMIN in all_permissions[resource_type]:
                return True

        logger.warning(f"Permission denied: user={user_id}, resource={resource_type.value}, permission={permission.value}")
        return False

    def _get_effective_permissions(
        self,
        role_names: Set[str]
    ) -> Dict[ResourceType, Set[Permission]]:
        """
        Get effective permissions from roles (including inheritance)

        Args:
            role_names: Set of role names

        Returns:
            Combined permissions
        """
        effective_permissions: Dict[ResourceType, Set[Permission]] = {}

        # Process each role
        for role_name in role_names:
            if role_name not in self.roles:
                continue

            role_def = self.roles[role_name]

            # Add inherited roles
            inherited_roles = set()
            self._collect_inherited_roles(role_name, inherited_roles)

            # Collect permissions from all roles
            for r in inherited_roles | {role_name}:
                if r in self.roles:
                    for resource, perms in self.roles[r].permissions.items():
                        if resource not in effective_permissions:
                            effective_permissions[resource] = set()

                        effective_permissions[resource].update(perms)

        return effective_permissions

    def _collect_inherited_roles(self, role_name: str, inherited: Set[str]):
        """Recursively collect inherited roles"""
        if role_name not in self.roles:
            return

        role_def = self.roles[role_name]

        for parent_role in role_def.inherits_from:
            if parent_role not in inherited:
                inherited.add(parent_role)
                self._collect_inherited_roles(parent_role, inherited)

    # ==================== USER ROLE MANAGEMENT ====================

    def assign_role(self, user_id: str, role_name: str) -> bool:
        """
        Assign role to user

        Args:
            user_id: User identifier
            role_name: Role name

        Returns:
            Success status
        """
        if role_name not in self.roles:
            logger.error(f"Role not found: {role_name}")
            return False

        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()

        self.user_roles[user_id].add(role_name)

        logger.info(f"Role assigned: user={user_id}, role={role_name}")

        return True

    def revoke_role(self, user_id: str, role_name: str) -> bool:
        """Revoke role from user"""
        if user_id not in self.user_roles:
            return False

        if role_name in self.user_roles[user_id]:
            self.user_roles[user_id].remove(role_name)
            logger.info(f"Role revoked: user={user_id}, role={role_name}")
            return True

        return False

    def get_user_roles(self, user_id: str) -> List[str]:
        """Get roles assigned to user"""
        return list(self.user_roles.get(user_id, set()))

    def get_user_permissions(
        self,
        user_id: str
    ) -> Dict[str, List[str]]:
        """
        Get all effective permissions for user

        Returns:
            Dict of resource -> permissions
        """
        if user_id not in self.user_roles:
            return {}

        effective_perms = self._get_effective_permissions(self.user_roles[user_id])

        # Convert to serializable format
        return {
            resource.value: [perm.value for perm in perms]
            for resource, perms in effective_perms.items()
        }

    # ==================== ROLE MANAGEMENT ====================

    def create_custom_role(
        self,
        role_name: str,
        description: str,
        permissions: Dict[ResourceType, Set[Permission]],
        inherits_from: Optional[List[str]] = None
    ) -> bool:
        """Create custom role"""
        if role_name in self.roles:
            logger.error(f"Role already exists: {role_name}")
            return False

        self.roles[role_name] = RoleDefinition(
            role_name=role_name,
            description=description,
            permissions=permissions,
            inherits_from=inherits_from or []
        )

        logger.info(f"Custom role created: {role_name}")

        return True

    def list_roles(self) -> List[Dict]:
        """List all roles"""
        return [
            {
                'role_name': role_def.role_name,
                'description': role_def.description,
                'inherits_from': role_def.inherits_from
            }
            for role_def in self.roles.values()
        ]

    def get_role_details(self, role_name: str) -> Optional[Dict]:
        """Get role details"""
        if role_name not in self.roles:
            return None

        role_def = self.roles[role_name]

        return {
            'role_name': role_def.role_name,
            'description': role_def.description,
            'inherits_from': role_def.inherits_from,
            'permissions': {
                resource.value: [perm.value for perm in perms]
                for resource, perms in role_def.permissions.items()
            }
        }


if __name__ == "__main__":
    # Example usage
    rbac = RBACService()

    # Assign roles to users
    rbac.assign_role("user_001", Role.PHYSICIAN.value)
    rbac.assign_role("user_002", Role.RESEARCHER.value)
    rbac.assign_role("user_003", Role.DATA_SCIENTIST.value)

    # Check permissions
    print("\nPermission Checks:")

    # Physician can read patient data
    can_read = rbac.check_permission("user_001", ResourceType.PATIENT_DATA, Permission.READ)
    print(f"Physician can READ patient data: {can_read}")

    # Researcher cannot write patient data
    can_write = rbac.check_permission("user_002", ResourceType.PATIENT_DATA, Permission.WRITE)
    print(f"Researcher can WRITE patient data: {can_write}")

    # Data scientist inherits from researcher
    perms = rbac.get_user_permissions("user_003")
    print(f"\nData Scientist permissions: {list(perms.keys())}")

    # List all roles
    roles = rbac.list_roles()
    print(f"\nTotal roles: {len(roles)}")

    print("\nRBAC Service ready")
