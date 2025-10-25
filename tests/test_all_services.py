"""
Comprehensive Test Suite for Biomedical Intelligence Platform
Tests all Phase 2 and Phase 4 services
"""

import requests
import pytest
import json
from typing import Dict

# Service endpoints
SERVICES = {
    'medical_imaging': 'http://localhost:5001',
    'ai_diagnostics': 'http://localhost:5002',
    'genomic_intelligence': 'http://localhost:5007',
    'obicare': 'http://localhost:5010',
    'hipaa_monitor': 'http://localhost:5011'
}


class TestServiceHealth:
    """Test health endpoints for all services"""

    @pytest.mark.parametrize("service_name,base_url", SERVICES.items())
    def test_health_endpoint(self, service_name, base_url):
        """Test that all services have working health endpoints"""
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        print(f"✓ {service_name}: Health check passed")


class TestMedicalImagingAI:
    """Test Medical Imaging AI service"""

    BASE_URL = SERVICES['medical_imaging']

    def test_models_info(self):
        """Test model information endpoint"""
        response = requests.get(f"{self.BASE_URL}/models/info")
        assert response.status_code == 200
        data = response.json()
        assert 'chest_xray_classifier' in data
        assert 'ct_segmenter' in data
        print("✓ Medical Imaging: Models info retrieved")


class TestAIDiagnostics:
    """Test AI Diagnostics service"""

    BASE_URL = SERVICES['ai_diagnostics']

    def test_symptom_check(self):
        """Test symptom checker"""
        payload = {
            "symptoms": ["cough", "fever", "fatigue"],
            "duration_days": 3,
            "severity": "moderate"
        }
        response = requests.post(f"{self.BASE_URL}/symptom-check", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'differential_diagnoses' in data
        assert len(data['differential_diagnoses']) > 0
        print(f"✓ AI Diagnostics: Symptom check - {len(data['differential_diagnoses'])} diagnoses found")

    def test_drug_interactions(self):
        """Test drug interaction checker"""
        payload = {"medications": ["warfarin", "aspirin"]}
        response = requests.post(f"{self.BASE_URL}/drug-interactions", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'overall_risk' in data
        assert 'interactions' in data
        print(f"✓ AI Diagnostics: Drug interactions - Risk level: {data['overall_risk']}")

    def test_lab_interpretation(self):
        """Test lab result interpreter"""
        payload = {
            "test_name": "glucose",
            "value": 150,
            "sex": "male"
        }
        response = requests.post(f"{self.BASE_URL}/lab-interpret/single", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'interpretation' in data
        print(f"✓ AI Diagnostics: Lab interpretation - Status: {data['status']}")


class TestGenomicIntelligence:
    """Test Genomic Intelligence service"""

    BASE_URL = SERVICES['genomic_intelligence']

    def test_variant_annotation(self):
        """Test variant annotation"""
        payload = {
            "chromosome": "chr7",
            "position": 117199563,
            "ref": "G",
            "alt": "A",
            "gene": "CYP2D6"
        }
        response = requests.post(f"{self.BASE_URL}/annotate/variant", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'variant_id' in data
        assert 'interpretation' in data
        print(f"✓ Genomic Intelligence: Variant annotated - {data['variant_id']}")

    def test_pharmacogenomics(self):
        """Test pharmacogenomics prediction"""
        payload = {
            "gene": "CYP2D6",
            "phenotype": "poor_metabolizer",
            "drug": "codeine"
        }
        response = requests.post(f"{self.BASE_URL}/pharmacogenomics/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'recommendation' in data
        assert data['actionable'] == True
        print(f"✓ Genomic Intelligence: PGx prediction - {data['gene']} + {data['drug']}")


class TestOBiCare:
    """Test OBiCare maternal health service"""

    BASE_URL = SERVICES['obicare']

    def test_preeclampsia_risk(self):
        """Test pre-eclampsia risk prediction"""
        payload = {
            "systolic_bp": 145,
            "diastolic_bp": 95,
            "proteinuria": 200,
            "gestational_age": 28,
            "maternal_age": 35,
            "bmi": 28.5,
            "previous_preeclampsia": False
        }
        response = requests.post(f"{self.BASE_URL}/predict/preeclampsia-risk", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'risk_probability' in data
        assert 'risk_category' in data
        assert 'recommendation' in data
        print(f"✓ OBiCare: Pre-eclampsia risk - Category: {data['risk_category']}")

    def test_maternal_vitals(self):
        """Test maternal vitals monitoring"""
        payload = {
            "heart_rate": 95,
            "blood_pressure_systolic": 130,
            "blood_pressure_diastolic": 85,
            "temperature": 37.2,
            "glucose": 95
        }
        response = requests.post(f"{self.BASE_URL}/monitor/vitals", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'alerts' in data
        print(f"✓ OBiCare: Vitals monitored - Status: {data['status']}, Alerts: {len(data['alerts'])}")


class TestHIPAAMonitor:
    """Test HIPAA Compliance Monitor"""

    BASE_URL = SERVICES['hipaa_monitor']

    def test_compliance_check(self):
        """Test HIPAA compliance checking"""
        payload = {
            "check_type": "technical",
            "details": {
                "unique_user_ids": True,
                "emergency_access": True,
                "audit_logging": True,
                "integrity_checks": True,
                "encryption_in_transit": True
            }
        }
        response = requests.post(f"{self.BASE_URL}/compliance/check", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'compliance_score' in data
        assert 'status' in data
        print(f"✓ HIPAA Monitor: Compliance check - Score: {data['compliance_score']}%")

    def test_audit_report(self):
        """Test audit report generation"""
        response = requests.get(f"{self.BASE_URL}/audit/report")
        assert response.status_code == 200
        data = response.json()
        assert 'summary' in data
        assert 'overall_compliance' in data
        print(f"✓ HIPAA Monitor: Audit report - Compliance: {data['overall_compliance']}")


def run_tests():
    """Run all tests and generate report"""
    print("\n" + "="*60)
    print("Biomedical Intelligence Platform - Test Suite")
    print("="*60 + "\n")

    # Run tests using pytest
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--color=yes'
    ])


if __name__ == "__main__":
    run_tests()
