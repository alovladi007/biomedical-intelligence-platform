"""
Unified API Gateway for Biomedical Intelligence Platform
Integrates all services with core infrastructure (auth, audit, data pipeline)
"""

import sys
import os
from pathlib import Path

# Add core-infrastructure to path
core_path = Path(__file__).parent.parent / 'core-infrastructure'
sys.path.insert(0, str(core_path))

from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Optional, Dict
from datetime import datetime
import httpx

# Import core infrastructure
from auth_service.src.auth_service import AuthenticationService, TokenType
from auth_service.src.rbac_service import RBACService, ResourceType, Permission
from audit_service.src.audit_logger import AuditLogger, AuditEventType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Biomedical Intelligence Platform API",
    description="Unified API Gateway with HIPAA compliance",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core services
auth_service = AuthenticationService(
    jwt_secret=os.getenv("JWT_SECRET", "change-this-secret-in-production"),
    jwt_algorithm="HS256"
)

rbac_service = RBACService()
audit_logger = AuditLogger(enable_real_time_alerts=True)

# Service endpoints (microservices)
SERVICES = {
    'medical-imaging': 'http://localhost:5001',
    'ai-diagnostics': 'http://localhost:5002',
    'biosensing': 'http://localhost:5003',
    'cloud-ehr': 'http://localhost:5004',
    'clinical-trials': 'http://localhost:5005',
    'telemedicine': 'http://localhost:5006',
    'genomic-intelligence': 'http://localhost:5007',
    'drug-discovery': 'http://localhost:5008'
}

# ==================== AUTHENTICATION MIDDLEWARE ====================

