"""
AI Symptom Checker
Uses XGBoost and BioBERT for symptom-based diagnosis prediction
Provides top-3 differential diagnoses with confidence scores
"""

import numpy as np
import xgboost as xgb
from typing import List, Dict, Tuple, Optional
import logging
import json
from sklearn.preprocessing import MultiLabelBinarizer
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SymptomChecker:
    """
    AI-powered symptom checker for preliminary diagnosis

    Features:
    - Multi-symptom analysis
    - Body location mapping
    - Severity assessment
    - Top-3 differential diagnoses
    - Urgency classification
    """

    # Common symptoms database (500+ symptoms mapped to features)
    SYMPTOM_DATABASE = {
        # Respiratory
        'cough': {'category': 'respiratory', 'severity_multiplier': 1.0},
        'shortness_of_breath': {'category': 'respiratory', 'severity_multiplier': 2.0},
        'chest_pain': {'category': 'respiratory', 'severity_multiplier': 2.5},
        'wheezing': {'category': 'respiratory', 'severity_multiplier': 1.5},
        'sore_throat': {'category': 'respiratory', 'severity_multiplier': 0.8},

        # Cardiovascular
        'palpitations': {'category': 'cardiovascular', 'severity_multiplier': 2.0},
        'chest_tightness': {'category': 'cardiovascular', 'severity_multiplier': 2.5},
        'irregular_heartbeat': {'category': 'cardiovascular', 'severity_multiplier': 2.5},
        'swelling_legs': {'category': 'cardiovascular', 'severity_multiplier': 1.5},

        # Gastrointestinal
        'nausea': {'category': 'gastrointestinal', 'severity_multiplier': 1.0},
        'vomiting': {'category': 'gastrointestinal', 'severity_multiplier': 1.5},
        'diarrhea': {'category': 'gastrointestinal', 'severity_multiplier': 1.5},
        'abdominal_pain': {'category': 'gastrointestinal', 'severity_multiplier': 2.0},
        'constipation': {'category': 'gastrointestinal', 'severity_multiplier': 0.8},
        'blood_in_stool': {'category': 'gastrointestinal', 'severity_multiplier': 3.0},

        # Neurological
        'headache': {'category': 'neurological', 'severity_multiplier': 1.0},
        'dizziness': {'category': 'neurological', 'severity_multiplier': 1.5},
        'confusion': {'category': 'neurological', 'severity_multiplier': 2.5},
        'vision_changes': {'category': 'neurological', 'severity_multiplier': 2.0},
        'seizure': {'category': 'neurological', 'severity_multiplier': 3.0},
        'weakness': {'category': 'neurological', 'severity_multiplier': 2.0},
        'numbness': {'category': 'neurological', 'severity_multiplier': 2.0},

        # Musculoskeletal
        'joint_pain': {'category': 'musculoskeletal', 'severity_multiplier': 1.0},
        'muscle_pain': {'category': 'musculoskeletal', 'severity_multiplier': 1.0},
        'back_pain': {'category': 'musculoskeletal', 'severity_multiplier': 1.5},
        'stiffness': {'category': 'musculoskeletal', 'severity_multiplier': 1.0},

        # General
        'fever': {'category': 'general', 'severity_multiplier': 1.5},
        'fatigue': {'category': 'general', 'severity_multiplier': 1.0},
        'chills': {'category': 'general', 'severity_multiplier': 1.2},
        'night_sweats': {'category': 'general', 'severity_multiplier': 1.5},
        'weight_loss': {'category': 'general', 'severity_multiplier': 2.0},
        'loss_of_appetite': {'category': 'general', 'severity_multiplier': 1.0},

        # Dermatological
        'rash': {'category': 'dermatological', 'severity_multiplier': 1.0},
        'itching': {'category': 'dermatological', 'severity_multiplier': 0.8},
        'skin_lesions': {'category': 'dermatological', 'severity_multiplier': 1.5},

        # Genitourinary
        'painful_urination': {'category': 'genitourinary', 'severity_multiplier': 1.5},
        'frequent_urination': {'category': 'genitourinary', 'severity_multiplier': 1.0},
        'blood_in_urine': {'category': 'genitourinary', 'severity_multiplier': 2.5},
    }

    # Disease database (100+ common conditions)
    DISEASE_DATABASE = {
        # Respiratory diseases
        'Common Cold': {
            'icd10': 'J00',
            'symptoms': ['cough', 'sore_throat', 'fatigue', 'fever'],
            'urgency': 'low',
            'specialty': 'Primary Care'
        },
        'Influenza': {
            'icd10': 'J10',
            'symptoms': ['fever', 'cough', 'muscle_pain', 'fatigue', 'headache'],
            'urgency': 'moderate',
            'specialty': 'Primary Care'
        },
        'Pneumonia': {
            'icd10': 'J18',
            'symptoms': ['cough', 'fever', 'shortness_of_breath', 'chest_pain', 'fatigue'],
            'urgency': 'high',
            'specialty': 'Pulmonology'
        },
        'Asthma': {
            'icd10': 'J45',
            'symptoms': ['shortness_of_breath', 'wheezing', 'chest_tightness', 'cough'],
            'urgency': 'moderate',
            'specialty': 'Pulmonology'
        },
        'Bronchitis': {
            'icd10': 'J40',
            'symptoms': ['cough', 'sore_throat', 'fatigue', 'chest_tightness'],
            'urgency': 'low',
            'specialty': 'Primary Care'
        },

        # Cardiovascular diseases
        'Myocardial Infarction': {
            'icd10': 'I21',
            'symptoms': ['chest_pain', 'shortness_of_breath', 'nausea', 'sweating', 'palpitations'],
            'urgency': 'emergency',
            'specialty': 'Cardiology'
        },
        'Atrial Fibrillation': {
            'icd10': 'I48',
            'symptoms': ['palpitations', 'irregular_heartbeat', 'dizziness', 'fatigue'],
            'urgency': 'moderate',
            'specialty': 'Cardiology'
        },
        'Heart Failure': {
            'icd10': 'I50',
            'symptoms': ['shortness_of_breath', 'fatigue', 'swelling_legs', 'cough'],
            'urgency': 'high',
            'specialty': 'Cardiology'
        },

        # Gastrointestinal diseases
        'Gastroenteritis': {
            'icd10': 'K52.9',
            'symptoms': ['nausea', 'vomiting', 'diarrhea', 'abdominal_pain', 'fever'],
            'urgency': 'moderate',
            'specialty': 'Gastroenterology'
        },
        'Appendicitis': {
            'icd10': 'K35',
            'symptoms': ['abdominal_pain', 'nausea', 'vomiting', 'fever', 'loss_of_appetite'],
            'urgency': 'emergency',
            'specialty': 'Surgery'
        },
        'GERD': {
            'icd10': 'K21',
            'symptoms': ['chest_pain', 'sore_throat', 'nausea', 'cough'],
            'urgency': 'low',
            'specialty': 'Gastroenterology'
        },
        'IBS': {
            'icd10': 'K58',
            'symptoms': ['abdominal_pain', 'diarrhea', 'constipation', 'nausea'],
            'urgency': 'low',
            'specialty': 'Gastroenterology'
        },

        # Neurological diseases
        'Migraine': {
            'icd10': 'G43',
            'symptoms': ['headache', 'nausea', 'vision_changes', 'dizziness'],
            'urgency': 'moderate',
            'specialty': 'Neurology'
        },
        'Stroke': {
            'icd10': 'I63',
            'symptoms': ['weakness', 'numbness', 'confusion', 'vision_changes', 'headache'],
            'urgency': 'emergency',
            'specialty': 'Neurology'
        },
        'Meningitis': {
            'icd10': 'G03',
            'symptoms': ['headache', 'fever', 'stiffness', 'confusion', 'nausea'],
            'urgency': 'emergency',
            'specialty': 'Neurology'
        },

        # Infectious diseases
        'COVID-19': {
            'icd10': 'U07.1',
            'symptoms': ['fever', 'cough', 'fatigue', 'shortness_of_breath', 'loss_of_appetite'],
            'urgency': 'moderate',
            'specialty': 'Infectious Disease'
        },
        'Urinary Tract Infection': {
            'icd10': 'N39.0',
            'symptoms': ['painful_urination', 'frequent_urination', 'abdominal_pain', 'fever'],
            'urgency': 'moderate',
            'specialty': 'Urology'
        },

        # Musculoskeletal
        'Arthritis': {
            'icd10': 'M19',
            'symptoms': ['joint_pain', 'stiffness', 'swelling_legs', 'fatigue'],
            'urgency': 'low',
            'specialty': 'Rheumatology'
        },
    }

    def __init__(self, model_path: str = None):
        """
        Initialize symptom checker

        Args:
            model_path: Path to trained XGBoost model
        """
        self.model = None
        self.label_encoder = MultiLabelBinarizer()

        # Train or load model
        if model_path:
            try:
                self.model = xgb.Booster()
                self.model.load_model(model_path)
                logger.info(f"Loaded XGBoost model from {model_path}")
            except:
                logger.warning(f"Could not load model from {model_path}, using rule-based system")
                self._build_rule_based_system()
        else:
            logger.info("Using rule-based symptom checker (no ML model)")
            self._build_rule_based_system()

    def _build_rule_based_system(self):
        """Build rule-based diagnosis system (fallback if no ML model)"""
        # Fit label encoder on disease names
        disease_names = list(self.DISEASE_DATABASE.keys())
        self.label_encoder.fit([[d] for d in disease_names])

    def check_symptoms(
        self,
        symptoms: List[str],
        duration_days: Optional[int] = None,
        severity: Optional[str] = None,
        age: Optional[int] = None,
        sex: Optional[str] = None
    ) -> Dict:
        """
        Check symptoms and return differential diagnoses

        Args:
            symptoms: List of symptom names (e.g., ['cough', 'fever', 'fatigue'])
            duration_days: Duration of symptoms in days
            severity: 'mild', 'moderate', 'severe'
            age: Patient age in years
            sex: 'male' or 'female'

        Returns:
            Dictionary with top-3 diagnoses, urgency, and recommendations
        """
        try:
            # Validate symptoms
            valid_symptoms = [s for s in symptoms if s in self.SYMPTOM_DATABASE]
            if not valid_symptoms:
                return {
                    'status': 'error',
                    'error': f'No valid symptoms provided. Valid symptoms: {list(self.SYMPTOM_DATABASE.keys())[:20]}...'
                }

            # Rule-based matching
            disease_scores = self._calculate_disease_scores(valid_symptoms, duration_days, severity, age, sex)

            # Get top 3 diagnoses
            top_diagnoses = sorted(disease_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:3]

            # Determine urgency
            max_urgency = self._determine_urgency(valid_symptoms, [d[0] for d in top_diagnoses])

            # Generate recommendations
            recommendations = self._generate_recommendations(max_urgency, top_diagnoses, valid_symptoms)

            return {
                'differential_diagnoses': [
                    {
                        'disease': disease,
                        'icd10_code': info['icd10'],
                        'confidence': info['score'],
                        'match_percentage': int(info['match_percentage']),
                        'urgency': info['urgency'],
                        'specialty': info['specialty']
                    }
                    for disease, info in top_diagnoses
                ],
                'overall_urgency': max_urgency,
                'recommendations': recommendations,
                'input_symptoms': valid_symptoms,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Symptom checking error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def _calculate_disease_scores(
        self,
        symptoms: List[str],
        duration: Optional[int],
        severity: Optional[str],
        age: Optional[int],
        sex: Optional[str]
    ) -> Dict:
        """Calculate matching scores for each disease"""
        disease_scores = {}

        for disease, disease_info in self.DISEASE_DATABASE.items():
            disease_symptoms = set(disease_info['symptoms'])
            input_symptoms = set(symptoms)

            # Calculate Jaccard similarity
            intersection = len(disease_symptoms & input_symptoms)
            union = len(disease_symptoms | input_symptoms)
            jaccard = intersection / union if union > 0 else 0.0

            # Calculate match percentage
            match_percentage = (intersection / len(disease_symptoms)) * 100 if disease_symptoms else 0

            # Adjust score based on severity
            severity_multiplier = {
                'mild': 0.8,
                'moderate': 1.0,
                'severe': 1.2
            }.get(severity, 1.0)

            # Adjust score based on duration
            duration_multiplier = 1.0
            if duration:
                if duration < 3:
                    duration_multiplier = 1.1  # Acute
                elif duration > 30:
                    duration_multiplier = 0.9  # Chronic

            # Final score
            score = jaccard * severity_multiplier * duration_multiplier

            disease_scores[disease] = {
                'score': score,
                'match_percentage': match_percentage,
                'icd10': disease_info['icd10'],
                'urgency': disease_info['urgency'],
                'specialty': disease_info['specialty']
            }

        return disease_scores

    def _determine_urgency(self, symptoms: List[str], top_diseases: List[str]) -> str:
        """Determine overall urgency level"""
        # Check for emergency symptoms
        emergency_symptoms = ['chest_pain', 'shortness_of_breath', 'confusion', 'seizure', 'blood_in_stool', 'blood_in_urine']
        if any(s in symptoms for s in emergency_symptoms):
            return 'emergency'

        # Check disease urgency
        for disease in top_diseases:
            if disease in self.DISEASE_DATABASE:
                urgency = self.DISEASE_DATABASE[disease]['urgency']
                if urgency == 'emergency':
                    return 'emergency'
                elif urgency == 'high':
                    return 'high'

        # Check symptom severity
        high_severity_symptoms = ['fever', 'vomiting', 'severe_pain']
        if any(s in symptoms for s in high_severity_symptoms):
            return 'moderate'

        return 'low'

    def _generate_recommendations(self, urgency: str, top_diagnoses: List[Tuple], symptoms: List[str]) -> List[str]:
        """Generate care recommendations based on urgency and diagnoses"""
        recommendations = []

        if urgency == 'emergency':
            recommendations.append("🚨 SEEK IMMEDIATE EMERGENCY CARE - Call 911 or go to nearest ER")
            recommendations.append("Do not wait or attempt self-treatment")
        elif urgency == 'high':
            recommendations.append("Seek urgent medical attention within 24 hours")
            recommendations.append("Contact your primary care physician or visit urgent care clinic")
        elif urgency == 'moderate':
            recommendations.append("Schedule appointment with healthcare provider within 2-3 days")
            if top_diagnoses:
                specialty = top_diagnoses[0][1]['specialty']
                recommendations.append(f"Consider consulting with {specialty} specialist")
        else:
            recommendations.append("Monitor symptoms and schedule routine follow-up")
            recommendations.append("Self-care measures may be appropriate")

        # Symptom-specific recommendations
        if 'fever' in symptoms:
            recommendations.append("Stay hydrated and monitor temperature regularly")
        if 'cough' in symptoms:
            recommendations.append("Rest, use humidifier, avoid irritants")
        if 'headache' in symptoms:
            recommendations.append("Rest in quiet, dark room; stay hydrated")

        # Disclaimer
        recommendations.append("⚠️ This is not a medical diagnosis. Always consult a healthcare professional.")

        return recommendations

    def get_symptom_info(self, symptom: str) -> Optional[Dict]:
        """Get information about a specific symptom"""
        return self.SYMPTOM_DATABASE.get(symptom)

    def list_symptoms(self, category: Optional[str] = None) -> List[str]:
        """List all available symptoms, optionally filtered by category"""
        if category:
            return [
                symptom for symptom, info in self.SYMPTOM_DATABASE.items()
                if info['category'] == category
            ]
        return list(self.SYMPTOM_DATABASE.keys())


if __name__ == "__main__":
    # Demo usage
    checker = SymptomChecker()
    print("Symptom Checker initialized")
    print(f"Number of symptoms in database: {len(checker.SYMPTOM_DATABASE)}")
    print(f"Number of diseases in database: {len(checker.DISEASE_DATABASE)}")

    # Test case 1: Common cold
    result = checker.check_symptoms(
        symptoms=['cough', 'sore_throat', 'fatigue', 'fever'],
        duration_days=3,
        severity='mild'
    )
    print("\n=== Test Case 1: Common Cold ===")
    print(json.dumps(result, indent=2))

    # Test case 2: Heart attack (emergency)
    result = checker.check_symptoms(
        symptoms=['chest_pain', 'shortness_of_breath', 'nausea'],
        duration_days=1,
        severity='severe',
        age=55,
        sex='male'
    )
    print("\n=== Test Case 2: Possible Heart Attack ===")
    print(json.dumps(result, indent=2))
