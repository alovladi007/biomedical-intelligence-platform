"""
HIPAA Audit Logging Service
Comprehensive audit trail for PHI access and system events per 45 CFR § 164.312(b)
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """HIPAA-required audit event types"""
    # PHI Access Events
    PHI_READ = "phi_read"
    PHI_WRITE = "phi_write"
    PHI_UPDATE = "phi_update"
    PHI_DELETE = "phi_delete"
    PHI_EXPORT = "phi_export"

    # Authentication Events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    SESSION_EXPIRED = "session_expired"
    PASSWORD_CHANGE = "password_change"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"

    # Authorization Events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGED = "permission_changed"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REVOKED = "role_revoked"

    # Data Events
    DATA_CREATED = "data_created"
    DATA_MODIFIED = "data_modified"
    DATA_DELETED = "data_deleted"
    DATA_ARCHIVED = "data_archived"

    # System Events
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    CONFIG_CHANGE = "config_change"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"

    # Security Events
    ENCRYPTION_KEY_ROTATION = "encryption_key_rotation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_ALERT = "security_alert"
    BREACH_DETECTED = "breach_detected"

    # ML Model Events
    MODEL_DEPLOYED = "model_deployed"
    MODEL_PREDICTION = "model_prediction"
    MODEL_UPDATED = "model_updated"
    MODEL_ARCHIVED = "model_archived"


class AuditSeverity(Enum):
    """Audit event severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """HIPAA-compliant audit event"""
    # Required fields (45 CFR § 164.312(b))
    timestamp: str
    event_type: str
    user_id: str
    user_name: str
    action: str
    resource_type: str
    resource_id: Optional[str]
    patient_id: Optional[str]  # For PHI access

    # Context
    ip_address: str
    user_agent: Optional[str]
    session_id: Optional[str]

    # Outcome
    success: bool
    failure_reason: Optional[str]

    # Additional metadata
    severity: str
    details: Dict[str, Any]

    # Integrity
    event_id: str = None
    checksum: str = None

    def __post_init__(self):
        """Generate event ID and checksum"""
        if not self.event_id:
            self.event_id = self._generate_event_id()

        if not self.checksum:
            self.checksum = self._generate_checksum()

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import secrets
        return f"audit_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(8)}"

    def _generate_checksum(self) -> str:
        """Generate checksum for integrity verification"""
        data = f"{self.timestamp}{self.event_type}{self.user_id}{self.action}{self.resource_type}{self.resource_id}"
        return hashlib.sha256(data.encode()).hexdigest()


