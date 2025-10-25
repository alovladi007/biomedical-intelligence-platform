"""
Authentication Service with JWT, MFA, and RBAC

Features:
- JWT-based authentication (access + refresh tokens)
- Multi-factor authentication (TOTP)
- Role-based access control (RBAC)
- Session management
- Password policies (HIPAA-compliant)
"""

import os
import secrets
import hashlib
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
MAX_FAILED_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_DURATION_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token authentication
security = HTTPBearer()


class AuthService:
    """Comprehensive authentication service"""

    def __init__(self, db_session: Session):
        self.db = db_session

    # ========================================================================
    # Password Management
    # ========================================================================

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password meets HIPAA security requirements

        Requirements:
        - Minimum 12 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(password) < 12:
            return False, "Password must be at least 12 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"

        return True, "Password is strong"

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for MFA recovery"""
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()  # 8-character hex code
            codes.append(code)
        return codes

    # ========================================================================
    # JWT Token Management
    # ========================================================================

    def create_access_token(
        self,
        user_id: int,
        username: str,
        role: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode = {
            "sub": str(user_id),
            "username": username,
            "role": role,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(
        self,
        user_id: int,
        username: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode = {
            "sub": str(user_id),
            "username": username,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Dict:
        """
        Verify JWT token and return payload

        Args:
            token: JWT token string
            token_type: Expected token type ('access' or 'refresh')

        Returns:
            Token payload dict

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Verify token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}"
                )

            return payload

        except JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # ========================================================================
    # Multi-Factor Authentication (TOTP)
    # ========================================================================

    def generate_mfa_secret(self) -> str:
        """Generate TOTP secret for MFA"""
        return pyotp.random_base32()

    def get_totp_uri(self, username: str, secret: str, issuer: str = "Biomedical Platform") -> str:
        """Get TOTP provisioning URI for QR code"""
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=issuer
        )

    def generate_mfa_qr_code(self, username: str, secret: str) -> str:
        """
        Generate QR code for MFA setup

        Returns:
            Base64-encoded PNG image
        """
        totp_uri = self.get_totp_uri(username, secret)

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return img_base64

    def verify_totp(self, secret: str, token: str) -> bool:
        """
        Verify TOTP token

        Args:
            secret: User's TOTP secret
            token: 6-digit TOTP code

        Returns:
            True if valid, False otherwise
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Allow 1 time step before/after

    # ========================================================================
    # Session Management
    # ========================================================================

    def create_session(
        self,
        user_id: int,
        ip_address: str,
        user_agent: str
    ) -> Tuple[str, str]:
        """
        Create new user session

        Returns:
            Tuple of (session_token, refresh_token)
        """
        from database.src.models import User, UserSession

        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create tokens
        access_token = self.create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role.value
        )
        refresh_token = self.create_refresh_token(
            user_id=user.id,
            username=user.username
        )

        # Create session record
        session = UserSession(
            user_id=user_id,
            session_token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            last_activity_at=datetime.utcnow()
        )

        self.db.add(session)
        self.db.commit()

        return access_token, refresh_token

    def revoke_session(self, session_token: str):
        """Revoke user session (logout)"""
        from database.src.models import UserSession

        session = self.db.query(UserSession).filter(
            UserSession.session_token == session_token
        ).first()

        if session:
            session.revoked_at = datetime.utcnow()
            self.db.commit()

    def revoke_all_user_sessions(self, user_id: int):
        """Revoke all sessions for a user"""
        from database.src.models import UserSession

        self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.revoked_at.is_(None)
        ).update({"revoked_at": datetime.utcnow()})
        self.db.commit()

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        from database.src.models import UserSession

        self.db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).delete()
        self.db.commit()

    # ========================================================================
    # Authentication Flow
    # ========================================================================

    def authenticate_user(
        self,
        username: str,
        password: str,
        mfa_token: Optional[str] = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict:
        """
        Authenticate user with username/password and optional MFA

        Returns:
            Dict with user info and tokens
        """
        from database.src.models import User
        from database.src.audit import AuditLogger

        # Get user
        user = self.db.query(User).filter(User.username == username).first()

        # Check if user exists
        if not user:
            logger.warning(f"Login attempt for non-existent user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account locked until {user.locked_until}"
            )

        # Verify password
        if not self.verify_password(password, user.password_hash):
            # Increment failed login attempts
            user.failed_login_attempts += 1

            # Lock account after max attempts
            if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=ACCOUNT_LOCKOUT_DURATION_MINUTES
                )
                logger.warning(f"Account locked due to too many failed attempts: {username}")

            self.db.commit()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )

        # Verify MFA if enabled
        if user.mfa_enabled:
            if not mfa_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="MFA token required"
                )

            if not self.verify_totp(user.mfa_secret, mfa_token):
                logger.warning(f"Invalid MFA token for user: {username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA token"
                )

        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.utcnow()
        self.db.commit()

        # Create session and tokens
        access_token, refresh_token = self.create_session(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Log successful login
        logger.info(f"Successful login: {username} from {ip_address}")

        return {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "mfa_enabled": user.mfa_enabled
        }

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh access token using refresh token

        Returns:
            New access token
        """
        # Verify refresh token
        payload = self.verify_token(refresh_token, token_type="refresh")

        user_id = int(payload["sub"])
        username = payload["username"]

        from database.src.models import User

        # Get user to get current role
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create new access token
        access_token = self.create_access_token(
            user_id=user_id,
            username=username,
            role=user.role.value
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }


# ============================================================================
# FastAPI Dependencies
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(None)  # Will be replaced with actual DB dependency
) -> Dict:
    """
    FastAPI dependency to get current authenticated user

    Usage:
        @app.get("/protected")
        async def protected_route(current_user: Dict = Depends(get_current_user)):
            return {"message": f"Hello {current_user['username']}"}
    """
    token = credentials.credentials
    auth_service = AuthService(db)
    payload = auth_service.verify_token(token, token_type="access")

    # Verify session is not revoked
    from database.src.models import UserSession

    session = db.query(UserSession).filter(
        UserSession.session_token == token,
        UserSession.revoked_at.is_(None)
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session revoked or expired"
        )

    # Update last activity
    session.last_activity_at = datetime.utcnow()
    db.commit()

    return {
        "user_id": int(payload["sub"]),
        "username": payload["username"],
        "role": payload["role"]
    }


def require_role(allowed_roles: List[str]):
    """
    FastAPI dependency to require specific roles

    Usage:
        @app.get("/admin")
        async def admin_route(
            current_user: Dict = Depends(get_current_user),
            _: None = Depends(require_role(["admin", "super_admin"]))
        ):
            return {"message": "Admin access"}
    """
    async def role_checker(current_user: Dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {allowed_roles}"
            )
        return None

    return role_checker
