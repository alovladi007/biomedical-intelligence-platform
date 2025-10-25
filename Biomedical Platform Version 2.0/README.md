# 🏥 BioMedical Intelligence Platform

> **Complete Healthcare Technology Suite** - AI Diagnostics, Medical Imaging, Biosensing, HIPAA Compliance, MLOps, and Maternal Care

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-%3E%3D5.0.0-blue)](https://www.typescriptlang.org/)
[![HIPAA](https://img.shields.io/badge/HIPAA-Compliant-green)](https://www.hhs.gov/hipaa/)

## 📋 Table of Contents

- [Overview](#overview)
- [Services](#services)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The BioMedical Intelligence Platform is a comprehensive, production-ready healthcare technology suite featuring six integrated microservices:

1. **AI Diagnostics** - ML-based disease prediction and risk assessment
2. **Medical Imaging AI** - DICOM processing with AI inference and Grad-CAM explainability
3. **Biosensing Technology** - Real-time health monitoring with IoT integration
4. **HIPAA Compliance** - Security, encryption, and audit management
5. **BioTensor Labs** - MLOps platform with experiment tracking
6. **MYNX NatalCare** - Maternal health monitoring and prenatal care

## 🚀 Services

### 1. AI Diagnostics (Port 3007 / API: 5001)
- ML-based disease prediction
- Risk scoring and assessment
- Predictive analytics
- Clinical decision support
- Multi-model inference

### 2. Medical Imaging AI (Port 3002 / API: 5002)
- DICOM image processing
- AI-powered diagnosis
- Grad-CAM explainability
- Automated triage
- Report generation

### 3. Biosensing Technology (Port 3003 / API: 5003)
- Real-time sensor monitoring
- AWS IoT Core integration
- WebSocket streaming
- Anomaly detection
- Device management

### 4. HIPAA Compliance (Port 3004 / API: 5004)
- AES-256-GCM encryption
- Comprehensive audit logging
- Breach detection and tracking
- Compliance reporting
- Key management

### 5. BioTensor Labs (Port 3005 / API: 5005)
- MLflow integration
- Experiment tracking
- Model registry
- Deployment pipelines
- Performance monitoring

### 6. MYNX NatalCare (Port 3006 / API: 5006)
- Prenatal care tracking
- Appointment management
- Vital signs monitoring
- Risk assessment
- Patient portal

## 🏗️ Architecture

```
┌─────────────────┐
│  Landing Page   │  (Port 8080)
│  (index.html)   │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┬────────┬────────┐
    │         │        │        │        │        │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐
│AI Diag│ │Med Img│ │BioSen│ │HIPAA │ │BioTen│ │MYNX  │
│ :3007 │ │ :3002 │ │ :3003│ │ :3004│ │ :3005│ │ :3006│
└───┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
    │        │        │        │        │        │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐
│Backend│ │Backend│ │Backend│ │Backend│ │Backend│ │Backend│
│ :5001 │ │ :5002 │ │ :5003 │ │ :5004 │ │ :5005 │ │ :5006 │
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘
```

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 14, React 18
- **Language**: TypeScript 5.3
- **Styling**: Tailwind CSS 3.3
- **Icons**: Lucide React
- **Build**: Webpack 5

### Backend
- **Runtime**: Node.js 18+
- **Framework**: Express.js 4
- **Language**: TypeScript 5.3
- **Security**: Helmet, CORS, Rate Limiting
- **Logging**: Morgan, Winston

### Database (Architecture Ready)
- PostgreSQL 15 with TimescaleDB
- Redis for caching
- AWS S3 for object storage

### ML/AI (Architecture Ready)
- TensorFlow, PyTorch
- MLflow for experiment tracking
- KServe for model serving

## 📦 Getting Started

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/biomedical-intelligence-platform.git
cd biomedical-intelligence-platform

# Make scripts executable
chmod +x *.sh

# Install all dependencies
./install-all.sh

# Start all services
./start-all.sh

# Open your browser
# Main landing page: http://localhost:8080
# Individual services: See URLs below
```

### Service URLs

**Frontend Applications:**
- Landing Page: http://localhost:8080
- AI Diagnostics: http://localhost:3007
- Medical Imaging: http://localhost:3002
- Biosensing: http://localhost:3003
- HIPAA Compliance: http://localhost:3004
- BioTensor Labs: http://localhost:3005
- MYNX NatalCare: http://localhost:3006

**Backend APIs:**
- AI Diagnostics API: http://localhost:5001
- Medical Imaging API: http://localhost:5002
- Biosensing API: http://localhost:5003
- HIPAA Compliance API: http://localhost:5004
- BioTensor Labs API: http://localhost:5005
- MYNX NatalCare API: http://localhost:5006

## 💻 Installation

### Manual Installation

Install dependencies for each service:

```bash
# AI Diagnostics
cd ai-diagnostics/backend && npm install && cd ../frontend && npm install && cd ../..

# Medical Imaging
cd medical-imaging/backend && npm install && cd ../frontend && npm install && cd ../..

# Biosensing
cd biosensing/backend && npm install && cd ../frontend && npm install && cd ../..

# HIPAA Compliance
cd hipaa-compliance/backend && npm install && cd ../frontend && npm install && cd ../..

# BioTensor Labs
cd biotensor-labs/backend && npm install && cd ../frontend && npm install && cd ../..

# MYNX NatalCare
cd mynx-natalcare/backend && npm install && cd ../frontend && npm install && cd ../..
```

## 🎮 Usage

### Start Individual Services

```bash
# AI Diagnostics
cd ai-diagnostics/backend && npm run dev &
cd ai-diagnostics/frontend && npm run dev &

# Or use the convenience scripts
./start-all.sh    # Start all services
./stop-all.sh     # Stop all services
```

### Development Mode

Each service can be run independently in development mode:

```bash
# Backend (with hot reload)
cd <service>/backend
npm run dev

# Frontend (with hot reload)
cd <service>/frontend
npm run dev
```

### Production Build

```bash
# Build all services
for service in ai-diagnostics medical-imaging biosensing hipaa-compliance biotensor-labs mynx-natalcare; do
  cd $service/backend && npm run build && cd ../..
  cd $service/frontend && npm run build && cd ../..
done
```

## 📚 API Documentation

Each service exposes a RESTful API. Example endpoints:

### AI Diagnostics API (Port 5001)

```bash
# Health check
GET /health

# Get diagnostics
GET /api/v1/diagnostics

# Run analysis
POST /api/v1/diagnostics/analyze
Content-Type: application/json
{
  "patientData": {...}
}

# Get models
GET /api/v1/models
```

### Medical Imaging API (Port 5002)

```bash
# Get studies
GET /api/v1/studies

# Analyze image
POST /api/v1/analyze
Content-Type: application/json
{
  "studyId": "STU-001",
  "imageData": "..."
}

# Get reports
GET /api/v1/reports
```

*See individual service README files for complete API documentation.*

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Individual Docker Builds

```bash
# Build image
docker build -t biomedical/ai-diagnostics:latest ./ai-diagnostics

# Run container
docker run -p 5001:5001 -p 3007:3007 biomedical/ai-diagnostics:latest
```

## 🔒 Security

### HIPAA Compliance
- AES-256-GCM encryption at rest
- TLS 1.3 for data in transit
- Comprehensive audit logging
- Role-based access control (RBAC)
- Multi-factor authentication (MFA) ready

### Security Features
- Helmet.js for HTTP headers
- CORS protection
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection

### Environment Variables

Create `.env` files for each service:

```bash
# Backend .env example
PORT=5001
NODE_ENV=production
CORS_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET=your-secret-key
ENCRYPTION_KEY=your-encryption-key
```

## 🚢 Deployment

### AWS Deployment

The platform is designed for deployment on AWS:

- **Compute**: EKS (Kubernetes)
- **Database**: RDS PostgreSQL + ElastiCache Redis
- **Storage**: S3 with encryption
- **Security**: KMS, CloudTrail, WAF
- **Monitoring**: CloudWatch, X-Ray

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n biomedical

# Access services
kubectl port-forward svc/ai-diagnostics 3007:3007
```

## 📊 Monitoring

### Logs

Logs are stored in the `logs/` directory:

```bash
# View backend logs
tail -f logs/ai-diagnostics-backend.log

# View frontend logs
tail -f logs/ai-diagnostics-frontend.log

# View all logs
tail -f logs/*.log
```

### Health Checks

Each backend service exposes a `/health` endpoint:

```bash
# Check all services
for port in 5001 5002 5003 5004 5005 5006; do
  curl http://localhost:$port/health
done
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow TypeScript best practices
- Write unit tests for new features
- Update documentation
- Ensure HIPAA compliance
- Follow security best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

**M.Y. Engineering and Technologies**
- Email: platform@myengineering.tech
- Phone: (800) 100-2000

## 🙏 Acknowledgments

- Built with modern healthcare technology standards
- Designed for HIPAA compliance
- FDA approval readiness
- Enterprise-grade security

## 📞 Support

For support and questions:
- Email: support@myengineering.tech
- Documentation: https://docs.biomedical-platform.com
- Issues: GitHub Issues

---

**⚕️ Built for Healthcare • 🔒 HIPAA Compliant • 🚀 Production Ready**
