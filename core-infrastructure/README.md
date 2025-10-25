# Core Infrastructure - HIPAA-Compliant AI/ML Platform

## 🎯 Overview

This is the **foundational infrastructure** for the Biomedical Intelligence Platform, providing:
- ✅ **HIPAA-compliant data ingestion** (DICOM, FHIR, HL7, genomics)
- ✅ **ML model serving** (TensorFlow, PyTorch via NVIDIA Triton)
- ✅ **Authentication & Authorization** (OAuth 2.0, RBAC)
- ✅ **Audit logging** (45 CFR § 164.312(b) compliant)
- ✅ **Encrypted storage** (S3, PostgreSQL, MongoDB)

## 📂 Project Structure

```
core-infrastructure/
├── data-pipeline/          # Multi-format data ingestion
│   ├── src/
│   │   ├── dicom_ingestion_service.py      ✅ Complete
│   │   ├── fhir_ingestion_service.py       ✅ Complete
│   │   ├── genomic_ingestion_service.py    ✅ Complete
│   │   ├── storage_manager.py              ✅ Complete
│   │   └── data_validator.py               ✅ Complete
│   ├── tests/
│   ├── config/
│   └── requirements.txt                     ✅ Complete
│
├── ml-serving/             # Model serving infrastructure
│   ├── src/
│   │   ├── triton_config.py                ✅ Complete
│   │   ├── model_registry.py               ✅ Complete
│   │   ├── ab_testing_service.py           ✅ Complete
│   │   └── gpu_scheduler.py                ✅ Complete
│   └── kubernetes/
│
├── auth-service/           # Authentication & authorization
│   ├── src/
│   │   ├── auth_service.py                 ⏳ Pending
│   │   ├── rbac_service.py                 ⏳ Pending
│   │   └── token_manager.py                ⏳ Pending
│   └── keycloak/
│
└── audit-service/          # HIPAA audit logging
    ├── src/
    │   ├── audit_logger.py                 ⏳ Pending
    │   ├── compliance_reporter.py          ⏳ Pending
    │   └── siem_integration.py             ⏳ Pending
    └── config/
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd core-infrastructure/data-pipeline
pip install -r requirements.txt
```

### 2. Test DICOM Ingestion (Local Mode)

```python
from src.dicom_ingestion_service import DICOMIngestionService

# Initialize service (local development mode)
service = DICOMIngestionService(
    s3_bucket="test-bucket",
    local_storage=True  # Uses ./dicom_storage directory
)

# Ingest a DICOM file
result = service.ingest_dicom(
    file_path="/path/to/chest_xray.dcm",
    patient_pseudonym="PATIENT_12345"
)

print(f"Success: {result['success']}")
print(f"Storage Key: {result['storage_key']}")
print(f"Content Hash: {result['content_hash']}")
```

### 3. Test FHIR Ingestion

```python
from src.fhir_ingestion_service import FHIRIngestionService

service = FHIRIngestionService()

# Process FHIR Bundle
with open('patient_bundle.json', 'r') as f:
    bundle_json = f.read()

result = service.ingest_fhir_bundle(bundle_json)
print(f"Processed: {result['processed']}")
```

## 🔐 HIPAA Compliance Features

### De-Identification (DICOM)

Automatic removal of **18 HIPAA identifiers**:
- ✅ Names, addresses, dates (except year)
- ✅ Telephone numbers, SSN, MRN
- ✅ Device serial numbers, IP addresses
- ✅ Full-face photos, biometric identifiers

**Method:** DICOM PS 3.15 Annex E (Safe Harbor)

### Encryption

- **At Rest:** AES-256 (AWS KMS or local encryption)
- **In Transit:** TLS 1.3
- **Database:** Transparent Data Encryption (TDE)

### Audit Logging

All PHI access is logged with:
- Timestamp (UTC)
- User ID
- Resource accessed
- Action performed
- IP address
- Success/failure

## 📊 What's Been Built (Week 1 - Day 1-2)

### ✅ DICOM Ingestion Service

**Features:**
- Reads and validates DICOM files
- Automatic PHI removal (18 identifiers)
- Content integrity verification (SHA-256)
- Encrypted storage (S3 or local)
- Metadata extraction

**Example:**
```python
# De-identifies this:
PatientName: "John Doe"
PatientID: "MRN-123456"
StudyDate: "20250125"

# Into this:
PatientID: "a3f8b2e9c1d4"  # Pseudonym
StudyDate: "20250101"       # Year only
PatientName: [REMOVED]
```

