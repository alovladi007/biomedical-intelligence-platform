"""
Data Validation Service - Quality Assurance for Biomedical Data
Validates ingested data for completeness, accuracy, and outlier detection
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import statistics
import re

# Data validation
from pydantic import BaseModel, Field, validator, ValidationError
from pydantic import constr, conint, confloat

# Numerical analysis
import numpy as np
from scipy import stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== PYDANTIC SCHEMAS ====================

class PatientSchema(BaseModel):
    """Patient demographics validation"""
    patient_id: str = Field(..., min_length=1, max_length=64)
    pseudonym: str = Field(..., min_length=1, max_length=64)
    gender: Optional[constr(regex=r'^(M|F|O|U)$')] = None  # Male, Female, Other, Unknown
    birth_year: Optional[conint(ge=1900, le=2025)] = None
    age: Optional[conint(ge=0, le=120)] = None
    state: Optional[constr(min_length=2, max_length=2)] = None  # US state code
    postal_code_prefix: Optional[constr(min_length=3, max_length=3)] = None
    deceased: bool = False

    @validator('age', 'birth_year')
    def check_age_consistency(cls, v, values):
        """Ensure age and birth_year are consistent"""
        if 'birth_year' in values and values['birth_year'] and v:
            current_year = datetime.now().year
            calculated_age = current_year - values['birth_year']
            if abs(calculated_age - v) > 1:  # Allow 1 year tolerance
                raise ValueError(f"Age {v} inconsistent with birth_year {values['birth_year']}")
        return v

    class Config:
        extra = 'allow'  # Allow additional fields


class ObservationSchema(BaseModel):
    """Clinical observation validation (vitals, labs)"""
    observation_id: str = Field(..., min_length=1)
    patient_pseudonym: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    code_system: str = Field(..., min_length=1)
    display_name: Optional[str] = None
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    unit: Optional[str] = None
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    effective_date: Optional[str] = None
    status: constr(regex=r'^(final|preliminary|amended|corrected)$')

    @validator('value_numeric')
    def validate_numeric_value(cls, v, values):
        """Check if numeric value is within reasonable range"""
        if v is not None and values.get('code'):
            code = values['code']

            # Example ranges for common observations (LOINC codes)
            ranges = {
                '8867-4': (0, 250),      # Heart rate (bpm)
                '8480-6': (50, 250),     # Systolic BP (mmHg)
                '8462-4': (30, 150),     # Diastolic BP (mmHg)
                '8310-5': (95, 106),     # Body temperature (F)
                '9279-1': (8, 30),       # Respiratory rate
                '2339-0': (0, 1000),     # Glucose (mg/dL)
            }

            if code in ranges:
                min_val, max_val = ranges[code]
                if not (min_val <= v <= max_val):
                    logger.warning(f"Value {v} out of expected range [{min_val}, {max_val}] for code {code}")

        return v

    class Config:
        extra = 'allow'


class GenomicVariantSchema(BaseModel):
    """Genomic variant validation"""
    patient_pseudonym: str = Field(..., min_length=1)
    chromosome: constr(regex=r'^(chr)?(1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|X|Y|MT?)$')
    position: conint(ge=1)
    ref_allele: constr(regex=r'^[ACGT]+$')
    alt_allele: constr(regex=r'^[ACGT]+$')
    genotype: Optional[constr(regex=r'^([0-9]\/[0-9]|[0-9]\|[0-9])$')] = None  # 0/0, 0/1, 1/1, etc.
    gene: Optional[str] = None
    quality: Optional[confloat(ge=0)] = None
    allele_frequency: Optional[confloat(ge=0, le=1)] = None

    @validator('alt_allele')
    def validate_variant(cls, v, values):
        """Ensure ref and alt alleles are different"""
        if 'ref_allele' in values and v == values['ref_allele']:
            raise ValueError("Alt allele must differ from ref allele")
        return v

    class Config:
        extra = 'allow'


class DICOMMetadataSchema(BaseModel):
    """DICOM metadata validation"""
    study_id: str = Field(..., min_length=1)
    patient_pseudonym: str = Field(..., min_length=1)
    storage_key: str = Field(..., min_length=1)
    content_hash: constr(min_length=64, max_length=64)  # SHA-256
    modality: constr(regex=r'^(CT|MR|XR|US|NM|PT|DX|MG|CR|DR)$')
    body_part: Optional[str] = None
    study_date: Optional[str] = None
    image_count: conint(ge=1) = 1
    file_size_bytes: conint(ge=0) = 0

    class Config:
        extra = 'allow'


# ==================== DATA VALIDATOR ====================

class DataValidator:
    """
    Data validation service for quality assurance

    Features:
    - Schema validation (Pydantic)
    - Completeness checks
    - Outlier detection (statistical)
    - Data quality metrics
    - Cross-field validation
    """

    def __init__(self):
        self.validation_stats = {
            'total_validated': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }

    # ==================== SCHEMA VALIDATION ====================

    def validate_patient(self, patient_data: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Validate patient data against schema

        Returns:
            (is_valid, error_message, validated_data)
        """
        try:
            validated = PatientSchema(**patient_data)
            self.validation_stats['passed'] += 1
            self.validation_stats['total_validated'] += 1

            return True, None, validated.dict()

        except ValidationError as e:
            self.validation_stats['failed'] += 1
            self.validation_stats['total_validated'] += 1

            error_msg = str(e)
            logger.error(f"Patient validation failed: {error_msg}")
            return False, error_msg, None

    def validate_observation(self, obs_data: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Validate clinical observation"""
        try:
            validated = ObservationSchema(**obs_data)
            self.validation_stats['passed'] += 1
            self.validation_stats['total_validated'] += 1

            return True, None, validated.dict()

        except ValidationError as e:
            self.validation_stats['failed'] += 1
            self.validation_stats['total_validated'] += 1

            error_msg = str(e)
            logger.error(f"Observation validation failed: {error_msg}")
            return False, error_msg, None

    def validate_variant(self, variant_data: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Validate genomic variant"""
        try:
            validated = GenomicVariantSchema(**variant_data)
            self.validation_stats['passed'] += 1
            self.validation_stats['total_validated'] += 1

            return True, None, validated.dict()

        except ValidationError as e:
            self.validation_stats['failed'] += 1
            self.validation_stats['total_validated'] += 1

            error_msg = str(e)
            logger.error(f"Variant validation failed: {error_msg}")
            return False, error_msg, None

    def validate_dicom_metadata(self, dicom_data: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Validate DICOM metadata"""
        try:
            validated = DICOMMetadataSchema(**dicom_data)
            self.validation_stats['passed'] += 1
            self.validation_stats['total_validated'] += 1

            return True, None, validated.dict()

        except ValidationError as e:
            self.validation_stats['failed'] += 1
            self.validation_stats['total_validated'] += 1

            error_msg = str(e)
            logger.error(f"DICOM validation failed: {error_msg}")
            return False, error_msg, None

    # ==================== COMPLETENESS CHECKS ====================

    def check_completeness(self, data: Dict, required_fields: List[str]) -> Dict:
        """
        Check data completeness

        Args:
            data: Data dictionary
            required_fields: List of required field names

        Returns:
            Dict with completeness report
        """
        missing_fields = []
        empty_fields = []
        present_fields = []

        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif data[field] is None or data[field] == '':
                empty_fields.append(field)
            else:
                present_fields.append(field)

        completeness_ratio = len(present_fields) / len(required_fields)

        report = {
            'complete': len(missing_fields) == 0 and len(empty_fields) == 0,
            'completeness_ratio': completeness_ratio,
            'missing_fields': missing_fields,
            'empty_fields': empty_fields,
            'present_fields': present_fields
        }

        if not report['complete']:
            logger.warning(f"Completeness check: {completeness_ratio*100:.1f}% complete")
            if missing_fields:
                logger.warning(f"Missing fields: {missing_fields}")
            if empty_fields:
                logger.warning(f"Empty fields: {empty_fields}")

            self.validation_stats['warnings'] += 1

        return report

    # ==================== OUTLIER DETECTION ====================

    def detect_outliers_zscore(
        self,
        values: List[float],
        threshold: float = 3.0
    ) -> Dict:
        """
        Detect outliers using Z-score method

        Args:
            values: List of numeric values
            threshold: Z-score threshold (default: 3.0)

        Returns:
            Dict with outlier analysis
        """
        if not values or len(values) < 3:
            return {
                'outliers': [],
                'method': 'z-score',
                'threshold': threshold,
                'error': 'Insufficient data'
            }

        values_array = np.array(values)
        mean = np.mean(values_array)
        std = np.std(values_array)

        if std == 0:
            return {
                'outliers': [],
                'method': 'z-score',
                'threshold': threshold,
                'mean': mean,
                'std': std,
                'note': 'No variation in data'
            }

        # Calculate Z-scores
        z_scores = np.abs((values_array - mean) / std)
        outlier_indices = np.where(z_scores > threshold)[0].tolist()

        outliers = []
        for idx in outlier_indices:
            outliers.append({
                'index': idx,
                'value': values[idx],
                'z_score': float(z_scores[idx])
            })

        if outliers:
            logger.warning(f"Detected {len(outliers)} outliers using Z-score method")
            self.validation_stats['warnings'] += len(outliers)

        return {
            'outliers': outliers,
            'method': 'z-score',
            'threshold': threshold,
            'mean': float(mean),
            'std': float(std),
            'outlier_count': len(outliers),
            'outlier_ratio': len(outliers) / len(values)
        }

    def detect_outliers_iqr(self, values: List[float]) -> Dict:
        """
        Detect outliers using Interquartile Range (IQR) method

        Args:
            values: List of numeric values

        Returns:
            Dict with outlier analysis
        """
        if not values or len(values) < 4:
            return {
                'outliers': [],
                'method': 'iqr',
                'error': 'Insufficient data'
            }

        values_array = np.array(values)
        q1 = np.percentile(values_array, 25)
        q3 = np.percentile(values_array, 75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Find outliers
        outlier_mask = (values_array < lower_bound) | (values_array > upper_bound)
        outlier_indices = np.where(outlier_mask)[0].tolist()

        outliers = []
        for idx in outlier_indices:
            outliers.append({
                'index': idx,
                'value': values[idx],
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound)
            })

        if outliers:
            logger.warning(f"Detected {len(outliers)} outliers using IQR method")
            self.validation_stats['warnings'] += len(outliers)

        return {
            'outliers': outliers,
            'method': 'iqr',
            'q1': float(q1),
            'q3': float(q3),
            'iqr': float(iqr),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'outlier_count': len(outliers),
            'outlier_ratio': len(outliers) / len(values)
        }

    # ==================== QUALITY METRICS ====================

    def calculate_quality_metrics(self, dataset: List[Dict], data_type: str) -> Dict:
        """
        Calculate data quality metrics for a dataset

        Args:
            dataset: List of data records
            data_type: Type of data (patient, observation, variant, etc.)

        Returns:
            Dict with quality metrics
        """
        if not dataset:
            return {
                'error': 'Empty dataset',
                'record_count': 0
            }

        record_count = len(dataset)

        # Completeness metrics
        field_completeness = {}
        if record_count > 0:
            sample_record = dataset[0]
            for field in sample_record.keys():
                non_null_count = sum(1 for record in dataset if record.get(field) is not None and record.get(field) != '')
                field_completeness[field] = non_null_count / record_count

        # Overall completeness
        avg_completeness = statistics.mean(field_completeness.values()) if field_completeness else 0

        # Duplicate detection
        if data_type in ['patient', 'observation', 'variant']:
            id_field = {
                'patient': 'patient_id',
                'observation': 'observation_id',
                'variant': 'variant_id'
            }.get(data_type)

            if id_field:
                ids = [record.get(id_field) for record in dataset if record.get(id_field)]
                duplicate_count = len(ids) - len(set(ids))
            else:
                duplicate_count = 0
        else:
            duplicate_count = 0

        metrics = {
            'data_type': data_type,
            'record_count': record_count,
            'avg_completeness': avg_completeness,
            'field_completeness': field_completeness,
            'duplicate_count': duplicate_count,
            'duplicate_ratio': duplicate_count / record_count if record_count > 0 else 0,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"Quality metrics for {data_type}: {avg_completeness*100:.1f}% complete, {duplicate_count} duplicates")

        return metrics

    def validate_date_range(
        self,
        date_str: str,
        min_year: int = 1900,
        max_year: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate date string is within reasonable range

        Args:
            date_str: Date string (YYYY-MM-DD or YYYY-MM)
            min_year: Minimum allowed year
            max_year: Maximum allowed year (defaults to current year)

        Returns:
            (is_valid, error_message)
        """
        if max_year is None:
            max_year = datetime.now().year

        # Parse date
        date_pattern = r'^(\d{4})-(\d{2})-(\d{2})$|^(\d{4})-(\d{2})$|^(\d{4})$'
        match = re.match(date_pattern, date_str)

        if not match:
            return False, f"Invalid date format: {date_str}"

        # Extract year
        year_str = date_str[:4]
        year = int(year_str)

        if year < min_year or year > max_year:
            return False, f"Year {year} out of range [{min_year}, {max_year}]"

        return True, None

    # ==================== STATISTICS ====================

    def get_validation_statistics(self) -> Dict:
        """Get validation statistics"""
        total = self.validation_stats['total_validated']

        return {
            'total_validated': total,
            'passed': self.validation_stats['passed'],
            'failed': self.validation_stats['failed'],
            'warnings': self.validation_stats['warnings'],
            'pass_rate': self.validation_stats['passed'] / total if total > 0 else 0,
            'fail_rate': self.validation_stats['failed'] / total if total > 0 else 0
        }

    def reset_statistics(self):
        """Reset validation statistics"""
        self.validation_stats = {
            'total_validated': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
        logger.info("Validation statistics reset")


if __name__ == "__main__":
    # Example usage
    validator = DataValidator()

    # Test patient validation
    patient_data = {
        'patient_id': 'original_123',
        'pseudonym': 'PATIENT_12345',
        'gender': 'F',
        'birth_year': 1985,
        'age': 40,
        'state': 'CA',
        'postal_code_prefix': '940'
    }

    is_valid, error, validated = validator.validate_patient(patient_data)
    print(f"Patient validation: {'PASS' if is_valid else 'FAIL'}")
    if error:
        print(f"Error: {error}")

    # Test completeness
    required_fields = ['patient_id', 'pseudonym', 'gender', 'birth_year', 'age']
    completeness = validator.check_completeness(patient_data, required_fields)
    print(f"Completeness: {completeness['completeness_ratio']*100:.1f}%")

    # Test outlier detection
    heart_rates = [72, 68, 75, 180, 70, 73, 71, 69, 220, 74]  # 180 and 220 are outliers
    outliers = validator.detect_outliers_zscore(heart_rates, threshold=2.0)
    print(f"Outliers detected: {outliers['outlier_count']}")

    # Get statistics
    stats = validator.get_validation_statistics()
    print(f"\nValidation Statistics:")
    print(f"Total validated: {stats['total_validated']}")
    print(f"Pass rate: {stats['pass_rate']*100:.1f}%")

    print("\nData Validator initialized successfully")
    print("Ready to validate biomedical data")