class AuditLogger:
    """
    HIPAA-compliant audit logging service

    Requirements (45 CFR § 164.312(b)):
    - Log all PHI access (read, write, update, delete)
    - Record user identity, timestamp, action
    - Include patient identifier
    - Maintain log integrity
    - Retain logs for 6 years
    - Support audit trail review
    """

    def __init__(
        self,
        storage_backend: str = "local",
        retention_days: int = 2190,  # 6 years
        enable_real_time_alerts: bool = True
    ):
        """
        Initialize audit logger

        Args:
            storage_backend: Storage backend (local, postgresql, s3, siem)
            retention_days: Log retention period (default: 6 years)
            enable_real_time_alerts: Enable real-time security alerts
        """
        self.storage_backend = storage_backend
        self.retention_days = retention_days
        self.enable_real_time_alerts = enable_real_time_alerts

        # In-memory buffer (flush to storage periodically)
        self.event_buffer: List[AuditEvent] = []
        self.buffer_max_size = 1000

        # Statistics
        self.stats = {
            'total_events': 0,
            'phi_access_events': 0,
            'failed_auth_events': 0,
            'security_events': 0
        }

        logger.info(f"Audit Logger initialized (retention: {retention_days} days)")

    # ==================== AUDIT LOGGING ====================

    def log_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        user_name: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        ip_address: str = "0.0.0.0",
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        success: bool = True,
        failure_reason: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        details: Optional[Dict] = None
    ) -> str:
        """
        Log audit event

        Args:
            event_type: Type of event
            user_id: User identifier
            user_name: Username
            action: Action performed
            resource_type: Type of resource accessed
            resource_id: Resource identifier
            patient_id: Patient identifier (for PHI access)
            ip_address: Client IP address
            user_agent: User agent string
            session_id: Session identifier
            success: Whether action succeeded
            failure_reason: Reason for failure
            severity: Event severity
            details: Additional metadata

        Returns:
            Event ID
        """
        event = AuditEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type.value,
            user_id=user_id,
            user_name=user_name,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            patient_id=patient_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            success=success,
            failure_reason=failure_reason,
            severity=severity.value,
            details=details or {}
        )

        # Add to buffer
        self.event_buffer.append(event)

        # Update statistics
        self._update_stats(event)

        # Flush if buffer full
        if len(self.event_buffer) >= self.buffer_max_size:
            self._flush_buffer()

        # Real-time alerts for critical events
        if self.enable_real_time_alerts and severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
            self._send_alert(event)

        logger.debug(f"Audit event logged: {event.event_id} ({event_type.value})")

        return event.event_id

    # ==================== PHI ACCESS LOGGING ====================

    def log_phi_access(
        self,
        user_id: str,
        user_name: str,
        patient_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        ip_address: str,
        success: bool = True,
        details: Optional[Dict] = None
    ) -> str:
        """
        Log PHI access event (HIPAA required)

        Args:
            user_id: User accessing PHI
            user_name: Username
            patient_id: Patient whose data was accessed
            action: Action performed (read, write, update, delete)
            resource_type: Type of PHI (medical_record, dicom_study, etc.)
            resource_id: Specific resource accessed
            ip_address: Client IP
            success: Whether access succeeded
            details: Additional context

        Returns:
            Event ID
        """
        # Determine event type based on action
        event_type_map = {
            'read': AuditEventType.PHI_READ,
            'write': AuditEventType.PHI_WRITE,
            'update': AuditEventType.PHI_UPDATE,
            'delete': AuditEventType.PHI_DELETE,
            'export': AuditEventType.PHI_EXPORT
        }

        event_type = event_type_map.get(action.lower(), AuditEventType.PHI_READ)

        return self.log_event(
            event_type=event_type,
            user_id=user_id,
            user_name=user_name,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            patient_id=patient_id,
            ip_address=ip_address,
            success=success,
            severity=AuditSeverity.INFO,
            details=details
        )

    def log_authentication(
        self,
        user_id: str,
        user_name: str,
        ip_address: str,
        success: bool,
        auth_method: str = "password",
        failure_reason: Optional[str] = None
    ) -> str:
        """Log authentication event"""
        event_type = AuditEventType.LOGIN_SUCCESS if success else AuditEventType.LOGIN_FAILURE
        severity = AuditSeverity.INFO if success else AuditSeverity.WARNING

        return self.log_event(
            event_type=event_type,
            user_id=user_id,
            user_name=user_name,
            action="authenticate",
            resource_type="authentication",
            ip_address=ip_address,
            success=success,
            failure_reason=failure_reason,
            severity=severity,
            details={'auth_method': auth_method}
        )

    def log_access_denied(
        self,
        user_id: str,
        user_name: str,
        resource_type: str,
        resource_id: str,
        required_permission: str,
        ip_address: str
    ) -> str:
        """Log access denied event"""
        return self.log_event(
            event_type=AuditEventType.ACCESS_DENIED,
            user_id=user_id,
            user_name=user_name,
            action="access_denied",
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            success=False,
            failure_reason=f"Missing permission: {required_permission}",
            severity=AuditSeverity.WARNING,
            details={'required_permission': required_permission}
        )

    # ==================== QUERYING ====================

    def query_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        resource_type: Optional[str] = None,
        success: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query audit events

        Args:
            start_time: Start of time range
            end_time: End of time range
            user_id: Filter by user
            patient_id: Filter by patient
            event_type: Filter by event type
            resource_type: Filter by resource type
            success: Filter by success/failure
            limit: Maximum results

        Returns:
            List of matching audit events
        """
        # Filter events
        results = []

        for event in self.event_buffer:
            # Time range filter
            if start_time or end_time:
                event_time = datetime.fromisoformat(event.timestamp)
                if start_time and event_time < start_time:
                    continue
                if end_time and event_time > end_time:
                    continue

            # User filter
            if user_id and event.user_id != user_id:
                continue

            # Patient filter
            if patient_id and event.patient_id != patient_id:
                continue

            # Event type filter
            if event_type and event.event_type != event_type.value:
                continue

            # Resource type filter
            if resource_type and event.resource_type != resource_type:
                continue

            # Success filter
            if success is not None and event.success != success:
                continue

            results.append(asdict(event))

            if len(results) >= limit:
                break

        return results

    def get_patient_access_log(
        self,
        patient_id: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Get complete access log for patient (HIPAA requirement)

        Args:
            patient_id: Patient identifier
            days: Number of days to look back

        Returns:
            All PHI access events for patient
        """
        start_time = datetime.utcnow() - timedelta(days=days)

        return self.query_events(
            start_time=start_time,
            patient_id=patient_id
        )

    def get_user_activity(
        self,
        user_id: str,
        days: int = 7
    ) -> List[Dict]:
        """Get user activity log"""
        start_time = datetime.utcnow() - timedelta(days=days)

        return self.query_events(
            start_time=start_time,
            user_id=user_id
        )

    # ==================== STATISTICS & REPORTING ====================

    def _update_stats(self, event: AuditEvent):
        """Update statistics"""
        self.stats['total_events'] += 1

        if event.patient_id:
            self.stats['phi_access_events'] += 1

        if event.event_type == AuditEventType.LOGIN_FAILURE.value:
            self.stats['failed_auth_events'] += 1

        if event.severity in [AuditSeverity.ERROR.value, AuditSeverity.CRITICAL.value]:
            self.stats['security_events'] += 1

    def get_statistics(self) -> Dict:
        """Get audit statistics"""
        return {
            **self.stats,
            'buffer_size': len(self.event_buffer),
            'timestamp': datetime.utcnow().isoformat()
        }

    def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Generate HIPAA compliance report

        Returns:
            Compliance metrics
        """
        events = self.query_events(
            start_time=start_date,
            end_time=end_date,
            limit=10000
        )

        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_events': len(events),
                'phi_access_count': len([e for e in events if e.get('patient_id')]),
                'failed_access_attempts': len([e for e in events if not e['success']]),
                'unique_users': len(set(e['user_id'] for e in events)),
                'unique_patients': len(set(e['patient_id'] for e in events if e.get('patient_id')))
            },
            'by_event_type': {},
            'by_user': {},
            'security_events': [e for e in events if e['severity'] in ['error', 'critical']]
        }

        # Count by event type
        for event in events:
            event_type = event['event_type']
            report['by_event_type'][event_type] = report['by_event_type'].get(event_type, 0) + 1

        # Count by user
        for event in events:
            user_id = event['user_id']
            report['by_user'][user_id] = report['by_user'].get(user_id, 0) + 1

        return report

    # ==================== STORAGE & ALERTS ====================

    def _flush_buffer(self):
        """Flush event buffer to storage"""
        if not self.event_buffer:
            return

        # In production, write to database or SIEM
        logger.info(f"Flushing {len(self.event_buffer)} audit events to storage")

        # For now, just clear buffer
        self.event_buffer = []

    def _send_alert(self, event: AuditEvent):
        """Send real-time alert for critical events"""
        logger.warning(f"SECURITY ALERT: {event.event_type} - {event.action} by {event.user_name}")

        # In production, integrate with alerting system
        # (Splunk, PagerDuty, AWS SNS, etc.)


if __name__ == "__main__":
    # Example usage
    audit_logger = AuditLogger(storage_backend="local", enable_real_time_alerts=True)

    # Log PHI access
    event_id = audit_logger.log_phi_access(
        user_id="user_001",
        user_name="dr_smith",
        patient_id="PATIENT_12345",
        action="read",
        resource_type="medical_record",
        resource_id="record_789",
        ip_address="10.0.1.50",
        success=True,
        details={'record_type': 'lab_results'}
    )

    print(f"PHI access logged: {event_id}")

    # Log failed authentication
    audit_logger.log_authentication(
        user_id="user_002",
        user_name="unknown_user",
        ip_address="192.168.1.100",
        success=False,
        failure_reason="Invalid credentials"
    )

    # Query patient access log
    access_log = audit_logger.get_patient_access_log("PATIENT_12345", days=30)
    print(f"\nPatient access log entries: {len(access_log)}")

    # Get statistics
    stats = audit_logger.get_statistics()
    print(f"\nAudit Statistics:")
    print(f"Total events: {stats['total_events']}")
    print(f"PHI access events: {stats['phi_access_events']}")

    print("\nAudit Logger ready")
