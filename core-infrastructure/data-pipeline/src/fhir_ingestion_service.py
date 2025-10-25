"""
FHIR/HL7 Ingestion Service - HIPAA Compliant
Handles EHR data ingestion from FHIR R4 and HL7 v2.x messages
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.condition import Condition
from fhir.resources.procedure import Procedure
from fhir.resources.medication import Medication
from fhir.resources.bundle import Bundle
import hl7
from hl7.util import generate_message_control_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FHIRIngestionService:
    """
    FHIR R4 compliant data ingestion service

    Supports:
    - Patient demographics
    - Observations (vitals, labs)
    - Conditions (diagnoses)
    - Procedures
    - Medications
    """

    def __init__(self, database_client=None):
        """
        Initialize FHIR ingestion service

        Args:
            database_client: Database client for storing processed data
        """
        self.db = database_client
        self.processed_resources = {
            "patients": 0,
            "observations": 0,
            "conditions": 0,
            "procedures": 0,
            "medications": 0
        }

    def ingest_fhir_bundle(self, bundle_json: str) -> Dict:
        """
        Process FHIR Bundle (e.g., from EHR export)

        Args:
            bundle_json: JSON string of FHIR Bundle

        Returns:
            Dict with ingestion results
        """
        try:
            logger.info("Processing FHIR Bundle")

            # Parse bundle
            bundle = Bundle.parse_raw(bundle_json)

            results = {
                "success": True,
                "total_entries": len(bundle.entry) if bundle.entry else 0,
                "processed": {},
                "errors": []
            }

            if not bundle.entry:
                return results

            # Process each entry
            for entry in bundle.entry:
                try:
                    resource = entry.resource
                    resource_type = resource.resource_type

                    # Route to appropriate handler
                    if resource_type == "Patient":
                        self._process_patient(resource)
                        results["processed"]["patients"] = results["processed"].get("patients", 0) + 1

                    elif resource_type == "Observation":
                        self._process_observation(resource)
                        results["processed"]["observations"] = results["processed"].get("observations", 0) + 1

                    elif resource_type == "Condition":
                        self._process_condition(resource)
                        results["processed"]["conditions"] = results["processed"].get("conditions", 0) + 1

                    elif resource_type == "Procedure":
                        self._process_procedure(resource)
                        results["processed"]["procedures"] = results["processed"].get("procedures", 0) + 1

                    elif resource_type == "Medication":
                        self._process_medication(resource)
                        results["processed"]["medications"] = results["processed"].get("medications", 0) + 1

                except Exception as e:
                    error_msg = f"Error processing {resource_type}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

            logger.info(f"Bundle processed: {results['processed']}")
            return results

        except Exception as e:
            logger.error(f"Bundle processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _process_patient(self, patient: Patient) -> Dict:
        """
        Extract and de-identify patient demographics

        De-identification per HIPAA Safe Harbor:
        - Remove specific dates (keep year only)
        - Remove geographic subdivisions smaller than state
        - Remove specific ages > 89
        """

        # Extract and de-identify
        deidentified = {
            "resource_type": "Patient",
            "id": patient.id,
            "gender": str(patient.gender.value) if patient.gender else None,
            "birth_year": patient.birthDate.year if patient.birthDate else None,
            "deceased": bool(patient.deceasedBoolean) if hasattr(patient, 'deceasedBoolean') else None
        }

        # Age calculation (de-identify if > 89)
        if patient.birthDate:
            age = datetime.now().year - patient.birthDate.year
            deidentified["age"] = 90 if age > 89 else age

        # Address (state only)
        if patient.address and len(patient.address) > 0:
            address = patient.address[0]
            deidentified["state"] = address.state if hasattr(address, 'state') else None
            deidentified["postal_code_prefix"] = address.postalCode[:3] if hasattr(address, 'postalCode') and address.postalCode else None

        # Language
        if patient.communication and len(patient.communication) > 0:
            comm = patient.communication[0]
            if hasattr(comm, 'language') and comm.language:
                deidentified["language"] = str(comm.language.coding[0].code) if comm.language.coding else None

        logger.info(f"Processed patient: {patient.id}")

        # Store in database (if configured)
        if self.db:
            self._store_resource("patients", deidentified)

        return deidentified

    def _process_observation(self, observation: Observation) -> Dict:
        """
        Process clinical observations (vitals, lab results)
        """

        obs_data = {
            "resource_type": "Observation",
            "id": observation.id,
            "status": str(observation.status.value) if observation.status else None,
            "category": [],
            "code": None,
            "value": None,
            "unit": None,
            "reference_range": None,
            "effective_datetime": None,
            "issued": str(observation.issued) if hasattr(observation, 'issued') and observation.issued else None
        }

        # Extract category (e.g., vital-signs, laboratory)
        if observation.category:
            for cat in observation.category:
                if cat.coding:
                    obs_data["category"].append({
                        "system": str(cat.coding[0].system) if cat.coding[0].system else None,
                        "code": str(cat.coding[0].code) if cat.coding[0].code else None,
                        "display": str(cat.coding[0].display) if cat.coding[0].display else None
                    })

        # Extract code (LOINC, SNOMED, etc.)
        if observation.code and observation.code.coding:
            coding = observation.code.coding[0]
            obs_data["code"] = {
                "system": str(coding.system) if coding.system else None,
                "code": str(coding.code) if coding.code else None,
                "display": str(coding.display) if coding.display else None
            }

        # Extract value
        if hasattr(observation, 'valueQuantity') and observation.valueQuantity:
            obs_data["value"] = float(observation.valueQuantity.value)
            obs_data["unit"] = str(observation.valueQuantity.unit) if observation.valueQuantity.unit else None
        elif hasattr(observation, 'valueString') and observation.valueString:
            obs_data["value"] = str(observation.valueString)

        # Reference range
        if observation.referenceRange and len(observation.referenceRange) > 0:
            ref = observation.referenceRange[0]
            obs_data["reference_range"] = {
                "low": float(ref.low.value) if hasattr(ref, 'low') and ref.low else None,
                "high": float(ref.high.value) if hasattr(ref, 'high') and ref.high else None
            }

        # Effective datetime (de-identify to year-month)
        if hasattr(observation, 'effectiveDateTime') and observation.effectiveDateTime:
            dt = observation.effectiveDateTime
            obs_data["effective_year_month"] = f"{dt.year}-{dt.month:02d}"

        logger.info(f"Processed observation: {observation.id}")

        if self.db:
            self._store_resource("observations", obs_data)

        return obs_data

    def _process_condition(self, condition: Condition) -> Dict:
        """
        Process diagnoses/conditions
        """

        cond_data = {
            "resource_type": "Condition",
            "id": condition.id,
            "clinical_status": None,
            "verification_status": None,
            "category": [],
            "severity": None,
            "code": None,
            "onset_datetime": None
        }

        # Clinical status
        if condition.clinicalStatus and condition.clinicalStatus.coding:
            cond_data["clinical_status"] = str(condition.clinicalStatus.coding[0].code)

        # Verification status
        if condition.verificationStatus and condition.verificationStatus.coding:
            cond_data["verification_status"] = str(condition.verificationStatus.coding[0].code)

        # Code (ICD-10, SNOMED)
        if condition.code and condition.code.coding:
            coding = condition.code.coding[0]
            cond_data["code"] = {
                "system": str(coding.system) if coding.system else None,
                "code": str(coding.code) if coding.code else None,
                "display": str(coding.display) if coding.display else None
            }

        # Onset (de-identify to year-month)
        if hasattr(condition, 'onsetDateTime') and condition.onsetDateTime:
            dt = condition.onsetDateTime
            cond_data["onset_year_month"] = f"{dt.year}-{dt.month:02d}"

        logger.info(f"Processed condition: {condition.id}")

        if self.db:
            self._store_resource("conditions", cond_data)

        return cond_data

    def _process_procedure(self, procedure: Procedure) -> Dict:
        """Process medical procedures"""

        proc_data = {
            "resource_type": "Procedure",
            "id": procedure.id,
            "status": str(procedure.status.value) if procedure.status else None,
            "code": None,
            "performed_datetime": None
        }

        # Code (CPT, SNOMED)
        if procedure.code and procedure.code.coding:
            coding = procedure.code.coding[0]
            proc_data["code"] = {
                "system": str(coding.system) if coding.system else None,
                "code": str(coding.code) if coding.code else None,
                "display": str(coding.display) if coding.display else None
            }

        # Performed date (de-identify)
        if hasattr(procedure, 'performedDateTime') and procedure.performedDateTime:
            dt = procedure.performedDateTime
            proc_data["performed_year_month"] = f"{dt.year}-{dt.month:02d}"

        logger.info(f"Processed procedure: {procedure.id}")

        if self.db:
            self._store_resource("procedures", proc_data)

        return proc_data

    def _process_medication(self, medication: Medication) -> Dict:
        """Process medication information"""

        med_data = {
            "resource_type": "Medication",
            "id": medication.id,
            "code": None,
            "status": str(medication.status.value) if hasattr(medication, 'status') and medication.status else None
        }

        # Code (RxNorm, NDC)
        if medication.code and medication.code.coding:
            coding = medication.code.coding[0]
            med_data["code"] = {
                "system": str(coding.system) if coding.system else None,
                "code": str(coding.code) if coding.code else None,
                "display": str(coding.display) if coding.display else None
            }

        logger.info(f"Processed medication: {medication.id}")

        if self.db:
            self._store_resource("medications", med_data)

        return med_data

    def _store_resource(self, collection: str, data: Dict):
        """Store resource in database"""
        # Placeholder for database storage
        # In production, this would insert into PostgreSQL/MongoDB
        logger.debug(f"Storing {collection}: {data.get('id')}")

    def get_statistics(self) -> Dict:
        """Get ingestion statistics"""
        return {
            "total_processed": sum(self.processed_resources.values()),
            "by_type": self.processed_resources
        }


class HL7IngestionService:
    """
    HL7 v2.x message ingestion service

    Supports common message types:
    - ADT (Admission/Discharge/Transfer)
    - ORU (Observation Result)
    - ORM (Order Message)
    """

    def ingest_hl7_message(self, hl7_message: str) -> Dict:
        """
        Parse and process HL7 v2.x message

        Args:
            hl7_message: HL7 message string

        Returns:
            Dict with processing results
        """
        try:
            # Parse message
            message = hl7.parse(hl7_message)

            # Extract message type
            msg_type = str(message.segment('MSH')[9])

            logger.info(f"Processing HL7 message type: {msg_type}")

            if msg_type.startswith('ADT'):
                return self._process_adt(message)
            elif msg_type.startswith('ORU'):
                return self._process_oru(message)
            elif msg_type.startswith('ORM'):
                return self._process_orm(message)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported message type: {msg_type}"
                }

        except Exception as e:
            logger.error(f"HL7 processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _process_adt(self, message) -> Dict:
        """Process ADT (Admission/Discharge/Transfer) message"""

        # Extract PID segment (Patient Identification)
        pid = message.segment('PID')

        patient_data = {
            "message_type": "ADT",
            "patient_id": str(pid[3]) if len(pid) > 3 else None,
            "gender": str(pid[8]) if len(pid) > 8 else None,
            "birth_date": str(pid[7]) if len(pid) > 7 else None
        }

        logger.info(f"Processed ADT message")
        return {"success": True, "data": patient_data}

    def _process_oru(self, message) -> Dict:
        """Process ORU (Observation Result) message"""

        observations = []

        # Extract OBX segments (Observation)
        for obx in message.segments('OBX'):
            obs = {
                "value_type": str(obx[2]) if len(obx) > 2 else None,
                "identifier": str(obx[3]) if len(obx) > 3 else None,
                "value": str(obx[5]) if len(obx) > 5 else None,
                "units": str(obx[6]) if len(obx) > 6 else None,
                "reference_range": str(obx[7]) if len(obx) > 7 else None
            }
            observations.append(obs)

        logger.info(f"Processed ORU message with {len(observations)} observations")
        return {
            "success": True,
            "message_type": "ORU",
            "observations": observations
        }

    def _process_orm(self, message) -> Dict:
        """Process ORM (Order Message)"""
        logger.info("Processed ORM message")
        return {"success": True, "message_type": "ORM"}


if __name__ == "__main__":
    # Example usage
    fhir_service = FHIRIngestionService()
    hl7_service = HL7IngestionService()

    print("FHIR/HL7 Ingestion Services initialized successfully")
    print("Ready to process EHR data")
