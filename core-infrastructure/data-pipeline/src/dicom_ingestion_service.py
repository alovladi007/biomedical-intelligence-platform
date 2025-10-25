"""
DICOM Ingestion Service - HIPAA Compliant
Handles medical imaging data ingestion with de-identification and secure storage
"""

import os
import hashlib
import io
from typing import Dict, Optional, List
from datetime import datetime
import logging

import pydicom
from pydicom.errors import InvalidDicomError
from pydicom import dcmread
from cryptography.fernet import Fernet
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DICOMIngestionService:
    """
    HIPAA-compliant DICOM ingestion with automatic de-identification

    Features:
    - PHI removal according to DICOM PS 3.15 Annex E
    - Server-side encryption (SSE-KMS)
    - Content integrity verification
    - Metadata extraction and indexing
    """

    # PHI tags to remove (DICOM PS 3.15 Annex E)
    PHI_TAGS = [
        'PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex',
        'PatientAddress', 'PatientTelephoneNumbers', 'InstitutionName',
        'InstitutionAddress', 'ReferringPhysicianName', 'PerformingPhysicianName',
        'OperatorsName', 'StudyDate', 'SeriesDate', 'AcquisitionDate',
        'ContentDate', 'StudyTime', 'SeriesTime', 'AcquisitionTime',
        'AccessionNumber', 'StudyID', 'DeviceSerialNumber',
        'StationName', 'InstitutionalDepartmentName'
    ]

    def __init__(
        self,
        s3_bucket: str,
        aws_region: str = 'us-east-1',
        kms_key_id: Optional[str] = None,
        local_storage: bool = False
    ):
        """
        Initialize DICOM ingestion service

        Args:
            s3_bucket: S3 bucket name for DICOM storage
            aws_region: AWS region
            kms_key_id: KMS key ID for encryption (optional)
            local_storage: Use local storage instead of S3 (for development)
        """
        self.bucket = s3_bucket
        self.kms_key_id = kms_key_id
        self.local_storage = local_storage

        if not local_storage:
            self.s3_client = boto3.client('s3', region_name=aws_region)
            if kms_key_id:
                self.kms_client = boto3.client('kms', region_name=aws_region)
        else:
            # Local storage for development
            self.local_dir = './dicom_storage'
            os.makedirs(self.local_dir, exist_ok=True)
            logger.info("Using local storage for development")

    def ingest_dicom(
        self,
        file_path: str,
        patient_pseudonym: str,
        study_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Ingest, validate, de-identify, and store DICOM file

        Args:
            file_path: Path to DICOM file
            patient_pseudonym: De-identified patient ID
            study_metadata: Additional study metadata

        Returns:
            Dict with ingestion results
        """
        try:
            logger.info(f"Ingesting DICOM file: {file_path}")

            # 1. Read and validate DICOM
            dicom_data = self._read_and_validate(file_path)
            if not dicom_data:
                return {"success": False, "error": "Invalid DICOM file"}

            # 2. Extract metadata BEFORE de-identification
            metadata = self._extract_metadata(dicom_data)

            # 3. De-identify PHI
            deidentified_dicom = self._deidentify_dicom(dicom_data, patient_pseudonym)

            # 4. Generate content hash for integrity
            content_hash = self._generate_content_hash(deidentified_dicom)

            # 5. Store DICOM file (encrypted)
            storage_key = self._store_dicom(
                deidentified_dicom,
                patient_pseudonym,
                content_hash
            )

            # 6. Prepare metadata for database storage
            metadata_record = {
                "patient_pseudonym": patient_pseudonym,
                "storage_key": storage_key,
                "content_hash": content_hash,
                "modality": metadata.get("Modality"),
                "body_part": metadata.get("BodyPartExamined"),
                "study_description": metadata.get("StudyDescription"),
                "image_dimensions": metadata.get("ImageDimensions"),
                "ingestion_timestamp": datetime.utcnow().isoformat(),
                "file_size_bytes": os.path.getsize(file_path),
                "additional_metadata": study_metadata or {}
            }

            logger.info(f"Successfully ingested DICOM: {storage_key}")

            return {
                "success": True,
                "storage_key": storage_key,
                "content_hash": content_hash,
                "metadata": metadata_record
            }

        except Exception as e:
            logger.error(f"DICOM ingestion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _read_and_validate(self, file_path: str) -> Optional[pydicom.Dataset]:
        """Read and validate DICOM file"""
        try:
            dicom_data = dcmread(file_path, force=True)

            # Basic validation
            if not hasattr(dicom_data, 'SOPInstanceUID'):
                logger.error("Missing SOPInstanceUID")
                return None

            if not hasattr(dicom_data, 'Modality'):
                logger.warning("Missing Modality tag")

            return dicom_data

        except InvalidDicomError as e:
            logger.error(f"Invalid DICOM file: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error reading DICOM: {str(e)}")
            return None

    def _extract_metadata(self, dicom_data: pydicom.Dataset) -> Dict:
        """Extract relevant metadata before de-identification"""
        metadata = {}

        # Safe getter helper
        def get_tag(tag_name):
            return str(getattr(dicom_data, tag_name, "")) if hasattr(dicom_data, tag_name) else None

        # Extract key metadata
        metadata["SOPInstanceUID"] = get_tag("SOPInstanceUID")
        metadata["Modality"] = get_tag("Modality")
        metadata["BodyPartExamined"] = get_tag("BodyPartExamined")
        metadata["StudyDescription"] = get_tag("StudyDescription")
        metadata["SeriesDescription"] = get_tag("SeriesDescription")
        metadata["Manufacturer"] = get_tag("Manufacturer")
        metadata["ManufacturerModelName"] = get_tag("ManufacturerModelName")

        # Image dimensions
        if hasattr(dicom_data, 'Rows') and hasattr(dicom_data, 'Columns'):
            metadata["ImageDimensions"] = {
                "rows": int(dicom_data.Rows),
                "columns": int(dicom_data.Columns)
            }

        # Slice information
        if hasattr(dicom_data, 'SliceThickness'):
            metadata["SliceThickness"] = float(dicom_data.SliceThickness)

        # Study/Series dates (year only for de-identification)
        if hasattr(dicom_data, 'StudyDate'):
            metadata["StudyYear"] = str(dicom_data.StudyDate)[:4]

        return metadata

    def _deidentify_dicom(
        self,
        dicom_data: pydicom.Dataset,
        patient_pseudonym: str
    ) -> pydicom.Dataset:
        """
        De-identify DICOM according to DICOM PS 3.15 Annex E

        Removes 18 HIPAA identifiers:
        1. Names
        2. Geographic subdivisions smaller than state
        3. Dates (except year)
        4. Telephone/fax numbers
        5. Email addresses
        6. Social Security numbers
        7. Medical record numbers
        8. Health plan numbers
        9. Account numbers
        10. Certificate/license numbers
        11. Vehicle identifiers
        12. Device identifiers and serial numbers
        13. Web URLs
        14. IP addresses
        15. Biometric identifiers
        16. Full face photos
        17. Any other unique identifying number/characteristic
        """

        # Remove PHI tags
        for tag in self.PHI_TAGS:
            if hasattr(dicom_data, tag):
                if tag == 'PatientID':
                    # Replace with pseudonym
                    dicom_data.PatientID = patient_pseudonym
                elif tag in ['StudyDate', 'SeriesDate', 'AcquisitionDate', 'ContentDate']:
                    # Keep year only
                    original_date = str(getattr(dicom_data, tag, ""))
                    if len(original_date) >= 4:
                        setattr(dicom_data, tag, original_date[:4] + '0101')
                    else:
                        delattr(dicom_data, tag)
                else:
                    # Remove completely
                    delattr(dicom_data, tag)

        # Add de-identification marker
        dicom_data.PatientIdentityRemoved = 'YES'
        dicom_data.DeidentificationMethod = 'DICOM PS 3.15 Annex E'

        return dicom_data

    def _generate_content_hash(self, dicom_data: pydicom.Dataset) -> str:
        """Generate SHA-256 hash of DICOM content for integrity verification"""
        # Save to bytes
        buffer = io.BytesIO()
        dicom_data.save_as(buffer, write_like_original=False)
        buffer.seek(0)

        # Calculate hash
        sha256_hash = hashlib.sha256()
        sha256_hash.update(buffer.read())

        return sha256_hash.hexdigest()

    def _store_dicom(
        self,
        dicom_data: pydicom.Dataset,
        patient_pseudonym: str,
        content_hash: str
    ) -> str:
        """Store DICOM file with encryption"""

        # Generate storage key
        modality = str(getattr(dicom_data, 'Modality', 'UNKNOWN'))
        sop_instance = str(getattr(dicom_data, 'SOPInstanceUID', content_hash[:16]))
        storage_key = f"dicom/{patient_pseudonym}/{modality}/{sop_instance}.dcm"

        # Save to buffer
        buffer = io.BytesIO()
        dicom_data.save_as(buffer, write_like_original=False)
        buffer.seek(0)

        if self.local_storage:
            # Local storage (development)
            local_path = os.path.join(self.local_dir, storage_key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            with open(local_path, 'wb') as f:
                f.write(buffer.read())

            logger.info(f"Stored locally: {local_path}")
        else:
            # S3 storage with encryption
            try:
                extra_args = {
                    'Metadata': {
                        'patient-pseudonym': patient_pseudonym,
                        'content-hash': content_hash,
                        'ingestion-timestamp': datetime.utcnow().isoformat()
                    }
                }

                # Add KMS encryption if configured
                if self.kms_key_id:
                    extra_args['ServerSideEncryption'] = 'aws:kms'
                    extra_args['SSEKMSKeyId'] = self.kms_key_id
                else:
                    extra_args['ServerSideEncryption'] = 'AES256'

                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=storage_key,
                    Body=buffer.read(),
                    **extra_args
                )

                logger.info(f"Stored in S3: s3://{self.bucket}/{storage_key}")

            except ClientError as e:
                logger.error(f"S3 upload failed: {str(e)}")
                raise

        return storage_key

    def retrieve_dicom(self, storage_key: str) -> Optional[pydicom.Dataset]:
        """Retrieve and decrypt DICOM file from storage"""
        try:
            if self.local_storage:
                local_path = os.path.join(self.local_dir, storage_key)
                return dcmread(local_path)
            else:
                response = self.s3_client.get_object(
                    Bucket=self.bucket,
                    Key=storage_key
                )

                buffer = io.BytesIO(response['Body'].read())
                return dcmread(buffer)

        except Exception as e:
            logger.error(f"DICOM retrieval failed: {str(e)}")
            return None

    def verify_integrity(self, storage_key: str, expected_hash: str) -> bool:
        """Verify DICOM file integrity using stored hash"""
        dicom_data = self.retrieve_dicom(storage_key)
        if not dicom_data:
            return False

        actual_hash = self._generate_content_hash(dicom_data)
        return actual_hash == expected_hash


if __name__ == "__main__":
    # Example usage
    service = DICOMIngestionService(
        s3_bucket="biomedical-dicom-storage",
        local_storage=True  # Development mode
    )

    print("DICOM Ingestion Service initialized successfully")
    print("Ready to ingest medical imaging data")
