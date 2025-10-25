"""Authentication request/response schemas"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., min_length=1, description="Password")
    mfa_token: Optional[str] = Field(None, min_length=6, max_length=6, description="MFA token (if enabled)")


class LoginResponse(BaseModel):
    """Login response schema"""
    user_id: int
    username: str
    role: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    mfa_enabled: bool


class RegisterRequest(BaseModel):
    """User registration request schema"""
    username: str = Field(..., min_length=3, max_length=100, description="Unique username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=12, description="Password (min 12 characters)")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field("patient", description="User role (default: patient)")


class RegisterResponse(BaseModel):
    """User registration response schema"""
    user_id: int
    username: str
    email: str
    role: str
    message: str


class MFASetupRequest(BaseModel):
    """MFA setup request schema"""
    pass  # No body needed, user is authenticated


class MFASetupResponse(BaseModel):
    """MFA setup response schema"""
    qr_code_url: str = Field(..., description="TOTP provisioning URI")
    qr_code_image: str = Field(..., description="Base64 encoded QR code image")
    secret: str = Field(..., description="TOTP secret (for manual entry)")
    backup_codes: List[str] = Field(..., description="Backup codes for recovery")


class MFAVerifyRequest(BaseModel):
    """MFA verification request schema"""
    mfa_token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code")


class MFAVerifyResponse(BaseModel):
    """MFA verification response schema"""
    success: bool
    message: str
    mfa_enabled: bool


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema"""
    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    """User profile response schema"""
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    department: Optional[str]
    phone: Optional[str]
    mfa_enabled: bool
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=12, description="New password (min 12 characters)")
    confirm_password: str = Field(..., min_length=12)


class ChangePasswordResponse(BaseModel):
    """Change password response schema"""
    success: bool
    message: str


class LogoutResponse(BaseModel):
    """Logout response schema"""
    success: bool
    message: str
