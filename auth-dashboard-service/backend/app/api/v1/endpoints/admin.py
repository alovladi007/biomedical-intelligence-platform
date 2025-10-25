"""Admin Endpoints - RBAC, Audit Logs, System Configuration"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../../../'))

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from infrastructure.database.src.database import get_db
from infrastructure.database.src.models import AuditLog, Permission, RolePermission
from infrastructure.authentication.src.auth_service import get_current_user
from infrastructure.authentication.src.rbac_service import RBACService
from pydantic import BaseModel

router = APIRouter()


class PermissionResponse(BaseModel):
    id: int
    name: str
    resource: str
    action: str
    description: Optional[str]

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: Optional[str]
    user_role: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[int]
    method: Optional[str]
    endpoint: Optional[str]
    status_code: Optional[int]
    ip_address: Optional[str]
    phi_accessed: bool
    patient_id: Optional[int]
    is_security_event: bool
    severity: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all permissions (admin only)"""
    rbac = RBACService(db)
    rbac.require_permission(current_user["user_id"], "config", "read")

    permissions = db.query(Permission).order_by(Permission.resource, Permission.action).all()
    return [PermissionResponse.from_orm(p) for p in permissions]


@router.get("/permissions/role/{role}")
async def get_role_permissions(
    role: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get permissions for a specific role (admin only)"""
    rbac = RBACService(db)
    rbac.require_permission(current_user["user_id"], "config", "read")

    return rbac.get_role_permissions(role)


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    phi_accessed: Optional[bool] = Query(None),
    is_security_event: Optional[bool] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs with filtering (admin/auditor only)"""
    rbac = RBACService(db)
    rbac.require_permission(current_user["user_id"], "audit", "read")

    query = db.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if severity:
        query = query.filter(AuditLog.severity == severity)
    if phi_accessed is not None:
        query = query.filter(AuditLog.phi_accessed == phi_accessed)
    if is_security_event is not None:
        query = query.filter(AuditLog.is_security_event == is_security_event)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)

    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()
    return [AuditLogResponse.from_orm(log) for log in logs]


@router.get("/audit-logs/security-events", response_model=List[AuditLogResponse])
async def get_security_events(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    severity: Optional[str] = Query(None),
    hours: int = Query(24, description="Number of hours to look back"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent security events (admin/auditor only)"""
    rbac = RBACService(db)
    rbac.require_permission(current_user["user_id"], "audit", "read")

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    query = db.query(AuditLog).filter(
        AuditLog.is_security_event == True,
        AuditLog.created_at >= cutoff_time
    )

    if severity:
        query = query.filter(AuditLog.severity == severity)

    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()
    return [AuditLogResponse.from_orm(log) for log in logs]


@router.get("/audit-logs/phi-access", response_model=List[AuditLogResponse])
async def get_phi_access_logs(
    patient_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    hours: int = Query(24, description="Number of hours to look back"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get PHI access logs (admin/auditor only)"""
    rbac = RBACService(db)
    rbac.require_permission(current_user["user_id"], "audit", "read")

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    query = db.query(AuditLog).filter(
        AuditLog.phi_accessed == True,
        AuditLog.created_at >= cutoff_time
    )

    if patient_id:
        query = query.filter(AuditLog.patient_id == patient_id)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()
    return [AuditLogResponse.from_orm(log) for log in logs]


@router.get("/system/health")
async def system_health(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system health status (admin only)"""
    rbac = RBACService(db)
    rbac.require_permission(current_user["user_id"], "config", "read")

    from infrastructure.database.src.database import db_manager

    return {
        "database": {
            "status": "connected" if db_manager.health_check() else "disconnected",
            "pool_size": db_manager.engine.pool.size(),
            "checked_in_connections": db_manager.engine.pool.checkedin()
        },
        "timestamp": datetime.utcnow().isoformat()
    }