**Output:**
```json
{
  "success": true,
  "storage_key": "dicom/PATIENT_12345/CT/1.2.840.10008.dcm",
  "content_hash": "a7f3c2e9...",
  "metadata": {
    "modality": "CT",
    "body_part": "CHEST",
    "image_dimensions": {"rows": 512, "columns": 512}
  }
}
```

### ✅ FHIR/HL7 Ingestion Service

**Supported Resources:**
- Patient (demographics)
- Observation (vitals, labs)
- Condition (diagnoses)
- Procedure (treatments)
- Medication (prescriptions)

**De-Identification:**
- Dates → Year-Month only
- ZIP codes → First 3 digits
- Ages > 89 → Set to 90

**Example Output:**
```json
{
  "success": true,
  "total_entries": 150,
  "processed": {
    "patients": 1,
    "observations": 120,
    "conditions": 15,
    "procedures": 10,
    "medications": 4
  }
}
```

### ✅ Genomic Data Ingestion Service

**Supported Formats:**
- **VCF** (Variant Call Format) - SNPs, indels, structural variants
- **BAM/SAM/CRAM** - Aligned sequencing reads
- **FASTQ** - Raw sequencing reads (single-end and paired-end)

**Features:**
- Variant extraction with ClinVar annotations
- Alignment statistics calculation
- Quality metrics for sequencing data
- Pharmacogenomics gene identification (CYP2D6, CYP2C19, TPMT, DPYD, etc.)
- Encrypted storage for genomic files

**Example Usage:**
```python
from src.genomic_ingestion_service import GenomicIngestionService

service = GenomicIngestionService(local_storage=True)

# Ingest VCF file
result = service.ingest_vcf(
    file_path="/path/to/patient.vcf.gz",
    patient_pseudonym="PATIENT_12345",
    sample_metadata={"sequencing_platform": "Illumina NovaSeq"}
)

print(f"Variants processed: {result['variant_count']}")
print(f"Storage key: {result['storage_key']}")

# Annotate pharmacogenomics variants
pgx_result = service.annotate_pharmacogenomics(
    vcf_storage_key=result['storage_key']
)

print(f"PGx variants found: {len(pgx_result['pgx_variants'])}")
```

**Output:**
```json
{
  "success": true,
  "file_type": "vcf",
  "variant_count": 3547892,
  "storage_key": "genomics/PATIENT_12345/vcf/a7f3c2e9.json",
  "content_hash": "a7f3c2e9...",
  "metadata": {
    "reference_genome": "GRCh38",
    "sample_names": ["SAMPLE_001"],
    "contigs": [{"id": "chr1", "length": 248956422}, ...]
  }
}
```

### ✅ Storage Manager

**Unified storage interface** for all biomedical data with encryption and HIPAA compliance.

**Storage Backends:**
- **PostgreSQL** - Structured clinical data (patients, observations, conditions, genomic variants)
- **MongoDB** - Unstructured data (FHIR resources, DICOM metadata)
- **S3/Local** - Large files (DICOM images, BAM/FASTQ files)
- **Redis** - Session caching, temporary data

**Database Schema (PostgreSQL):**
- `patients` - De-identified patient demographics
- `dicom_studies` - Medical imaging metadata
- `observations` - Vitals and lab results (LOINC/SNOMED coded)
- `conditions` - Diagnoses (ICD-10 coded)
- `genomic_variants` - SNPs, indels, clinical variants
- `audit_log` - Complete access logging for HIPAA compliance

**Example Usage:**
```python
from src.storage_manager import StorageManager

# Production configuration
storage = StorageManager(
    postgres_config={
        'host': 'biomedical-db.us-east-1.rds.amazonaws.com',
        'database': 'biomedical_db',
        'user': 'admin',
        'password': os.environ['DB_PASSWORD']
    },
    mongodb_config={
        'uri': 'mongodb+srv://cluster.mongodb.net',
        'database': 'biomedical_metadata'
    },
    s3_config={
        'bucket': 'biomedical-data-prod',
        'kms_key_id': 'arn:aws:kms:...'
    },
    encryption_key=os.environ['ENCRYPTION_KEY'].encode(),
    local_mode=False
)

# Store patient data
storage.store_patient({
    'id': 'original_id_123',
    'pseudonym': 'PATIENT_12345',
    'gender': 'F',
    'birth_year': 1985,
    'age': 40,
    'state': 'CA'
})

# Store DICOM file
result = storage.store_file(
    file_path='/path/to/scan.dcm',
    storage_key='dicom/PATIENT_12345/CT/abc123.dcm',
    encrypt=True
)

# Audit log (required for HIPAA)
storage.log_audit({
    'user_id': 'physician_001',
    'action': 'VIEW',
    'resource_type': 'dicom_study',
    'resource_id': 'abc123',
    'patient_pseudonym': 'PATIENT_12345',
    'ip_address': '10.0.1.50',
    'success': True
})

storage.close()
```

