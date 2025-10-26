"""User Management Endpoints - For managing user accounts"""

from __future__ import annotations

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../../../'))

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Dict, Optional
from datetime import datetime

from infrastructure.database.src.database import get_db
from infrastructure.database.src.models import User, UserRole
from infrastructure.authentication.src.auth_service import AuthService, get_current_user
from infrastructure.authentication.src.rbac_service import RBACService, AuditLogger

from app.schemas.user_schemas import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    UserFilterRequest, ResetPasswordRequest, ResetPasswordResponse,
    UserStatsResponse
)

router = APIRouter()


@router.get("/", response_model=UserListResponse)
async def list_users(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    rbac = RBACService(db)
    rbac.require_permission(current_user["user_id"], "user", "read")

    query = db.query(User)
    if role:
        query = query.filter(User.role == UserRole[role.upper()])
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
        )

    total = query.count()
    users = query.order_by(User.created_at.desc()).limit(limit).offset(offset).all()

    return UserListResponse(
        total=total,
        users=[UserResponse.from_orm(u) for u in users]
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only)"""
    rbac = RBACService(db)
    rbac.require_permission(current_user["user_id"], "user", "read")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.from_orm(user)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request_data: UserCreate,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new user (admin only)"""
    rbac = RBACService(db)
    auth_service = AuthService(db)
    rbac.require_permission(current_user["user_id"], "user", "write")

    # Check if username exists
    if db.query(User).filter(User.username == request_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    # Validate password
    is_valid, message = auth_service.validate_password_strength(request_data.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    new_user = User(
        username=request_data.username,
        email=request_data.email,
        password_hash=auth_service.hash_password(request_data.password),
        first_name=request_data.first_name,
        last_name=request_data.last_name,
        role=UserRole[request_data.role.upper()],
        department=request_data.department,
        phone=request_data.phone,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse.from_orm(new_user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    request_data: UserUpdate,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    rbac = RBACService(db)
    rbac.require_permission(current_user["user_id"], "user", "write")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = request_data.dict(exclude_unset=True)
    if "role" in update_data:
        update_data["role"] = UserRole[update_data["role"].upper()]

    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return UserResponse.from_orm(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    rbac = RBACService(db)
    rbac.require_permission(current_user["user_id"], "user", "delete")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()


@router.post("/{user_id}/reset-password", response_model=ResetPasswordResponse)
async def reset_user_password(
    user_id: int,
    request_data: ResetPasswordRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset user password (admin only)"""
    rbac = RBACService(db)
    auth_service = AuthService(db)
    rbac.require_permission(current_user["user_id"], "user", "write")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    is_valid, message = auth_service.validate_password_strength(request_data.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    user.password_hash = auth_service.hash_password(request_data.new_password)
    user.must_change_password = request_data.must_change_password
    user.password_changed_at = datetime.utcnow()
    db.commit()

    return ResetPasswordResponse(
        success=True,
        message="Password reset successfully"
    )


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics (admin only)"""
    rbac = RBACService(db)
    rbac.require_permission(current_user["user_id"], "user", "read")

    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    inactive_users = total_users - active_users
    mfa_enabled_users = db.query(User).filter(User.mfa_enabled == True).count()

    users_by_role = {}
    role_counts = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    for role, count in role_counts:
        users_by_role[role.value] = count

    return UserStatsResponse(
        total_users=total_users,
        users_by_role=users_by_role,
        active_users=active_users,
        inactive_users=inactive_users,
        mfa_enabled_users=mfa_enabled_users,
        mfa_enabled_percentage=round((mfa_enabled_users / total_users * 100) if total_users > 0 else 0, 1)
    )
