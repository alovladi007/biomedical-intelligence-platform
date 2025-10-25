# Auth Dashboard Service

Central Authentication & Data API for Biomedical Intelligence Platform

**Port:** 8100

## Features

- **Authentication**: Login, register, MFA (TOTP), JWT tokens
- **Patient Management**: CRUD operations on patient records
- **Prediction History**: View and review AI predictions
- **User Management**: Admin user management
- **Admin Panel**: RBAC, audit logs, system monitoring

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 15
- Infrastructure services running (see `infrastructure/` directory)

### Installation

```bash
# Navigate to backend directory
cd auth-dashboard-service/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and set your configuration
nano .env
```

### Initialize Database

```bash
# Make sure PostgreSQL is running
# Make sure DATABASE_URL is set in .env

# Run database migrations from infrastructure directory
cd ../../infrastructure/database
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/biomedical_platform"
alembic -c config/alembic.ini upgrade head

# Go back to auth-dashboard-service
cd ../../auth-dashboard-service/backend
```

### Run Server

```bash
# From auth-dashboard-service/backend directory with venv activated
python app/main.py

# Or use uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload
```

The service will be available at:
- API: http://localhost:8100
- Swagger Docs: http://localhost:8100/docs
- ReDoc: http://localhost:8100/redoc

## API Endpoints

### Authentication (`/auth`)

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `POST /auth/refresh` - Refresh access token
- `POST /auth/mfa/setup` - Setup MFA
- `POST /auth/mfa/verify` - Verify and enable MFA
- `POST /auth/mfa/disable` - Disable MFA
- `GET /auth/me` - Get current user profile
- `POST /auth/change-password` - Change password

### Patients (`/api/patients`)

- `GET /api/patients` - List all patients
- `GET /api/patients/{id}` - Get patient by ID
- `POST /api/patients` - Create new patient
- `PUT /api/patients/{id}` - Update patient
- `DELETE /api/patients/{id}` - Delete patient (soft delete)
- `POST /api/patients/search` - Search patients

### Predictions (`/api/predictions`)

- `GET /api/predictions` - List all predictions
- `GET /api/predictions/{id}` - Get prediction by ID
- `GET /api/predictions/patient/{patient_id}` - Get patient predictions
- `POST /api/predictions/{id}/review` - Submit clinician review
- `POST /api/predictions/filter` - Filter predictions
- `GET /api/predictions/stats` - Get prediction statistics

### Users (`/api/users`) - Admin Only

- `GET /api/users` - List all users
- `GET /api/users/{id}` - Get user by ID
- `POST /api/users` - Create new user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user (soft delete)
- `POST /api/users/{id}/reset-password` - Reset user password
- `GET /api/users/stats` - Get user statistics

### Admin (`/api/admin`) - Admin/Auditor Only

- `GET /api/admin/permissions` - List all permissions
- `GET /api/admin/permissions/role/{role}` - Get role permissions
- `GET /api/admin/audit-logs` - Get audit logs
- `GET /api/admin/audit-logs/security-events` - Get security events
- `GET /api/admin/audit-logs/phi-access` - Get PHI access logs
- `GET /api/admin/system/health` - Get system health

### Health & Monitoring

- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## Authentication

All protected endpoints require Bearer token authentication:

```bash
# Login to get token
curl -X POST http://localhost:8100/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your-password"
  }'

# Use token in subsequent requests
curl -X GET http://localhost:8100/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Example Usage

### Register New User

```bash
curl -X POST http://localhost:8100/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "physician"
  }'
```

### Create Patient

```bash
curl -X POST http://localhost:8100/api/patients \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mrn": "MRN001",
    "first_name": "Jane",
    "last_name": "Smith",
    "date_of_birth": "1990-01-15",
    "sex": "female",
    "email": "jane@example.com"
  }'
```

### Get Prediction Statistics

```bash
curl -X GET http://localhost:8100/api/predictions/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Development

### Project Structure

```
auth-dashboard-service/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── auth.py
│   │   │           ├── patients.py
│   │   │           ├── predictions.py
│   │   │           ├── users.py
│   │   │           └── admin.py
│   │   ├── schemas/
│   │   │   ├── auth_schemas.py
│   │   │   ├── patient_schemas.py
│   │   │   ├── prediction_schemas.py
│   │   │   └── user_schemas.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## Security

- JWT tokens expire after 30 minutes (configurable)
- Refresh tokens expire after 7 days (configurable)
- Passwords must be 12+ characters with complexity requirements
- MFA support with TOTP
- Account lockout after 5 failed login attempts
- All PHI access is logged for HIPAA compliance
- RBAC permissions for all endpoints

## Troubleshooting

### Database Connection Error

Make sure PostgreSQL is running and DATABASE_URL is correct:

```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432

# Test connection
psql postgresql://postgres:postgres@localhost:5432/biomedical_platform
```

### Port Already in Use

If port 8100 is in use, change PORT in .env or use a different port:

```bash
PORT=8101 python app/main.py
```

### Module Import Errors

Make sure you're in the correct directory and venv is activated:

```bash
cd auth-dashboard-service/backend
source venv/bin/activate
python app/main.py
```

## Integration with Frontend

This service is designed to work with the frontend dashboard. The frontend should:

1. Store tokens in localStorage after login
2. Include Bearer token in Authorization header for all requests
3. Handle token refresh when access token expires
4. Redirect to login on 401 errors

Example frontend integration:

```typescript
// Login
const response = await fetch('http://localhost:8100/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});
const { access_token, refresh_token } = await response.json();
localStorage.setItem('access_token', access_token);

// API call with auth
const data = await fetch('http://localhost:8100/api/patients', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please contact support@myengineering.tech
