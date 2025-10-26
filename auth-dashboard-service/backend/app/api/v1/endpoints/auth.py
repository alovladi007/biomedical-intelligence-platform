"""
Authentication Endpoints

Endpoints:
- POST /auth/register - Register new user
- POST /auth/login - Login user
- POST /auth/logout - Logout user
- POST /auth/refresh - Refresh access token
- POST /auth/mfa/setup - Setup MFA
- POST /auth/mfa/verify - Verify and enable MFA
- POST /auth/mfa/disable - Disable MFA
- GET /auth/me - Get current user profile
- POST /auth/change-password - Change password
"""

from __future__ import annotations

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../../../'))

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict
from slowapi import Limiter
from slowapi.util import get_remote_address

from infrastructure.database.src.database import get_db
from infrastructure.database.src.models import User, UserRole
from infrastructure.authentication.src.auth_service import AuthService, get_current_user
from infrastructure.authentication.src.rbac_service import AuditLogger

from app.schemas.auth_schemas import (
    LoginRequest, LoginResponse,
    RegisterRequest, RegisterResponse,
    MFASetupResponse, MFAVerifyRequest, MFAVerifyResponse,
    RefreshTokenRequest, RefreshTokenResponse,
    UserProfileResponse,
    ChangePasswordRequest, ChangePasswordResponse,
    LogoutResponse
)

router = APIRouter()

# Rate limiter for authentication endpoints
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")  # Limit registration to 10 per minute
async def register(
    request_data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user

    Creates a new user account with the specified role.
    Default role is 'patient' if not specified.
    """
    auth_service = AuthService(db)
    audit_logger = AuditLogger(db)

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == request_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate password strength
    is_valid, message = auth_service.validate_password_strength(request_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Hash password
    password_hash = auth_service.hash_password(request_data.password)

    # Map role string to UserRole enum
    try:
        role_enum = UserRole[request_data.role.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {request_data.role}"
        )

    # Create user
    new_user = User(
        username=request_data.username,
        email=request_data.email,
        password_hash=password_hash,
        first_name=request_data.first_name,
        last_name=request_data.last_name,
        role=role_enum,
        department=request_data.department,
        phone=request_data.phone,
        is_active=True,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log registration
    audit_logger.log_event(
        user_id=new_user.id,
        action="user_registered",
        resource_type="user",
        resource_id=new_user.id,
        method="POST",
        endpoint="/auth/register",
        status_code=201,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        severity="info"
    )

    return RegisterResponse(
        user_id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role.value,
        message="User registered successfully"
    )


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")  # Strict limit for login to prevent brute force
async def login(
    request_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login user

    Authenticates user with username/password and optional MFA token.
    Returns access token and refresh token.
    """
    auth_service = AuthService(db)
    audit_logger = AuditLogger(db)

    try:
        result = auth_service.authenticate_user(
            username=request_data.username,
            password=request_data.password,
            mfa_token=request_data.mfa_token,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

        # Log successful login
        audit_logger.log_event(
            user_id=result["user_id"],
            action="login_success",
            method="POST",
            endpoint="/auth/login",
            status_code=200,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            severity="info"
        )

        return LoginResponse(**result)

    except HTTPException as e:
        # Log failed login
        audit_logger.log_security_event(
            event_type="login_failed",
            severity="warning",
            ip_address=request.client.host,
            details={"username": request_data.username, "reason": str(e.detail)}
        )
        raise


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user

    Revokes current session.
    """
    auth_service = AuthService(db)
    audit_logger = AuditLogger(db)

    # Get token from header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        auth_service.revoke_session(token)

    # Log logout
    audit_logger.log_event(
        user_id=current_user["user_id"],
        action="logout",
        method="POST",
        endpoint="/auth/logout",
        status_code=200,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        severity="info"
    )

    return LogoutResponse(
        success=True,
        message="Logged out successfully"
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token

    Uses refresh token to get a new access token.
    """
    auth_service = AuthService(db)

    result = auth_service.refresh_access_token(request_data.refresh_token)

    return RefreshTokenResponse(**result)


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Setup MFA for current user

    Generates TOTP secret and QR code for authenticator app.
    Returns backup codes for recovery.
    """
    auth_service = AuthService(db)

    # Get user
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate MFA secret
    secret = auth_service.generate_mfa_secret()

    # Generate QR code
    qr_code_image = auth_service.generate_mfa_qr_code(user.username, secret)

    # Get provisioning URI
    totp_uri = auth_service.get_totp_uri(user.username, secret)

    # Generate backup codes
    backup_codes = auth_service.generate_backup_codes()

    # Store secret and backup codes (temporarily, until verified)
    user.mfa_secret = secret
    user.backup_codes = {"codes": [auth_service.hash_password(code) for code in backup_codes]}
    db.commit()

    return MFASetupResponse(
        qr_code_url=totp_uri,
        qr_code_image=qr_code_image,
        secret=secret,
        backup_codes=backup_codes
    )


@router.post("/mfa/verify", response_model=MFAVerifyResponse)
async def verify_mfa(
    request_data: MFAVerifyRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify MFA setup

    Verifies the TOTP code from authenticator app and enables MFA.
    """
    auth_service = AuthService(db)

    # Get user
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not set up. Please call /mfa/setup first"
        )

    # Verify TOTP code
    if not auth_service.verify_totp(user.mfa_secret, request_data.mfa_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA token"
        )

    # Enable MFA
    user.mfa_enabled = True
    db.commit()

    return MFAVerifyResponse(
        success=True,
        message="MFA enabled successfully",
        mfa_enabled=True
    )


@router.post("/mfa/disable", response_model=MFAVerifyResponse)
async def disable_mfa(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable MFA for current user
    """
    # Get user
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Disable MFA
    user.mfa_enabled = False
    user.mfa_secret = None
    user.backup_codes = None
    db.commit()

    return MFAVerifyResponse(
        success=True,
        message="MFA disabled successfully",
        mfa_enabled=False
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile

    Returns profile information for the authenticated user.
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        department=user.department,
        phone=user.phone,
        mfa_enabled=user.mfa_enabled,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at
    )


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request_data: ChangePasswordRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for current user

    Requires current password for verification.
    """
    auth_service = AuthService(db)

    # Get user
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify current password
    if not auth_service.verify_password(request_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Check if new passwords match
    if request_data.new_password != request_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )

    # Validate new password strength
    is_valid, message = auth_service.validate_password_strength(request_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Update password
    user.password_hash = auth_service.hash_password(request_data.new_password)
    from datetime import datetime
    user.password_changed_at = datetime.utcnow()
    db.commit()

    return ChangePasswordResponse(
        success=True,
        message="Password changed successfully"
    )
