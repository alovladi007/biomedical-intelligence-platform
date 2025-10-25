# Unified API Gateway - Biomedical Intelligence Platform

**Production-grade API Gateway** integrating all microservices with core infrastructure.

## 🎯 Purpose

This API Gateway serves as the **single entry point** for all medical AI services, providing:
- ✅ **Centralized Authentication** (OAuth 2.0 + JWT)
- ✅ **Role-Based Access Control** (14 predefined roles)
- ✅ **HIPAA Audit Logging** (all API calls logged)
- ✅ **Service Proxy** (routes to 8 microservices)
- ✅ **Permission Checking** (before every request)

## 🏗️ Architecture

```
Client Request
     ↓
API Gateway (Port 8000)
     ↓
1. Verify JWT Token
2. Check RBAC Permissions
3. Log to Audit Trail
4. Proxy to Microservice
5. Log Response
     ↓
Microservice Response
```

## 🔐 Authentication Flow

### 1. Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dr_smith",
    "email": "dr.smith@hospital.com",
    "password": "SecurePass123!@#",
    "roles": ["physician"]
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dr_smith",
    "password": "SecurePass123!@#"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "...",
  "token_type": "Bearer",
  "expires_in": 900,
  "session_id": "session_abc123"
}
```

### 3. Use Token for API Calls
```bash
curl -X GET http://localhost:8000/api/services/medical-imaging/health \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

## 🌐 Available Services

| Service | Port | Description | Resource Type |
|---------|------|-------------|---------------|
| **medical-imaging** | 5001 | Medical Imaging AI | DICOM_STUDY |
| **ai-diagnostics** | 5002 | AI Diagnostics | MEDICAL_RECORD |
| **biosensing** | 5003 | Biosensing Analytics | LAB_RESULTS |
| **cloud-ehr** | 5004 | Cloud EHR | MEDICAL_RECORD |
| **clinical-trials** | 5005 | Clinical Trials | PATIENT_DATA |
| **telemedicine** | 5006 | Telemedicine | PATIENT_DATA |
| **genomic-intelligence** | 5007 | Genomic Intelligence | GENOMIC_DATA |
| **drug-discovery** | 5008 | Drug Discovery AI | MODEL_PREDICTION |

## 📊 Permission Matrix

| Role | Patient Data | DICOM | Genomic | Lab Results | Models |
|------|--------------|-------|---------|-------------|--------|
| **Physician** | READ, WRITE, UPDATE | READ, WRITE | READ | READ, WRITE | READ, EXECUTE |
| **Nurse** | READ | - | - | READ, WRITE | - |
| **Radiologist** | READ | READ, WRITE, UPDATE | - | - | READ, EXECUTE |
| **Researcher** | READ (de-identified) | READ | READ | READ | READ |
| **Data Scientist** | READ | READ | READ | - | READ, WRITE, EXECUTE |
| **Admin** | - | - | - | - | - |

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn httpx pyjwt bcrypt
```

### 2. Set Environment Variables
```bash
export JWT_SECRET="your-secret-key-change-in-production"
```

### 3. Start API Gateway
```bash
cd api-gateway
python3 gateway.py
```

**Gateway will start on:** `http://localhost:8000`

### 4. View Documentation
Open browser: `http://localhost:8000/docs`

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout user

### Service Proxy (Authenticated)
- `GET/POST/PUT/DELETE /api/services/{service_name}/{path}` - Proxy to service

### Audit
- `GET /api/audit/patient/{patient_id}` - Get patient access log
- `GET /api/audit/statistics` - Get audit statistics

### Health
- `GET /health` - Health check
- `GET /` - API information

## 🔒 Security Features

1. **JWT Authentication**
   - Access tokens expire in 15 minutes
   - Refresh tokens expire in 30 days
   - Tokens signed with HS256 (configurable to RS256)

2. **RBAC Enforcement**
   - Permission checked before every request
   - Resource-level access control
   - Hierarchical role inheritance

3. **Audit Logging**
   - Every API call logged with:
     - User ID and username
     - IP address
     - Action performed
     - Resource accessed
     - Success/failure status
   - 6-year retention (HIPAA compliant)

4. **Request Validation**
   - Authorization header required
   - Token format validation
   - Permission verification

## 📖 Example Workflows

### Medical Imaging Prediction
```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo_physician", "password": "DemoPass123!@#"}' \
  | jq -r '.access_token')

# 2. Call Medical Imaging Service
curl -X POST http://localhost:8000/api/services/medical-imaging/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/xray.jpg",
    "patient_id": "PATIENT_12345"
  }'
```

### Genomic Analysis
```bash
# Call Genomic Intelligence Service
curl -X POST http://localhost:8000/api/services/genomic-intelligence/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vcf_file": "patient.vcf",
    "patient_id": "PATIENT_12345"
  }'
```

### Audit Trail Query
```bash
# Get patient access log (requires auditor role)
curl -X GET http://localhost:8000/api/audit/patient/PATIENT_12345?days=30 \
  -H "Authorization: Bearer $TOKEN"
```

## 🛡️ HIPAA Compliance

This API Gateway ensures HIPAA compliance through:

1. **Access Control (§164.312(a)(1))**
   - User authentication required for all endpoints
   - Role-based permissions enforced

2. **Audit Controls (§164.312(b))**
   - All PHI access logged
   - Patient identifier recorded
   - 6-year retention period

3. **Integrity (§164.312(c)(1))**
   - JWT tokens prevent tampering
   - Request/response validation

4. **Person/Entity Authentication (§164.312(d))**
   - Multi-factor authentication support
   - Session management

## 🔧 Configuration

### Production Settings
```python
# Use RS256 for better security
auth_service = AuthenticationService(
    jwt_secret=private_key,  # RSA private key
    jwt_algorithm="RS256"
)

# Enable CORS for specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hospital.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# HTTPS only
uvicorn.run(app, host="0.0.0.0", port=8000, ssl_certfile="cert.pem", ssl_keyfile="key.pem")
```

## 📊 Monitoring

The gateway logs all activity:
- Authentication attempts (success/failure)
- Permission checks (granted/denied)
- API calls (method, endpoint, status)
- Service errors

Logs can be forwarded to SIEM for real-time monitoring.

## 🎯 Next Steps

1. **Start all microservices** on their designated ports (5001-5008)
2. **Start API Gateway** on port 8000
3. **Test authentication** with demo users
4. **Make authenticated API calls** to services
5. **Review audit logs** for compliance

---

**The platform is now fully integrated and production-ready!**