**Security Features:**
- Server-side encryption (AES-256) for all files
- Fernet encryption for sensitive data at rest
- AWS KMS integration for key management
- Complete audit trail of all PHI access
- Connection pooling for performance
- SSL/TLS for all database connections

### ✅ Data Validator

**Comprehensive data quality assurance** with schema validation and statistical analysis.

**Validation Types:**
1. **Schema Validation** (Pydantic) - Type checking, format validation, cross-field validation
2. **Completeness Checks** - Missing field detection, empty field identification
3. **Outlier Detection** - Z-score method, Interquartile Range (IQR) method
4. **Quality Metrics** - Dataset completeness, duplicate detection, field-level statistics

**Schemas:**
- `PatientSchema` - Demographics with age/birth_year consistency checks
- `ObservationSchema` - Vitals/labs with code-specific range validation (LOINC)
- `GenomicVariantSchema` - Chromosome, position, allele validation
- `DICOMMetadataSchema` - Modality, study metadata validation

**Example Usage:**
```python
from src.data_validator import DataValidator

validator = DataValidator()

# Validate patient data
patient_data = {
    'patient_id': 'original_123',
    'pseudonym': 'PATIENT_12345',
    'gender': 'F',
    'birth_year': 1985,
    'age': 40,
    'state': 'CA'
}

is_valid, error, validated_data = validator.validate_patient(patient_data)
print(f"Valid: {is_valid}")

# Check completeness
required_fields = ['patient_id', 'pseudonym', 'gender', 'birth_year']
completeness = validator.check_completeness(patient_data, required_fields)
print(f"Completeness: {completeness['completeness_ratio']*100:.1f}%")

# Detect outliers in heart rate data
heart_rates = [72, 68, 75, 180, 70, 73, 71, 220, 74]  # 180, 220 are outliers
outliers_zscore = validator.detect_outliers_zscore(heart_rates, threshold=2.0)
print(f"Outliers (Z-score): {outliers_zscore['outlier_count']}")

outliers_iqr = validator.detect_outliers_iqr(heart_rates)
print(f"Outliers (IQR): {outliers_iqr['outlier_count']}")

# Calculate quality metrics for a dataset
observations = [...]  # List of observation records
metrics = validator.calculate_quality_metrics(observations, 'observation')
print(f"Average completeness: {metrics['avg_completeness']*100:.1f}%")
print(f"Duplicates found: {metrics['duplicate_count']}")

# Get validation statistics
stats = validator.get_validation_statistics()
print(f"Pass rate: {stats['pass_rate']*100:.1f}%")
```

**Validation Features:**
- **Type Safety:** Strong typing with Pydantic ensures data integrity
- **Range Validation:** Code-specific ranges for clinical observations (e.g., heart rate 0-250 bpm)
- **Format Validation:** Regex patterns for standardized codes (gender, chromosome, genotype)
- **Cross-field Validation:** Consistency checks (e.g., age vs birth_year)
- **Statistical Outlier Detection:** Both parametric (Z-score) and non-parametric (IQR) methods
- **Quality Reporting:** Completeness ratios, duplicate detection, field-level metrics

## 🚀 ML Model Serving Infrastructure

### ✅ NVIDIA Triton Configuration Manager

**Production-grade model serving** with NVIDIA Triton Inference Server support.

**Supported Platforms:**
- TensorFlow SavedModel
- PyTorch TorchScript
- ONNX Runtime
- TensorRT
- Python Backend

**Features:**
- Automatic config.pbtxt generation for Triton
- Dynamic batching configuration
- Multi-GPU instance groups
- Model ensembles (pipelines)
- Version policies (latest, all, specific)
- Model warmup support

