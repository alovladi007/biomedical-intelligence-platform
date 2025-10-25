"""
Epic FHIR Integration
Connects to Epic EHR systems using FHIR R4 API (SMART on FHIR)
"""

import requests
from typing import Dict, List, Optional
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EpicFHIRConnector:
    """Epic EHR integration via FHIR R4 API"""

    def __init__(self, base_url: str, client_id: str, client_secret: str):
        """
        Initialize Epic FHIR connector

        Args:
            base_url: Epic FHIR base URL (e.g., https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4)
            client_id: OAuth 2.0 client ID
            client_secret: OAuth 2.0 client secret
        """
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def authenticate(self) -> bool:
        """Authenticate with Epic using OAuth 2.0"""
        try:
            # Epic OAuth 2.0 token endpoint
            token_url = f"{self.base_url}/oauth2/token"

            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }

            response = requests.post(token_url, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data['access_token']
            logger.info("Successfully authenticated with Epic FHIR")
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False

    def get_patient(self, patient_id: str) -> Optional[Dict]:
        """Fetch patient demographics"""
        endpoint = f"{self.base_url}/Patient/{patient_id}"
        return self._make_request(endpoint)

    def get_observations(self, patient_id: str, category: str = None) -> List[Dict]:
        """
        Fetch patient observations (labs, vitals)

        Args:
            patient_id: Patient FHIR ID
            category: vital-signs, laboratory, etc.
        """
        endpoint = f"{self.base_url}/Observation"
        params = {'patient': patient_id}
        if category:
            params['category'] = category

        return self._make_request(endpoint, params=params).get('entry', [])

    def get_imaging_studies(self, patient_id: str) -> List[Dict]:
        """Fetch imaging studies (DICOM metadata)"""
        endpoint = f"{self.base_url}/ImagingStudy"
        params = {'patient': patient_id}
        return self._make_request(endpoint, params=params).get('entry', [])

    def send_diagnostic_report(
        self,
        patient_id: str,
        report_data: Dict
    ) -> Dict:
        """
        Send AI diagnostic report back to Epic

        Args:
            patient_id: Patient FHIR ID
            report_data: Diagnostic report content
        """
        endpoint = f"{self.base_url}/DiagnosticReport"

        # FHIR DiagnosticReport resource
        fhir_report = {
            'resourceType': 'DiagnosticReport',
            'status': 'final',
            'code': {
                'coding': [{
                    'system': 'http://loinc.org',
                    'code': '11528-7',
                    'display': 'AI Diagnostic Report'
                }]
            },
            'subject': {
                'reference': f'Patient/{patient_id}'
            },
            'effectiveDateTime': datetime.utcnow().isoformat(),
            'issued': datetime.utcnow().isoformat(),
            'conclusion': report_data.get('conclusion', ''),
            'result': report_data.get('results', [])
        }

        return self._make_request(endpoint, method='POST', data=fhir_report)

    def _make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        params: Dict = None,
        data: Dict = None
    ) -> Dict:
        """Make authenticated FHIR API request"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        }

        try:
            if method == 'GET':
                response = requests.get(endpoint, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(endpoint, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"FHIR API error: {e}")
            return {}


if __name__ == "__main__":
    # Demo usage (requires real Epic credentials)
    print("Epic FHIR Connector - Demo Mode")
    print("In production, provide real Epic FHIR endpoint and credentials")
