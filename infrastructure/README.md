# Infrastructure Components

Complete production-ready infrastructure for the Biomedical Intelligence Platform with PostgreSQL, Authentication, and Monitoring.

## 📦 Components

### 1. **Database** ([database/](database/))
- PostgreSQL with SQLAlchemy ORM
- HIPAA-compliant schema
- Alembic migrations
- 6-year audit log retention

### 2. **Authentication** ([authentication/](authentication/))
- JWT-based authentication
- Multi-factor authentication (TOTP)
- Role-based access control (RBAC)
- Session management
- Password policies

### 3. **Monitoring** ([monitoring/](monitoring/))
- Prometheus metrics
- Centralized logging (JSON format)
- Grafana dashboards
- Slack/PagerDuty alerting
- CloudWatch/Elasticsearch integration

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install PostgreSQL
brew install postgresql@15  # macOS
# OR
sudo apt-get install postgresql-15  # Ubuntu

# Start PostgreSQL
brew services start postgresql@15  # macOS
# OR
sudo systemctl start postgresql  # Ubuntu

# Install Python dependencies
python3 -m pip install -r database/requirements.txt
python3 -m pip install -r authentication/requirements.txt
python3 -m pip install -r monitoring/requirements.txt
```

### 1. Database Setup

```bash
# Create database
createdb biomedical_platform

# Set environment variable
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/biomedical_platform"

# Run migrations
cd database
alembic -c config/alembic.ini upgrade head
```

### 2. Initialize Database Schema

```python
from database.src.database import init_database
from database.src.models import Base

# Initialize database
db_manager = init_database(
    database_url="postgresql://postgres:postgres@localhost:5432/biomedical_platform"
)

# Create all tables
db_manager.create_all_tables()
```

### 3. Initialize RBAC Permissions

```python
from database.src.database import init_database
from authentication.src.rbac_service import RBACService

db_manager = init_database()

with db_manager.get_session() as session:
    rbac = RBACService(session)

    # Initialize default permissions
    rbac.initialize_default_permissions()

    # Assign permissions to roles
    rbac.initialize_default_role_permissions()
```

### 4. Create Admin User

```python
from database.src.database import init_database
from database.src.models import User, UserRole
from authentication.src.auth_service import AuthService

db_manager = init_database()

with db_manager.get_session() as session:
    auth_service = AuthService(session)

    # Create admin user
    admin = User(
        username="admin",
        email="admin@biomedical-platform.com",
        password_hash=auth_service.hash_password("ChangeMe123!@#"),
        first_name="System",
        last_name="Administrator",
        role=UserRole.SUPER_ADMIN,
        is_active=True,
        is_verified=True
    )

    session.add(admin)
    session.commit()
```

---

## 📚 Detailed Documentation

### Database Component

#### Schema Overview

**Core Tables:**
- `users` - User accounts with authentication
- `permissions` - Granular permissions for RBAC
- `role_permissions` - Role-to-permission mappings
- `user_sessions` - Active user sessions with JWT tokens
- `patients` - Patient demographic and health information
- `imaging_studies` - Medical imaging studies (X-ray, CT, MRI)
- `model_predictions` - AI model predictions with audit trail
- `diagnostic_reports` - AI-generated diagnostic reports
- `genomic_reports` - Genomic analysis reports
- `audit_logs` - Comprehensive audit trail (HIPAA 6-year retention)
- `hipaa_compliance_checks` - HIPAA compliance audit results
- `system_configuration` - System-wide configuration settings

#### Database Models Usage

```python
from database.src.database import get_db
from database.src.models import Patient, ImagingStudy, ModelPrediction
from fastapi import Depends
from sqlalchemy.orm import Session