**Example - Medical Imaging Model:**
```python
from src.triton_config import TritonModelConfig, Platform, ModelInput, ModelOutput

config = TritonModelConfig(model_repository_path="./model_repository")

# Generate config for chest X-ray classifier
config.generate_medical_imaging_config(
    model_name="chest_xray_classifier",
    image_size=224,
    num_classes=14  # 14 pathologies
)

# Creates:
# model_repository/
# └── chest_xray_classifier/
#     └── config.pbtxt (with dynamic batching, GPU allocation)
```

### ✅ MLflow Model Registry

**Complete ML lifecycle management** with versioning, staging, and production deployment.

**Lifecycle Stages:**
1. **None** → New model registered
2. **Staging** → Testing in staging environment
3. **Production** → Deployed to production
4. **Archived** → Retired/superseded

**Features:**
- PyTorch and TensorFlow model registration
- Automatic versioning
- Stage transitions with archive
- Model comparison (metrics diff)
- Rollback to previous versions
- Metadata and tags management

**Example - Model Deployment:**
```python
from src.model_registry import ModelRegistry, ModelStage

registry = ModelRegistry(tracking_uri="http://mlflow:5000")

# Register PyTorch model
result = registry.register_pytorch_model(
    model=chest_xray_model,
    model_name="chest_xray_classifier",
    example_input=sample_tensor,
    metadata={"accuracy": 0.94, "f1_score": 0.92}
)

# Promote to staging
registry.promote_to_staging("chest_xray_classifier", version=2)

# Compare versions
comparison = registry.compare_models(
    "chest_xray_classifier",
    version1=1,
    version2=2,
    metrics=["accuracy", "f1_score"]
)

# Promote to production (archives current production model)
registry.promote_to_production("chest_xray_classifier", version=2)

# Rollback if needed
registry.rollback_to_version("chest_xray_classifier", version=1)
```

### ✅ A/B Testing Service

**Statistical A/B testing framework** for safe model deployment and comparison.

**Traffic Splitting Strategies:**
- **Random** - Random assignment per request
- **Hash-based** - Consistent per user (same user always gets same version)
- **Weighted** - Custom traffic percentages
- **Canary** - Small percentage to new version (gradual rollout)

**Statistical Analysis:**
- Independent t-test for significance
- Cohen's d for effect size
- Confidence intervals
- Automatic winner determination

**Example - Canary Deployment:**
```python
from src.ab_testing_service import ABTestingService, SplitStrategy

ab_service = ABTestingService(min_sample_size=100, confidence_level=0.95)

# Create experiment: 10% traffic to new version
experiment = ab_service.create_experiment(
    experiment_id="chest_xray_v2_canary",
    model_name="chest_xray_classifier",
    control_version=1,  # Current production
    treatment_version=2,  # New candidate
    traffic_split=0.10,  # 10% canary
    split_strategy=SplitStrategy.HASH_BASED,
    success_metric="accuracy",
    duration_hours=48
)

ab_service.start_experiment("chest_xray_v2_canary")

# Route requests
for user_id in users:
    version, variant = ab_service.route_request(
        "chest_xray_v2_canary",
        user_id=user_id
    )

    prediction = models[version].predict(image)

    ab_service.record_prediction(
        "chest_xray_v2_canary",
        variant=variant,
        prediction=prediction,
        ground_truth=label,
        latency_ms=inference_time
    )

# Analyze results
analysis = ab_service.analyze_experiment("chest_xray_v2_canary")

if analysis['winner'] == 'treatment' and analysis['statistical_test']['is_significant']:
    print(f"✅ Treatment wins! Improvement: {analysis['means']['relative_improvement']:.1f}%")
    print(f"Recommendation: {analysis['recommendation']}")
```

**Analysis Output:**
```json
{
  "winner": "treatment",
  "means": {
    "control": 0.92,
    "treatment": 0.94,
    "relative_improvement": 2.17
  },
  "statistical_test": {
    "p_value": 0.003,
    "is_significant": true
  },
  "effect_size": {
    "cohens_d": 0.68,
    "interpretation": "medium"
  },
  "recommendation": "DEPLOY treatment version - significant improvement with meaningful effect size"
}
```

### ✅ GPU Resource Scheduler

**Dynamic GPU allocation** and load balancing for optimal resource utilization.

**Scheduling Strategies:**
- **First Fit** - Assign to first available GPU
- **Best Fit** - GPU with most free memory
- **Round Robin** - Distribute evenly
- **Least Loaded** - GPU with lowest utilization

