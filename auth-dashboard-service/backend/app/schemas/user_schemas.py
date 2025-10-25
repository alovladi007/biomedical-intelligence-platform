"""User management schemas"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    """Create user request schema (admin only)"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=12)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., description="User role")
    department: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class UserUpdate(BaseModel):
    """Update user request schema"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response schema"""
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
    is_verified: bool
    email_verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """User list response schema"""
    total: int
    users: List[UserResponse]


class UserFilterRequest(BaseModel):
    """User filter request schema"""
    role: Optional[str] = None
    is_active: Optional[bool] = None
    department: Optional[str] = None
    search: Optional[str] = Field(None, description="Search by username, email, or name")
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class ResetPasswordRequest(BaseModel):
    """Reset password request schema (admin)"""
    new_password: str = Field(..., min_length=12)
    must_change_password: bool = Field(True, description="Force user to change password on next login")


class ResetPasswordResponse(BaseModel):
    """Reset password response schema"""
    success: bool
    message: str


class UserStatsResponse(BaseModel):
    """User statistics response schema"""
    total_users: int
    users_by_role: dict
    active_users: int
    inactive_users: int
    mfa_enabled_users: int
    mfa_enabled_percentage: float
