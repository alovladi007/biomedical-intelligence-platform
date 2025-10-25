# 🏥 BioMedical Intelligence Platform

> **Complete Production-Ready Healthcare AI Platform** with PostgreSQL, Authentication, Monitoring, and HIPAA Compliance

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-%3E%3D5.0.0-blue)](https://www.typescriptlang.org/)
[![HIPAA](https://img.shields.io/badge/HIPAA-Compliant-green)](https://www.hhs.gov/hipaa/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)

---

## 🎯 What's New - Complete Production Infrastructure

**Latest Update:** Full production infrastructure with Database, Authentication, Monitoring, Backups, and Security!

### ✨ **Just Added** (See [`infrastructure/`](infrastructure/) directory):

🗄️ **PostgreSQL Database** - HIPAA-compliant with 6-year audit retention
🔐 **JWT + MFA Authentication** - Multi-factor authentication with TOTP
👥 **RBAC Authorization** - 8 roles with granular permissions
📊 **Prometheus + Grafana** - Real-time monitoring with 15+ alerts
📝 **Centralized Logging** - JSON logs with CloudWatch/ELK integration
💾 **Automated Backups** - Encrypted backups with 6-year retention
🔒 **Security Hardening** - Firewall, SSL/TLS, penetration testing
🐳 **Docker Deployment** - Complete stack with docker-compose

**📚 Quick Links:**
- [🚀 Quick Start](#-quick-start-5-minutes) - Get running in 5 minutes
- [📖 Full Deployment Guide](DEPLOYMENT_GUIDE.md) - Complete setup instructions
- [🏗️ Infrastructure Docs](infrastructure/README.md) - Database, Auth, Monitoring details

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Quick Start](#-quick-start-5-minutes)
- [Platform Architecture](#-platform-architecture)
- [AI Services](#-ai-services)
- [Infrastructure Components](#-infrastructure-components)
- [Production Tools](#-production-tools)
- [Getting Started](#-getting-started)
- [Deployment](#-deployment)
- [Security & Compliance](#-security--compliance)
- [API Documentation](#-api-documentation)
- [Monitoring & Logging](#-monitoring--logging)
- [Contributing](#-contributing)

---

## 🎯 Overview

The BioMedical Intelligence Platform is a **complete, production-ready healthcare AI platform** with:

### **5 AI Services** (FastAPI + Python)
1. **Medical Imaging AI** (Port 5001) - Chest X-ray classification, CT segmentation
2. **AI Diagnostics** (Port 5002) - Symptom checker, drug interactions, lab interpretation
3. **Genomic Intelligence** (Port 5007) - Variant annotation, pharmacogenomics
4. **OBiCare Maternal Health** (Port 5010) - Pre-eclampsia prediction, ultrasound analysis
5. **HIPAA Monitor** (Port 5011) - Compliance checking, anomaly detection

### **Production Infrastructure** (NEW!)
- PostgreSQL database with 15 HIPAA-compliant tables
- JWT + MFA authentication
- Role-based access control (RBAC)
- Prometheus metrics + Grafana dashboards
- Centralized logging (JSON, CloudWatch, ELK)
- Automated encrypted backups (6-year retention)
- Security hardening + penetration testing
- Docker Compose deployment

### **Production Tools**
- Model training pipeline (NIH ChestX-ray14)
- Security penetration testing (OWASP Top 10)
- HIPAA compliance audit (§164.302-318)

---

## 🚀 Quick Start (5 Minutes)

### **Option 1: Start Infrastructure Only**

```bash
# Clone repository
git clone https://github.com/alovladi007/biomedical-intelligence-platform.git
cd biomedical-intelligence-platform

# Start infrastructure (PostgreSQL, Prometheus, Grafana, Redis, Elasticsearch, Kibana)
cd infrastructure
docker-compose up -d

# Initialize database
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/biomedical_platform"
cd database
alembic -c config/alembic.ini upgrade head

# Access dashboards
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
# - Kibana: http://localhost:5601
```

### **Option 2: Full Platform**

See complete deployment guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 🏗️ Platform Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client Applications                          │
└────────────┬────────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────────┐
│                      API Gateway (Future)                       │
│                   Load Balancer / NGINX                         │
└────┬─────────┬──────────┬──────────┬──────────┬────────────────┘
     │         │          │          │          │
┌────▼────┐ ┌─▼─────┐ ┌──▼──────┐ ┌─▼──────┐ ┌▼─────────┐
│Medical  │ │AI Diag│ │Genomic  │ │OBiCare │ │HIPAA     │
│Imaging  │ │:5002  │ │Intel    │ │:5010   │ │Monitor   │
│AI :5001 │ │       │ │:5007    │ │        │ │:5011     │
└────┬────┘ └───┬───┘ └────┬────┘ └───┬────┘ └────┬─────┘
     │          │          │          │          │
     └──────────┴──────────┴──────────┴──────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼───────┐ ┌───────▼───────┐ ┌──────▼──────┐
│   Database    │ │Authentication │ │ Monitoring  │
│  PostgreSQL   │ │  JWT + MFA    │ │ Prometheus  │
│   Port 5432   │ │  RBAC + Audit │ │ Grafana     │
└───────────────┘ └───────────────┘ └─────────────┘
```

---

## 🤖 AI Services

### 1. **Medical Imaging AI** (Port 5001)
**Capabilities:**
- Chest X-ray classification (14 pathologies, DenseNet-121)
- CT segmentation (6 organs, 3D U-Net)
- Risk scoring and clinical recommendations

**Endpoints:**
```bash
POST /classify/chest-xray   # Classify chest X-ray
POST /segment/ct            # Segment CT scan
GET  /health                # Health check
GET  /metrics               # Prometheus metrics
```

**Tech Stack:** FastAPI, PyTorch, torchvision, pydicom, nibabel

---

### 2. **AI Diagnostics** (Port 5002)
**Capabilities:**
- Symptom checker (50+ symptoms, 20+ diseases with ICD-10)
- Drug interaction checker (10+ critical interactions)
- Lab result interpreter (40+ tests with normal ranges)

**Endpoints:**
```bash
POST /symptom-check         # Check symptoms
POST /drug-interactions     # Check drug interactions
POST /interpret-labs        # Interpret lab results
GET  /health                # Health check
```

**Tech Stack:** FastAPI, XGBoost, scikit-learn

---

### 3. **Genomic Intelligence** (Port 5007)
**Capabilities:**
- Variant annotation (ClinVar, gnomAD)
- Pharmacogenomics (CPIC guidelines, 10 pharmacogenes)
- Personalized warfarin dosing

**Endpoints:**
```bash
POST /annotate/variant      # Annotate genetic variant
POST /pharmacogenomics      # Get drug-gene interactions
POST /warfarin-dosing       # Calculate personalized warfarin dose
```

**Tech Stack:** FastAPI, vcfpy, requests

---

### 4. **OBiCare Maternal Health** (Port 5010)
**Capabilities:**
- Pre-eclampsia risk prediction
- Ultrasound analysis (fetal biometry)
- Maternal vitals monitoring

**Endpoints:**
```bash
POST /predict/preeclampsia-risk   # Predict pre-eclampsia risk
POST /analyze/ultrasound          # Analyze ultrasound
POST /monitor/vitals              # Monitor maternal vitals
```

---

### 5. **HIPAA Monitor** (Port 5011)
**Capabilities:**
- Automated compliance checking
- Anomaly detection in access logs
- Audit reporting

**Endpoints:**
```bash
POST /compliance/check      # Check HIPAA compliance
POST /detect/anomalies      # Detect access anomalies
GET  /audit/report          # Generate audit report
```

---

## 🏗️ Infrastructure Components

### **Database** ([`infrastructure/database/`](infrastructure/database/))

**PostgreSQL with SQLAlchemy ORM:**
- 15 HIPAA-compliant tables
- Connection pooling (10 connections, 20 max overflow)
- Alembic migrations
- 6-year audit log retention

**Tables:**
- `users` - User accounts with MFA
- `patients` - Patient demographic/health info
- `imaging_studies` - Medical imaging studies
- `model_predictions` - AI predictions with audit trail
- `diagnostic_reports` - AI diagnostic reports
- `genomic_reports` - Genomic analysis reports
- `audit_logs` - Comprehensive audit trail (6-year retention)
- `user_sessions` - JWT session tracking
- And more...

**Usage:**
```python
from infrastructure.database.src.database import init_database, get_db
from infrastructure.database.src.models import Patient, ModelPrediction

db_manager = init_database()
```

---

### **Authentication** ([`infrastructure/authentication/`](infrastructure/authentication/))

**JWT + MFA + RBAC:**
- Access tokens (30 min expiry)
- Refresh tokens (7 day expiry)
- TOTP-based MFA with QR codes
- 8 user roles: super_admin, admin, physician, radiologist, nurse, researcher, patient, auditor
- 20+ granular permissions

**Usage:**
```python
from infrastructure.authentication.src.auth_service import AuthService, get_current_user
from infrastructure.authentication.src.rbac_service import RBACService

# Authenticate user
auth = AuthService(db)
result = auth.authenticate_user(username, password, mfa_token)

# Check permissions
rbac = RBACService(db)
rbac.require_permission(user_id, resource="patient", action="read")
```

**Features:**
- Password policies (12+ chars, complexity requirements)
- Account lockout (5 failed attempts = 30 min lock)
- Session management with IP tracking
- HIPAA-compliant audit logging

---

### **Monitoring** ([`infrastructure/monitoring/`](infrastructure/monitoring/))

**Prometheus + Grafana + Logging:**
- HTTP request metrics
- Model prediction metrics
- Database query performance
- Authentication tracking
- PHI access monitoring
- Error tracking

**Usage:**
```python
from infrastructure.monitoring.src.monitoring_service import MonitoringService

monitoring = MonitoringService("my-service")
monitoring.record_http_request(method="POST", endpoint="/predict", status_code=200, duration_seconds=0.5)
monitoring.record_model_prediction(model_name="chest_xray", model_version="v1.0", duration_seconds=0.8, confidence_score=0.92)
```

**Dashboards:**
- Grafana: http://localhost:3000 (9 pre-configured panels)
- Prometheus: http://localhost:9090 (15+ alert rules)

**Alerting:**
- Slack integration
- PagerDuty integration
- Alert rate limiting

---

## 🛠️ Production Tools

### **1. Model Training** ([`production-ready/model-training/`](production-ready/model-training/))

Train models on real datasets:

```bash
cd production-ready/model-training
pip install -r requirements.txt

# Train on NIH ChestX-ray14 (112,120 images, 14 pathologies)
python train_chest_xray_model.py \
    --data_dir /path/to/nih-chest-xray14 \
    --csv_path /path/to/Data_Entry_2017.csv \
    --output_dir ./models \
    --num_epochs 50
```

---

### **2. Security Testing** ([`production-ready/security-testing/`](production-ready/security-testing/))

OWASP Top 10 penetration testing:

```bash
cd production-ready/security-testing
pip install -r requirements.txt

python penetration_test.py
# Output: Security score (0-100), vulnerability report
```

**Tests:**
- Authentication bypass
- SQL injection
- XSS (Cross-Site Scripting)
- IDOR (Insecure Direct Object Reference)
- Security misconfiguration
- Sensitive data exposure
- Rate limiting
- CORS misconfiguration

---

### **3. HIPAA Compliance Audit** ([`production-ready/hipaa-compliance/`](production-ready/hipaa-compliance/))

Complete HIPAA Security Rule audit:

```bash
cd production-ready/hipaa-compliance
pip install -r requirements.txt

python hipaa_audit.py
# Output: Compliance report with evidence requirements
```

**Audits:**
- Administrative Safeguards (§164.308)
- Physical Safeguards (§164.310)
- Technical Safeguards (§164.312)
- Organizational Requirements (§164.314)
- Policies and Procedures (§164.316)

---

## 🚀 Getting Started

### **Prerequisites**

- Python 3.9+
- Node.js 18+
- PostgreSQL 15
- Docker & Docker Compose
- Git

### **Installation**

```bash
# 1. Clone repository
git clone https://github.com/alovladi007/biomedical-intelligence-platform.git
cd biomedical-intelligence-platform

# 2. Start infrastructure
cd infrastructure
docker-compose up -d

# 3. Initialize database
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/biomedical_platform"
cd database
alembic -c config/alembic.ini upgrade head

# 4. Install service dependencies
cd ../../medical-imaging-ai
pip install -r requirements.txt

# 5. Start a service
cd src
python main.py
# Service running on http://localhost:5001
```

---

## 🐳 Deployment

### **Docker Compose (Recommended)**

```bash
cd infrastructure
docker-compose up -d
```

**This starts:**
- PostgreSQL (port 5432)
- Prometheus (port 9090)
- Grafana (port 3000)
- Redis (port 6379)
- Elasticsearch (port 9200)
- Kibana (port 5601)

### **Production Deployment**

See complete guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Includes:**
- Security hardening script
- Automated backup configuration
- SSL/TLS setup
- Firewall configuration
- Monitoring setup
- Alert configuration

---

## 🔒 Security & Compliance

### **HIPAA Compliance**

✅ **Encryption:**
- AES-256-GCM at rest
- TLS 1.3 in transit
- Encrypted backups (GPG)

✅ **Audit Logging:**
- All PHI access logged
- 6-year retention
- Tamper-proof trail

✅ **Access Control:**
- JWT + MFA authentication
- Role-based access control (RBAC)
- Session management

✅ **Backups:**
- Automated daily backups
- 6-year retention policy
- Encrypted and off-site storage

### **Security Features**

- Password policies (12+ chars, complexity)
- Account lockout (5 failed attempts)
- Rate limiting
- CORS protection
- Input validation
- SQL injection prevention
- XSS protection

### **Automated Backups**

```bash
# Full backup
./infrastructure/scripts/backup_database.sh full

# Incremental backup
./infrastructure/scripts/backup_database.sh incremental

# Restore
./infrastructure/scripts/restore_database.sh /path/to/backup.sql.gpg
```

**Backup Features:**
- GPG encryption
- 6-year retention
- S3 upload (optional)
- Integrity verification
- Automated reporting

---

## 📊 Monitoring & Logging

### **Grafana Dashboards**

Access: http://localhost:3000 (admin/admin)

**9 Pre-configured Panels:**
- Service health status
- HTTP request rate and duration
- Model prediction metrics
- Error rates
- Authentication attempts
- PHI access tracking
- Database connections

### **Prometheus Metrics**

Access: http://localhost:9090

**Metrics:**
- `http_requests_total`
- `http_request_duration_seconds`
- `model_predictions_total`
- `model_prediction_duration_seconds`
- `db_connections_active`
- `auth_attempts_total`
- `phi_access_total`
- `errors_total`

### **Alerts**

**15+ Production Alerts:**
- ServiceDown (critical)
- HighErrorRate (warning)
- SlowModelPrediction (warning)
- HighFailedLoginAttempts (critical - brute force)
- PHIAccessWithoutReason (critical - HIPAA violation)
- DiskSpaceLow (critical)

---

## 📚 API Documentation

### **Authentication**

```bash
# Login
POST /auth/login
{
  "username": "user@example.com",
  "password": "password",
  "mfa_token": "123456"  # Optional, if MFA enabled
}

# Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user_id": 1,
  "role": "physician"
}
```

### **Medical Imaging AI**

```bash
# Classify chest X-ray
POST /classify/chest-xray
Authorization: Bearer <token>
{
  "patient_id": 123,
  "image_path": "/path/to/xray.dcm"
}

# Response
{
  "predictions": {
    "Cardiomegaly": 0.89,
    "Atelectasis": 0.12,
    ...
  },
  "risk_level": "high",
  "recommendations": "Follow-up with cardiology"
}
```

### **AI Diagnostics**

```bash
# Symptom check
POST /symptom-check
Authorization: Bearer <token>
{
  "symptoms": ["cough", "fever", "shortness_of_breath"],
  "duration_days": 5,
  "severity": "moderate",
  "age": 45,
  "sex": "male"
}

# Response
{
  "differential_diagnoses": [
    {
      "disease": "Pneumonia",
      "confidence": 0.85,
      "icd10": "J18",
      "urgency": "high"
    }
  ],
  "recommendations": "Seek immediate medical attention"
}
```

**Complete API docs:** See individual service README files or integration example at [`infrastructure/examples/service_integration_example.py`](infrastructure/examples/service_integration_example.py)

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Development Guidelines:**
- Follow Python/TypeScript best practices
- Write tests for new features
- Update documentation
- Ensure HIPAA compliance
- Follow security best practices

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📖 Additional Resources

**Documentation:**
- [Full Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Infrastructure README](infrastructure/README.md)
- [Production-Ready Tools](production-ready/README.md)

**Quick Links:**
- [Database Models](infrastructure/database/src/models.py)
- [Authentication Service](infrastructure/authentication/src/auth_service.py)
- [Monitoring Service](infrastructure/monitoring/src/monitoring_service.py)
- [Integration Example](infrastructure/examples/service_integration_example.py)

---

## 🏆 Features Summary

✅ **5 AI Services** - Medical imaging, diagnostics, genomics, maternal health, HIPAA monitoring
✅ **Production Database** - PostgreSQL with 15 HIPAA tables
✅ **Authentication** - JWT + MFA + RBAC
✅ **Monitoring** - Prometheus + Grafana + 15+ alerts
✅ **Logging** - Centralized JSON logs with CloudWatch/ELK
✅ **Backups** - Automated encrypted backups with 6-year retention
✅ **Security** - Penetration testing, hardening, SSL/TLS
✅ **Compliance** - HIPAA audit framework
✅ **Docker** - Complete infrastructure with docker-compose
✅ **Documentation** - 2,000+ lines of comprehensive docs

---

## 👥 Authors

**M.Y. Engineering and Technologies**

- Email: platform@myengineering.tech
- Phone: (800) 100-2000

---

## 🙏 Acknowledgments

- Built with modern healthcare technology standards
- Designed for HIPAA compliance
- FDA approval readiness
- Enterprise-grade security
- Production-ready infrastructure

---

## 📞 Support

For support and questions:

- **Email:** support@myengineering.tech
- **Documentation:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Issues:** [GitHub Issues](https://github.com/alovladi007/biomedical-intelligence-platform/issues)

---

<div align="center">

⚕️ **Built for Healthcare** • 🔒 **HIPAA Compliant** • 🚀 **Production Ready**

**[Get Started](DEPLOYMENT_GUIDE.md)** | **[Documentation](infrastructure/README.md)** | **[API Docs](#-api-documentation)**

</div>