@app.post("/patients")
async def create_patient(patient_data: dict, db: Session = Depends(get_db)):
    patient = Patient(
        mrn=patient_data["mrn"],
        first_name=patient_data["first_name"],
        last_name=patient_data["last_name"],
        date_of_birth=patient_data["date_of_birth"],
        sex=patient_data["sex"]
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient
```

#### Alembic Migrations

```bash
# Create a new migration
cd database
alembic -c config/alembic.ini revision -m "Add new column"

# Apply migrations
alembic -c config/alembic.ini upgrade head

# Rollback one migration
alembic -c config/alembic.ini downgrade -1

# Show current revision
alembic -c config/alembic.ini current

# Show migration history
alembic -c config/alembic.ini history
```

---

### Authentication Component

#### User Roles

- `SUPER_ADMIN` - Full system access
- `ADMIN` - Administrative access
- `PHYSICIAN` - Clinical access with diagnostic capabilities
- `RADIOLOGIST` - Imaging-focused access
- `NURSE` - Read access to patient data
- `RESEARCHER` - Analysis and research capabilities
- `PATIENT` - Self-service access to own data
- `AUDITOR` - Audit log and compliance review

#### JWT Authentication

```python
from authentication.src.auth_service import AuthService, get_current_user
from database.src.database import get_db
from fastapi import Depends

@app.post("/auth/login")
async def login(credentials: dict, db: Session = Depends(get_db)):
    auth_service = AuthService(db)

    result = auth_service.authenticate_user(
        username=credentials["username"],
        password=credentials["password"],
        mfa_token=credentials.get("mfa_token"),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    return result  # Returns access_token, refresh_token, user info

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['username']}"}
```

#### Multi-Factor Authentication (MFA)

```python
from authentication.src.auth_service import AuthService

# Enable MFA for user
auth_service = AuthService(db)

# Generate MFA secret
mfa_secret = auth_service.generate_mfa_secret()

# Generate QR code for user to scan
qr_code_base64 = auth_service.generate_mfa_qr_code(
    username="user@example.com",
    secret=mfa_secret
)

# Generate backup codes
backup_codes = auth_service.generate_backup_codes(count=10)

# Save to user account
user.mfa_secret = mfa_secret
user.backup_codes = backup_codes
user.mfa_enabled = True
db.commit()

# Verify TOTP token during login
is_valid = auth_service.verify_totp(mfa_secret, "123456")
```

#### Role-Based Access Control (RBAC)

```python
from authentication.src.rbac_service import RBACService
from authentication.src.auth_service import require_role

# Check permissions
rbac = RBACService(db)

# Check if user has permission
can_access = rbac.has_permission(
    user_id=123,
    resource="patient",
    action="read"
)

# Require permission (raises exception if not authorized)
rbac.require_permission(
    user_id=123,
    resource="patient",
    action="write"
)

# Require specific role
@app.post("/admin/users")
async def create_user(
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_role(["admin", "super_admin"]))
):
    # Only admins can access this
    pass
```

#### Audit Logging

```python
from authentication.src.rbac_service import AuditLogger

audit_logger = AuditLogger(db)

# Log general event
audit_logger.log_event(
    user_id=123,
    action="view_patient",
    resource_type="patient",
    resource_id=456,
    method="GET",
    endpoint="/api/patients/456",
    status_code=200,
    ip_address="192.168.1.1",
    phi_accessed=True,
    patient_id=456,
    access_reason="Clinical review"
)

# Log PHI access (HIPAA requirement)
audit_logger.log_phi_access(
    user_id=123,
    patient_id=456,
    action="view_patient_record",
    access_reason="Annual checkup review",
    ip_address="192.168.1.1"
)

# Log security event
audit_logger.log_security_event(
    event_type="failed_login",
    severity="warning",
    user_id=123,
    ip_address="192.168.1.100",
    details={"username": "user@example.com", "attempts": 3}
)
```

---

### Monitoring Component

#### Prometheus Metrics

```python
from monitoring.src.monitoring_service import MonitoringService

# Initialize monitoring
monitoring = MonitoringService(
    service_name="medical-imaging-ai",
    slack_webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
)

# Record HTTP request
monitoring.record_http_request(
    method="POST",
    endpoint="/classify/chest-xray",
    status_code=200,
    duration_seconds=1.23
)

# Record model prediction
monitoring.record_model_prediction(
    model_name="chest_xray_classifier",
    model_version="v1.0",
    duration_seconds=0.85,
    confidence_score=0.92,
    status="success"
)

# Record PHI access (HIPAA compliance)
monitoring.record_phi_access(
    user_role="physician",
    resource_type="patient"
)

# Set service health
monitoring.set_service_health(is_healthy=True)

# FastAPI metrics endpoint
@app.get("/metrics")
async def metrics():
    return monitoring.get_metrics()
```

#### Centralized Logging

```python
from monitoring.src.logging_config import init_logging, log_with_context

# Initialize logging
logger = init_logging(
    service_name="medical-imaging-ai",
    log_level="INFO",
    enable_cloudwatch=True,
    cloudwatch_config={
        "log_group": "/biomedical-platform/services",
        "log_stream": "medical-imaging-ai",
        "region": "us-east-1"
    }
)

# Log with context
log_with_context(
    logger,
    logging.INFO,
    "Processing chest X-ray classification",
    user_id=123,
    patient_id=456,
    model_name="chest_xray_classifier",
    confidence=0.92
)

# Logs are automatically formatted as JSON:
# {
#   "timestamp": "2025-01-25T10:30:00Z",
#   "level": "INFO",
#   "logger": "medical-imaging-ai",
#   "message": "Processing chest X-ray classification",
#   "user_id": 123,
#   "patient_id": 456,
#   "model_name": "chest_xray_classifier",
#   "confidence": 0.92
# }
```

#### Monitoring Middleware (FastAPI)

```python
from monitoring.src.monitoring_service import MonitoringService, MonitoringMiddleware

