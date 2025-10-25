"""
Auth Dashboard Service - Central Authentication & Data API

This service provides:
- Authentication endpoints (login, register, MFA)
- Patient management endpoints
- Prediction history endpoints
- User profile endpoints
- Admin endpoints

Port: 8100
"""

import os
import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

# Add parent directory to path to import infrastructure modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from infrastructure.database.src.database import init_database
from infrastructure.monitoring.src.monitoring_service import MonitoringService
from infrastructure.authentication.src.rbac_service import RBACService

# Import routers
from app.api.v1.endpoints import auth, patients, predictions, users, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize monitoring
monitoring = MonitoringService("auth-dashboard-service")


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting Auth Dashboard Service...")

    # Initialize database
    database_url = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/biomedical_platform'
    )
    db_manager = init_database(database_url=database_url, echo=False)
    logger.info("Database initialized")

    # Initialize RBAC permissions
    try:
        with db_manager.get_session() as db:
            rbac = RBACService(db)
            rbac.initialize_default_permissions()
            rbac.initialize_default_role_permissions()
            logger.info("RBAC permissions initialized")
    except Exception as e:
        logger.warning(f"RBAC initialization: {str(e)}")

    # Health check
    if db_manager.health_check():
        logger.info("Database health check passed")
    else:
        logger.error("Database health check failed!")

    logger.info("Auth Dashboard Service started successfully on port 8100")

    yield

    # Shutdown
    logger.info("Shutting down Auth Dashboard Service...")


# Create FastAPI app
app = FastAPI(
    title="Auth Dashboard Service",
    description="Central Authentication & Data API for Biomedical Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Main dashboard frontend
        "http://localhost:3001",  # Medical imaging frontend
        "http://localhost:3002",  # AI diagnostics frontend
        "http://localhost:3007",  # Genomic intelligence frontend
        "http://localhost:3010",  # OBiCare frontend
        "http://localhost:3011",  # HIPAA monitor frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and track metrics"""
    start_time = time.time()

    # Process request
    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # Record metrics
        monitoring.record_http_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration_seconds=duration
        )

        # Log request
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration:.3f}s"
        )

        return response

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url.path} - {str(e)}")

        # Record error
        monitoring.record_http_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=500,
            duration_seconds=duration
        )

        raise


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status_code": 500
        }
    )


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(patients.router, prefix="/api/patients", tags=["Patients"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": "Auth Dashboard Service",
        "version": "1.0.0",
        "status": "running",
        "port": 8100,
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    from infrastructure.database.src.database import db_manager

    db_healthy = db_manager.health_check() if db_manager else False

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "auth-dashboard-service",
        "database": "connected" if db_healthy else "disconnected",
        "port": 8100,
        "version": "1.0.0"
    }


# Metrics endpoint for Prometheus
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    return monitoring.get_prometheus_metrics()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8100,
        reload=True,
        log_level="info"
    )