async def verify_token(authorization: Optional[str] = Header(None)) -> Dict:
    """Verify JWT token and return payload"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization.replace("Bearer ", "")

    is_valid, error, payload = auth_service.verify_token(token, TokenType.ACCESS)

    if not is_valid:
        raise HTTPException(status_code=401, detail=error)

    return payload


async def check_permission(
    request: Request,
    user_payload: Dict,
    resource_type: ResourceType,
    permission: Permission
):
    """Check if user has permission for resource"""
    user_id = user_payload['sub']

    has_permission = rbac_service.check_permission(
        user_id,
        resource_type,
        permission
    )

    if not has_permission:
        # Log access denied
        audit_logger.log_access_denied(
            user_id=user_id,
            user_name=user_payload['username'],
            resource_type=resource_type.value,
            resource_id=str(request.url),
            required_permission=permission.value,
            ip_address=request.client.host
        )

        raise HTTPException(status_code=403, detail="Insufficient permissions")


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/register")
async def register(request: Request):
    """Register new user"""
    data = await request.json()

    success, error, user = auth_service.register_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        roles=data.get('roles', ['api_user']),
        mfa_enabled=data.get('mfa_enabled', False)
    )

    if not success:
        raise HTTPException(status_code=400, detail=error)

    # Assign roles in RBAC
    for role in data.get('roles', ['api_user']):
        rbac_service.assign_role(user.user_id, role)

    return {
        'success': True,
        'user_id': user.user_id,
        'username': user.username
    }


@app.post("/api/auth/login")
async def login(request: Request):
    """Authenticate user"""
    data = await request.json()

    success, error, tokens = auth_service.authenticate(
        username=data['username'],
        password=data['password'],
        mfa_code=data.get('mfa_code'),
        ip_address=request.client.host
    )

    if not success:
        # Log failed authentication
        audit_logger.log_authentication(
            user_id="unknown",
            user_name=data['username'],
            ip_address=request.client.host,
            success=False,
            failure_reason=error
        )

        raise HTTPException(status_code=401, detail=error)

    # Log successful authentication
    user = auth_service.get_user(data['username'])
    audit_logger.log_authentication(
        user_id=user.user_id,
        user_name=user.username,
        ip_address=request.client.host,
        success=True
    )

    return tokens


@app.post("/api/auth/refresh")
async def refresh_token(request: Request):
    """Refresh access token"""
    data = await request.json()

    success, error, new_tokens = auth_service.refresh_access_token(
        data['refresh_token']
    )

    if not success:
        raise HTTPException(status_code=401, detail=error)

    return new_tokens


@app.post("/api/auth/logout")
async def logout(user_payload: Dict = Depends(verify_token)):
    """Logout user"""
    # End session would go here
    return {'success': True, 'message': 'Logged out successfully'}


# ==================== SERVICE PROXY ENDPOINTS ====================

@app.api_route("/api/services/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_service(
    service_name: str,
    path: str,
    request: Request,
    user_payload: Dict = Depends(verify_token)
):
    """
    Proxy requests to microservices with authentication and audit logging
    """
    # Check if service exists
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

    # Map service to resource type for RBAC
    resource_map = {
        'medical-imaging': ResourceType.DICOM_STUDY,
        'genomic-intelligence': ResourceType.GENOMIC_DATA,
        'ai-diagnostics': ResourceType.MEDICAL_RECORD,
        'biosensing': ResourceType.LAB_RESULTS,
        'cloud-ehr': ResourceType.MEDICAL_RECORD,
        'drug-discovery': ResourceType.MODEL_PREDICTION
    }

    resource_type = resource_map.get(service_name, ResourceType.MODEL_PREDICTION)

    # Determine required permission based on HTTP method
    permission_map = {
        'GET': Permission.READ,
        'POST': Permission.WRITE,
        'PUT': Permission.UPDATE,
        'DELETE': Permission.DELETE
    }

    required_permission = permission_map.get(request.method, Permission.READ)

    # Check permission
    await check_permission(request, user_payload, resource_type, required_permission)

    # Build target URL
    service_url = SERVICES[service_name]
    target_url = f"{service_url}/{path}"

    # Get request body if present
    body = None
    if request.method in ['POST', 'PUT']:
        body = await request.body()

    # Forward request to microservice
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=dict(request.headers),
                params=dict(request.query_params),
                timeout=30.0
            )

        # Log successful API call
        audit_logger.log_event(
            event_type=AuditEventType.MODEL_PREDICTION if 'predict' in path else AuditEventType.PHI_READ,
            user_id=user_payload['sub'],
            user_name=user_payload['username'],
            action=request.method,
            resource_type=service_name,
            resource_id=path,
            ip_address=request.client.host,
            success=True,
            details={
                'service': service_name,
                'endpoint': path,
                'status_code': response.status_code
            }
        )

        # Return service response
        return JSONResponse(
            content=response.json() if response.headers.get('content-type', '').startswith('application/json') else {'data': response.text},
            status_code=response.status_code
        )

    except httpx.HTTPError as e:
        logger.error(f"Service {service_name} error: {str(e)}")

        # Log failed request
        audit_logger.log_event(
            event_type=AuditEventType.PHI_READ,
            user_id=user_payload['sub'],
            user_name=user_payload['username'],
            action=request.method,
            resource_type=service_name,
            resource_id=path,
            ip_address=request.client.host,
            success=False,
            failure_reason=str(e)
        )

        raise HTTPException(status_code=503, detail=f"Service {service_name} unavailable")


# ==================== AUDIT ENDPOINTS ====================

@app.get("/api/audit/patient/{patient_id}")
async def get_patient_audit_log(
    patient_id: str,
    days: int = 30,
    user_payload: Dict = Depends(verify_token)
):
    """Get audit log for patient (HIPAA requirement)"""
    # Check permission
    if not rbac_service.check_permission(
        user_payload['sub'],
        ResourceType.AUDIT_LOG,
        Permission.READ
    ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    access_log = audit_logger.get_patient_access_log(patient_id, days)

    return {
        'patient_id': patient_id,
        'days': days,
        'total_events': len(access_log),
        'events': access_log
    }


@app.get("/api/audit/statistics")
async def get_audit_statistics(user_payload: Dict = Depends(verify_token)):
    """Get audit statistics"""
    # Check permission
    if not rbac_service.check_permission(
        user_payload['sub'],
        ResourceType.AUDIT_LOG,
        Permission.READ
    ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    stats = audit_logger.get_statistics()

    return stats


# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            name: 'unknown' for name in SERVICES.keys()
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        'name': 'Biomedical Intelligence Platform API',
        'version': '1.0.0',
        'status': 'operational',
        'documentation': '/docs',
        'services': list(SERVICES.keys())
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Unified API Gateway...")
    logger.info(f"Available services: {list(SERVICES.keys())}")

    # Register demo users
    auth_service.register_user(
        username="demo_physician",
        email="physician@demo.com",
        password="DemoPass123!@#",
        roles=["physician"]
    )
    rbac_service.assign_role("demo_physician", "physician")

    auth_service.register_user(
        username="demo_researcher",
        email="researcher@demo.com",
        password="DemoPass123!@#",
        roles=["researcher"]
    )
    rbac_service.assign_role("demo_researcher", "researcher")

    logger.info("Demo users created: demo_physician, demo_researcher")

    uvicorn.run(app, host="0.0.0.0", port=8000)