app = FastAPI()
monitoring = MonitoringService("my-service")

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware, monitoring_service=monitoring)

# All HTTP requests are now automatically tracked!
```

#### Alerting

```python
# Send alert
await monitoring.send_alert(
    title="High Error Rate",
    message="Error rate exceeded 5% in last 5 minutes",
    severity="critical",
    channels=["slack", "pagerduty"]
)

# Alerts are automatically rate-limited (1 per 5 minutes)
```

#### Context Managers for Tracking

```python
from monitoring.src.monitoring_service import track_prediction_time, track_db_query

# Track model prediction time
with track_prediction_time(monitoring, "chest_xray_classifier", "v1.0"):
    predictions = model.predict(image)

# Track database query time
with track_db_query(monitoring, "select_patient"):
    patient = db.query(Patient).filter(Patient.id == 123).first()
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/biomedical_platform

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Monitoring
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PAGERDUTY_API_KEY=your-pagerduty-integration-key

# AWS CloudWatch (optional)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Elasticsearch (optional)
ELASTICSEARCH_HOSTS=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme

# Service Info
SERVICE_NAME=biomedical-platform
ENVIRONMENT=production
```

---

## 🐳 Docker Deployment

### Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: biomedical_platform
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/config/grafana-dashboard.json:/etc/grafana/provisioning/dashboards/biomedical.json
    ports:
      - "3000:3000"

volumes:
  postgres_data:
  prometheus_data:
  grafana_data:
```

---

## 📊 Monitoring Setup

### Prometheus Configuration

Create `monitoring/config/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'medical-imaging-ai'
    static_configs:
      - targets: ['localhost:5001']

  - job_name: 'ai-diagnostics'
    static_configs:
      - targets: ['localhost:5002']

  - job_name: 'genomic-intelligence'
    static_configs:
      - targets: ['localhost:5007']

  - job_name: 'obicare'
    static_configs:
      - targets: ['localhost:5010']

  - job_name: 'hipaa-monitor'
    static_configs:
      - targets: ['localhost:5011']
```

### Grafana Dashboards

1. Import dashboard from `monitoring/config/grafana-dashboard.json`
2. Configure Prometheus data source: `http://prometheus:9090`
3. View real-time metrics at `http://localhost:3000`

---

## 🔐 Security Best Practices

### Password Policy

- Minimum 12 characters
- Must include: uppercase, lowercase, digits, special characters
- Passwords hashed with bcrypt
- Password change required every 90 days
- Account lockout after 5 failed attempts

### Session Management

- Access tokens expire in 30 minutes
- Refresh tokens expire in 7 days
- Sessions tracked with IP and user agent
- Automatic session cleanup

### Audit Logging

- All PHI access logged (HIPAA requirement)
- 6-year retention period
- Tamper-proof audit trail
- Real-time security event detection

---

## 📈 Performance

### Database Optimization

- Connection pooling (10 connections, 20 max overflow)
- Indexed columns for fast queries
- Query performance monitoring
- Automatic connection recycling (1 hour)

### Caching Strategy

- Redis for session storage (optional)
- Query result caching
- Token validation caching

---

## 🧪 Testing

```python
# Test database connection
from database.src.database import init_database

db_manager = init_database()
assert db_manager.health_check() == True

# Test authentication
from authentication.src.auth_service import AuthService

auth_service = AuthService(db)
token = auth_service.create_access_token(
    user_id=1,
    username="test",
    role="physician"
)
payload = auth_service.verify_token(token)
assert payload["sub"] == "1"

# Test monitoring
from monitoring.src.monitoring_service import MonitoringService

monitoring = MonitoringService("test-service")
monitoring.record_http_request("GET", "/health", 200, 0.1)
```

---

## 🚨 Troubleshooting

### Database Issues

```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432

# View database logs
tail -f /usr/local/var/log/postgresql@15.log

# Reset database
dropdb biomedical_platform
createdb biomedical_platform
alembic upgrade head
```

### Authentication Issues

```python
# Reset user password
user = db.query(User).filter(User.username == "admin").first()
user.password_hash = auth_service.hash_password("NewPassword123!@#")
user.failed_login_attempts = 0
user.locked_until = None
db.commit()

# Revoke all sessions
auth_service.revoke_all_user_sessions(user.id)
```

### Monitoring Issues

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# View metrics
curl http://localhost:5001/metrics

# Test Slack webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert"}' \
  $SLACK_WEBHOOK_URL
```

---

## 📖 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)

---

## 📝 License

This infrastructure is part of the Biomedical Intelligence Platform and is intended for healthcare and research use. Ensure all deployments comply with HIPAA, FDA, and local regulations.
