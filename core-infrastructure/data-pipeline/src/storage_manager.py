"""
Storage Manager - Unified storage interface for biomedical data
Handles PostgreSQL, MongoDB, S3, and Redis with encryption
"""

import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import os

# Database clients
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.pool import SimpleConnectionPool
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# AWS S3
import boto3
from botocore.exceptions import ClientError

# Redis for caching
import redis

# Encryption
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StorageManager:
    """
    Unified storage manager for biomedical platform

    Manages:
    - PostgreSQL: Structured clinical data, patient records
    - MongoDB: Unstructured metadata, FHIR resources
    - S3: Large files (DICOM, BAM, FASTQ)
    - Redis: Session cache, temporary data
    """

    def __init__(
        self,
        postgres_config: Optional[Dict] = None,
        mongodb_config: Optional[Dict] = None,
        s3_config: Optional[Dict] = None,
        redis_config: Optional[Dict] = None,
        encryption_key: Optional[bytes] = None,
        local_mode: bool = True
    ):
        """
        Initialize storage manager

        Args:
            postgres_config: PostgreSQL connection params
            mongodb_config: MongoDB connection params
            s3_config: S3 bucket configuration
            redis_config: Redis connection params
            encryption_key: Fernet encryption key
            local_mode: Use local storage for development
        """
        self.local_mode = local_mode

        # Encryption
        self.encryption_key = encryption_key
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            logger.warning("No encryption key provided - data will not be encrypted")
            self.cipher = None

        # Initialize PostgreSQL
        if postgres_config and not local_mode:
            self._init_postgres(postgres_config)
        else:
            self.pg_pool = None
            logger.info("PostgreSQL: Disabled (local mode)")

        # Initialize MongoDB
        if mongodb_config and not local_mode:
            self._init_mongodb(mongodb_config)
        else:
            self.mongo_client = None
            self.mongo_db = None
            logger.info("MongoDB: Disabled (local mode)")

        # Initialize S3
        if s3_config and not local_mode:
            self._init_s3(s3_config)
        else:
            self.s3_client = None
            self.s3_bucket = None
            # Local storage directory
            self.local_storage_dir = Path('./storage')
            self.local_storage_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"S3: Using local storage at {self.local_storage_dir}")

        # Initialize Redis
        if redis_config and not local_mode:
            self._init_redis(redis_config)
        else:
            self.redis_client = None
            logger.info("Redis: Disabled (local mode)")

    # ==================== INITIALIZATION ====================

    def _init_postgres(self, config: Dict):
        """Initialize PostgreSQL connection pool"""
        try:
            self.pg_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=config.get('host', 'localhost'),
                port=config.get('port', 5432),
                database=config.get('database', 'biomedical_db'),
                user=config.get('user', 'postgres'),
                password=config.get('password', ''),
                sslmode=config.get('sslmode', 'require')
            )
            logger.info("PostgreSQL connection pool initialized")

            # Create tables if they don't exist
            self._create_postgres_tables()

        except Exception as e:
            logger.error(f"PostgreSQL initialization failed: {str(e)}")
            raise

    def _init_mongodb(self, config: Dict):
        """Initialize MongoDB client"""
        try:
            self.mongo_client = MongoClient(
                config.get('uri', 'mongodb://localhost:27017'),
                maxPoolSize=50,
                minPoolSize=10
            )

            db_name = config.get('database', 'biomedical_metadata')
            self.mongo_db = self.mongo_client[db_name]

            # Test connection
            self.mongo_client.admin.command('ping')
            logger.info(f"MongoDB connected: {db_name}")

            # Create collections and indexes
            self._create_mongodb_collections()

        except Exception as e:
            logger.error(f"MongoDB initialization failed: {str(e)}")
            raise

    def _init_s3(self, config: Dict):
        """Initialize S3 client"""
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=config.get('region', 'us-east-1'),
                aws_access_key_id=config.get('access_key_id'),
                aws_secret_access_key=config.get('secret_access_key')
            )

            self.s3_bucket = config.get('bucket')
            self.kms_key_id = config.get('kms_key_id')

            # Test connection
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            logger.info(f"S3 connected: {self.s3_bucket}")

        except Exception as e:
            logger.error(f"S3 initialization failed: {str(e)}")
            raise

    def _init_redis(self, config: Dict):
        """Initialize Redis client"""
        try:
            self.redis_client = redis.Redis(
                host=config.get('host', 'localhost'),
                port=config.get('port', 6379),
                password=config.get('password'),
                db=config.get('db', 0),
                decode_responses=True
            )

            # Test connection
            self.redis_client.ping()
            logger.info("Redis connected")

        except Exception as e:
            logger.error(f"Redis initialization failed: {str(e)}")
            raise

    # ==================== SCHEMA CREATION ====================

    def _create_postgres_tables(self):
        """Create PostgreSQL tables for clinical data"""
        conn = self.pg_pool.getconn()
        cursor = conn.cursor()

        try:
            # Patients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id VARCHAR(64) PRIMARY KEY,
                    pseudonym VARCHAR(64) UNIQUE NOT NULL,
                    gender VARCHAR(10),
                    birth_year INTEGER,
                    age INTEGER,
                    state VARCHAR(2),
                    postal_code_prefix VARCHAR(3),
                    deceased BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_patients_pseudonym ON patients(pseudonym);
                CREATE INDEX IF NOT EXISTS idx_patients_age ON patients(age);
            """)

            # DICOM metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dicom_studies (
                    study_id VARCHAR(64) PRIMARY KEY,
                    patient_pseudonym VARCHAR(64) REFERENCES patients(pseudonym),
                    storage_key TEXT NOT NULL,
                    content_hash VARCHAR(64) NOT NULL,
                    modality VARCHAR(10),
                    body_part VARCHAR(50),
                    study_date DATE,
                    image_count INTEGER,
                    file_size_bytes BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_dicom_patient ON dicom_studies(patient_pseudonym);
                CREATE INDEX IF NOT EXISTS idx_dicom_modality ON dicom_studies(modality);
                CREATE INDEX IF NOT EXISTS idx_dicom_date ON dicom_studies(study_date);
            """)

            # Observations table (vitals, labs)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS observations (
                    observation_id VARCHAR(64) PRIMARY KEY,
                    patient_pseudonym VARCHAR(64) REFERENCES patients(pseudonym),
                    category VARCHAR(50),
                    code VARCHAR(20),
                    code_system VARCHAR(50),
                    display_name TEXT,
                    value_numeric NUMERIC,
                    value_text TEXT,
                    unit VARCHAR(20),
                    reference_low NUMERIC,
                    reference_high NUMERIC,
                    effective_date DATE,
                    status VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_obs_patient ON observations(patient_pseudonym);
                CREATE INDEX IF NOT EXISTS idx_obs_code ON observations(code);
                CREATE INDEX IF NOT EXISTS idx_obs_category ON observations(category);
                CREATE INDEX IF NOT EXISTS idx_obs_date ON observations(effective_date);
            """)

            # Conditions table (diagnoses)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conditions (
                    condition_id VARCHAR(64) PRIMARY KEY,
                    patient_pseudonym VARCHAR(64) REFERENCES patients(pseudonym),
                    code VARCHAR(20),
                    code_system VARCHAR(50),
                    display_name TEXT,
                    clinical_status VARCHAR(20),
                    verification_status VARCHAR(20),
                    onset_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_cond_patient ON conditions(patient_pseudonym);
                CREATE INDEX IF NOT EXISTS idx_cond_code ON conditions(code);
                CREATE INDEX IF NOT EXISTS idx_cond_date ON conditions(onset_date);
            """)

            # Genomic variants table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS genomic_variants (
                    variant_id SERIAL PRIMARY KEY,
                    patient_pseudonym VARCHAR(64) REFERENCES patients(pseudonym),
                    vcf_storage_key TEXT NOT NULL,
                    chromosome VARCHAR(10),
                    position BIGINT,
                    ref_allele TEXT,
                    alt_allele TEXT,
                    genotype VARCHAR(10),
                    gene VARCHAR(50),
                    impact VARCHAR(20),
                    clinical_significance VARCHAR(50),
                    allele_frequency NUMERIC,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_var_patient ON genomic_variants(patient_pseudonym);
                CREATE INDEX IF NOT EXISTS idx_var_gene ON genomic_variants(gene);
                CREATE INDEX IF NOT EXISTS idx_var_chr_pos ON genomic_variants(chromosome, position);
            """)

            # Audit log table (HIPAA compliance)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id VARCHAR(64),
                    action VARCHAR(50),
                    resource_type VARCHAR(50),
                    resource_id VARCHAR(64),
                    patient_pseudonym VARCHAR(64),
                    ip_address INET,
                    success BOOLEAN,
                    details JSONB
                );

                CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
                CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
                CREATE INDEX IF NOT EXISTS idx_audit_patient ON audit_log(patient_pseudonym);
            """)

            conn.commit()
            logger.info("PostgreSQL tables created successfully")

        except Exception as e:
            conn.rollback()
            logger.error(f"Table creation failed: {str(e)}")
            raise
        finally:
            cursor.close()
            self.pg_pool.putconn(conn)

    def _create_mongodb_collections(self):
        """Create MongoDB collections and indexes"""
        try:
            # FHIR resources collection
            fhir_collection = self.mongo_db['fhir_resources']
            fhir_collection.create_index([('resourceType', 1), ('id', 1)], unique=True)
            fhir_collection.create_index('subject.reference')
            fhir_collection.create_index('code.coding.code')

            # DICOM metadata collection
            dicom_collection = self.mongo_db['dicom_metadata']
            dicom_collection.create_index('patient_pseudonym')
            dicom_collection.create_index('study_id', unique=True)
            dicom_collection.create_index('modality')

            # Genomic metadata collection
            genomic_collection = self.mongo_db['genomic_metadata']
            genomic_collection.create_index('patient_pseudonym')
            genomic_collection.create_index('file_type')
            genomic_collection.create_index('storage_key', unique=True)

            # Model predictions collection
            predictions_collection = self.mongo_db['model_predictions']
            predictions_collection.create_index('patient_pseudonym')
            predictions_collection.create_index('model_name')
            predictions_collection.create_index('timestamp')

            logger.info("MongoDB collections and indexes created")

        except Exception as e:
            logger.error(f"MongoDB collection creation failed: {str(e)}")
            raise

    # ==================== PATIENT OPERATIONS ====================

    def store_patient(self, patient_data: Dict) -> bool:
        """Store patient demographics in PostgreSQL"""
        if not self.pg_pool:
            logger.warning("PostgreSQL not available - skipping patient storage")
            return False

        conn = self.pg_pool.getconn()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO patients (
                    patient_id, pseudonym, gender, birth_year, age,
                    state, postal_code_prefix, deceased
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (patient_id) DO UPDATE SET
                    gender = EXCLUDED.gender,
                    birth_year = EXCLUDED.birth_year,
                    age = EXCLUDED.age,
                    state = EXCLUDED.state,
                    postal_code_prefix = EXCLUDED.postal_code_prefix,
                    deceased = EXCLUDED.deceased,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                patient_data.get('id'),
                patient_data.get('pseudonym'),
                patient_data.get('gender'),
                patient_data.get('birth_year'),
                patient_data.get('age'),
                patient_data.get('state'),
                patient_data.get('postal_code_prefix'),
                patient_data.get('deceased', False)
            ))

            conn.commit()
            logger.info(f"Patient stored: {patient_data.get('pseudonym')}")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Patient storage failed: {str(e)}")
            return False
        finally:
            cursor.close()
            self.pg_pool.putconn(conn)

    def get_patient(self, pseudonym: str) -> Optional[Dict]:
        """Retrieve patient by pseudonym"""
        if not self.pg_pool:
            return None

        conn = self.pg_pool.getconn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute("""
                SELECT * FROM patients WHERE pseudonym = %s
            """, (pseudonym,))

            result = cursor.fetchone()
            return dict(result) if result else None

        finally:
            cursor.close()
            self.pg_pool.putconn(conn)

    # ==================== DICOM OPERATIONS ====================

    def store_dicom_metadata(self, dicom_data: Dict) -> bool:
        """Store DICOM study metadata"""
        if not self.pg_pool:
            logger.warning("PostgreSQL not available")
            return False

        conn = self.pg_pool.getconn()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO dicom_studies (
                    study_id, patient_pseudonym, storage_key, content_hash,
                    modality, body_part, study_date, image_count, file_size_bytes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (study_id) DO NOTHING
            """, (
                dicom_data.get('study_id'),
                dicom_data.get('patient_pseudonym'),
                dicom_data.get('storage_key'),
                dicom_data.get('content_hash'),
                dicom_data.get('modality'),
                dicom_data.get('body_part'),
                dicom_data.get('study_date'),
                dicom_data.get('image_count', 1),
                dicom_data.get('file_size_bytes', 0)
            ))

            conn.commit()
            logger.info(f"DICOM metadata stored: {dicom_data.get('study_id')}")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"DICOM metadata storage failed: {str(e)}")
            return False
        finally:
            cursor.close()
            self.pg_pool.putconn(conn)

    # ==================== FHIR OPERATIONS ====================

    def store_fhir_resource(self, resource: Dict) -> bool:
        """Store FHIR resource in MongoDB"""
        if not self.mongo_db:
            logger.warning("MongoDB not available")
            return False

        try:
            collection = self.mongo_db['fhir_resources']

            # Add timestamp
            resource['_stored_at'] = datetime.utcnow()

            # Upsert
            collection.update_one(
                {
                    'resourceType': resource.get('resourceType'),
                    'id': resource.get('id')
                },
                {'$set': resource},
                upsert=True
            )

            logger.info(f"FHIR resource stored: {resource.get('resourceType')}/{resource.get('id')}")
            return True

        except Exception as e:
            logger.error(f"FHIR resource storage failed: {str(e)}")
            return False

    # ==================== OBJECT STORAGE (S3/Local) ====================

    def store_file(
        self,
        file_path: str,
        storage_key: str,
        encrypt: bool = True
    ) -> Dict:
        """Store file in S3 or local storage"""
        try:
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Encrypt if requested
            if encrypt and self.cipher:
                file_data = self.cipher.encrypt(file_data)

            # Calculate hash
            content_hash = hashlib.sha256(file_data).hexdigest()

            if self.local_mode:
                # Local storage
                local_path = self.local_storage_dir / storage_key
                local_path.parent.mkdir(parents=True, exist_ok=True)

                with open(local_path, 'wb') as f:
                    f.write(file_data)

                logger.info(f"File stored locally: {local_path}")

            else:
                # S3 storage
                extra_args = {}
                if self.kms_key_id:
                    extra_args = {
                        'ServerSideEncryption': 'aws:kms',
                        'SSEKMSKeyId': self.kms_key_id
                    }

                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=storage_key,
                    Body=file_data,
                    **extra_args
                )

                logger.info(f"File stored in S3: s3://{self.s3_bucket}/{storage_key}")

            return {
                'success': True,
                'storage_key': storage_key,
                'content_hash': content_hash,
                'encrypted': encrypt and self.cipher is not None
            }

        except Exception as e:
            logger.error(f"File storage failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def retrieve_file(
        self,
        storage_key: str,
        decrypt: bool = True
    ) -> Optional[bytes]:
        """Retrieve file from S3 or local storage"""
        try:
            if self.local_mode:
                # Local storage
                local_path = self.local_storage_dir / storage_key

                with open(local_path, 'rb') as f:
                    file_data = f.read()

            else:
                # S3 storage
                response = self.s3_client.get_object(
                    Bucket=self.s3_bucket,
                    Key=storage_key
                )

                file_data = response['Body'].read()

            # Decrypt if needed
            if decrypt and self.cipher:
                file_data = self.cipher.decrypt(file_data)

            return file_data

        except Exception as e:
            logger.error(f"File retrieval failed: {str(e)}")
            return None

    # ==================== AUDIT LOGGING ====================

    def log_audit(self, audit_data: Dict) -> bool:
        """Log access to PHI for HIPAA compliance"""
        if not self.pg_pool:
            logger.warning("Audit logging unavailable (PostgreSQL disabled)")
            return False

        conn = self.pg_pool.getconn()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO audit_log (
                    user_id, action, resource_type, resource_id,
                    patient_pseudonym, ip_address, success, details
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                audit_data.get('user_id'),
                audit_data.get('action'),
                audit_data.get('resource_type'),
                audit_data.get('resource_id'),
                audit_data.get('patient_pseudonym'),
                audit_data.get('ip_address'),
                audit_data.get('success', True),
                json.dumps(audit_data.get('details', {}))
            ))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Audit logging failed: {str(e)}")
            return False
        finally:
            cursor.close()
            self.pg_pool.putconn(conn)

    # ==================== CLEANUP ====================

    def close(self):
        """Close all connections"""
        if self.pg_pool:
            self.pg_pool.closeall()
            logger.info("PostgreSQL connections closed")

        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed")

        if self.redis_client:
            self.redis_client.close()
            logger.info("Redis connection closed")


if __name__ == "__main__":
    # Example usage
    storage = StorageManager(local_mode=True)

    print("Storage Manager initialized successfully")
    print("Local mode: PostgreSQL, MongoDB, Redis disabled")
    print("Using local file storage")

    storage.close()