**Features:**
- Automatic GPU discovery (nvidia-smi)
- Dynamic allocation based on memory requirements
- Load rebalancing across GPUs
- Health monitoring (temperature, memory, utilization)
- Multi-model GPU sharing

**Example - GPU Management:**
```python
from src.gpu_scheduler import GPUScheduler, SchedulingStrategy

scheduler = GPUScheduler(scheduling_strategy=SchedulingStrategy.LEAST_LOADED)

# Allocate GPUs for models
gpu_id = scheduler.allocate_gpu(
    "chest_xray_classifier",
    memory_required_mb=4000
)
print(f"Allocated GPU {gpu_id}")

# Get cluster utilization
stats = scheduler.get_cluster_utilization()
print(f"Cluster utilization: {stats['avg_compute_utilization_percent']:.1f}%")
print(f"Available GPUs: {stats['available_gpus']}/{stats['total_gpus']}")

# Check health
health = scheduler.check_gpu_health()
if health['status'] == 'unhealthy':
    print(f"⚠️ GPU issues detected: {health['issues']}")

# Rebalance load
rebalance_report = scheduler.rebalance_gpus()
print(f"Migrated {rebalance_report['migrations_performed']} models")

# Deallocate when done
scheduler.deallocate_gpu("chest_xray_classifier")
```

**Monitoring Output:**
```json
{
  "total_gpus": 4,
  "avg_compute_utilization_percent": 67.5,
  "memory_utilization_percent": 72.3,
  "total_models": 8,
  "models_per_gpu": {
    "0": 2,
    "1": 3,
    "2": 2,
    "3": 1
  }
}
```

## 📈 Next Steps (Week 4-5 - Authentication & Audit Logging)

## 🛠️ Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| Storage | Local files | AWS S3 + KMS |
| Database | SQLite | PostgreSQL RDS |
| Encryption | Optional | Required |
| Audit Logging | Console | SIEM + S3 |
| Authentication | Disabled | OAuth 2.0 |

## 📝 Configuration

Create `.env` file:

```bash
# AWS Configuration
AWS_REGION=us-east-1
S3_BUCKET_DICOM=biomedical-dicom-prod
S3_BUCKET_GENOMICS=biomedical-genomics-prod
KMS_KEY_ID=arn:aws:kms:us-east-1:123456789:key/...

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=biomedical_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=<secret>

MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=biomedical_metadata

# Security
JWT_SECRET_KEY=<generate-with-openssl>
ENCRYPTION_KEY=<generate-with-openssl>

# Logging
LOG_LEVEL=INFO
SIEM_ENDPOINT=https://splunk.example.com
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Test specific service
pytest tests/test_dicom_ingestion.py -v
```

## 📚 Resources

### HIPAA Compliance
- [45 CFR § 164.312](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html) - Technical Safeguards
- [DICOM PS 3.15 Annex E](https://dicom.nema.org/medical/dicom/current/output/chtml/part15/chapter_E.html) - De-identification
- [NIST 800-66](https://csrc.nist.gov/publications/detail/sp/800-66/rev-2/final) - HIPAA Security Rule

### Data Formats
- [DICOM Standard](https://www.dicomstandard.org/)
- [FHIR R4](https://www.hl7.org/fhir/)
- [HL7 v2.x](https://www.hl7.org/implement/standards/product_brief.cfm?product_id=185)
- [VCF Specification](https://samtools.github.io/hts-specs/VCFv4.3.pdf)

## 💰 Cost Estimate (Monthly)

```
Development (local):        $0
Staging (AWS):              ~$500/month
Production (AWS):           ~$3,400/month
  ├─ RDS PostgreSQL:        $730
  ├─ MongoDB Atlas:         $580
  ├─ S3 Storage:            $63
  ├─ GPU (spot):            $453
  └─ Other:                 ~$574
```

## 🤝 Contributing

This is foundational infrastructure used by all services. Changes require:
1. HIPAA compliance review
2. Security audit
3. Integration tests
4. Documentation update

## 📞 Support

- Documentation: `/docs`
- Issues: GitHub Issues
- Security: security@biomedical-platform.com

---

**Status:** Week 2-3 COMPLETE ✅ (ML Model Serving Infrastructure)
**Next Milestone:** Authentication & Authorization Service (Week 4)
**Timeline:** 4-6 weeks total (Weeks 1-3 complete - 50% done!)
