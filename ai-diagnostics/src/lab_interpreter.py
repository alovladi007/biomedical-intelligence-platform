"""
Lab Result Interpreter
Interprets laboratory test results and provides clinical insights
Covers common labs: CBC, CMP, Lipid Panel, Thyroid, HbA1c, etc.
"""

import logging
from typing import Dict, List, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LabInterpreter:
    """
    Laboratory result interpretation service

    Features:
    - Normal range checking
    - Abnormality flagging (High, Low, Critical)
    - Clinical significance interpretation
    - Follow-up recommendations
    """

    # Reference ranges (adult, non-pregnant)
    REFERENCE_RANGES = {
        # Complete Blood Count (CBC)
        'wbc': {'min': 4.5, 'max': 11.0, 'unit': '10^9/L', 'name': 'White Blood Cell Count'},
        'rbc_male': {'min': 4.5, 'max': 5.9, 'unit': '10^12/L', 'name': 'Red Blood Cell Count (Male)'},
        'rbc_female': {'min': 4.1, 'max': 5.1, 'unit': '10^12/L', 'name': 'Red Blood Cell Count (Female)'},
        'hemoglobin_male': {'min': 13.5, 'max': 17.5, 'unit': 'g/dL', 'name': 'Hemoglobin (Male)'},
        'hemoglobin_female': {'min': 12.0, 'max': 15.5, 'unit': 'g/dL', 'name': 'Hemoglobin (Female)'},
        'hematocrit_male': {'min': 38.8, 'max': 50.0, 'unit': '%', 'name': 'Hematocrit (Male)'},
        'hematocrit_female': {'min': 34.9, 'max': 44.5, 'unit': '%', 'name': 'Hematocrit (Female)'},
        'platelets': {'min': 150, 'max': 400, 'unit': '10^9/L', 'name': 'Platelet Count'},

        # Comprehensive Metabolic Panel (CMP)
        'glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL', 'name': 'Glucose (Fasting)'},
        'bun': {'min': 7, 'max': 20, 'unit': 'mg/dL', 'name': 'Blood Urea Nitrogen'},
        'creatinine_male': {'min': 0.7, 'max': 1.3, 'unit': 'mg/dL', 'name': 'Creatinine (Male)'},
        'creatinine_female': {'min': 0.6, 'max': 1.1, 'unit': 'mg/dL', 'name': 'Creatinine (Female)'},
        'sodium': {'min': 136, 'max': 145, 'unit': 'mmol/L', 'name': 'Sodium'},
        'potassium': {'min': 3.5, 'max': 5.0, 'unit': 'mmol/L', 'name': 'Potassium'},
        'chloride': {'min': 98, 'max': 107, 'unit': 'mmol/L', 'name': 'Chloride'},
        'calcium': {'min': 8.5, 'max': 10.5, 'unit': 'mg/dL', 'name': 'Calcium'},
        'albumin': {'min': 3.5, 'max': 5.5, 'unit': 'g/dL', 'name': 'Albumin'},
        'total_protein': {'min': 6.0, 'max': 8.3, 'unit': 'g/dL', 'name': 'Total Protein'},
        'alt': {'min': 7, 'max': 56, 'unit': 'U/L', 'name': 'Alanine Aminotransferase (ALT)'},
        'ast': {'min': 10, 'max': 40, 'unit': 'U/L', 'name': 'Aspartate Aminotransferase (AST)'},
        'bilirubin_total': {'min': 0.1, 'max': 1.2, 'unit': 'mg/dL', 'name': 'Total Bilirubin'},
        'alkaline_phosphatase': {'min': 44, 'max': 147, 'unit': 'U/L', 'name': 'Alkaline Phosphatase'},

        # Lipid Panel
        'cholesterol_total': {'min': 0, 'max': 200, 'unit': 'mg/dL', 'name': 'Total Cholesterol'},
        'ldl': {'min': 0, 'max': 100, 'unit': 'mg/dL', 'name': 'LDL Cholesterol'},
        'hdl_male': {'min': 40, 'max': 999, 'unit': 'mg/dL', 'name': 'HDL Cholesterol (Male)'},
        'hdl_female': {'min': 50, 'max': 999, 'unit': 'mg/dL', 'name': 'HDL Cholesterol (Female)'},
        'triglycerides': {'min': 0, 'max': 150, 'unit': 'mg/dL', 'name': 'Triglycerides'},

        # Diabetes
        'hba1c': {'min': 4.0, 'max': 5.6, 'unit': '%', 'name': 'Hemoglobin A1c'},

        # Thyroid
        'tsh': {'min': 0.4, 'max': 4.0, 'unit': 'mIU/L', 'name': 'Thyroid Stimulating Hormone'},
        't4_free': {'min': 0.8, 'max': 1.8, 'unit': 'ng/dL', 'name': 'Free T4'},
        't3_free': {'min': 2.3, 'max': 4.2, 'unit': 'pg/mL', 'name': 'Free T3'},

        # Inflammation
        'crp': {'min': 0, 'max': 3.0, 'unit': 'mg/L', 'name': 'C-Reactive Protein'},
        'esr': {'min': 0, 'max': 20, 'unit': 'mm/hr', 'name': 'Erythrocyte Sedimentation Rate'},
    }

    # Clinical interpretations
    INTERPRETATIONS = {
        'wbc': {
            'high': 'Leukocytosis - possible infection, inflammation, or hematologic disorder',
            'critical_high': 'Severe leukocytosis - immediate evaluation for leukemia or severe infection',
            'low': 'Leukopenia - possible bone marrow suppression, autoimmune disease, or medication effect',
            'critical_low': 'Severe leukopenia - high infection risk, requires urgent evaluation'
        },
        'hemoglobin_male': {
            'high': 'Polycythemia - possible dehydration, COPD, or polycythemia vera',
            'low': 'Anemia - iron deficiency, chronic disease, or blood loss',
            'critical_low': 'Severe anemia - may require transfusion'
        },
        'platelets': {
            'high': 'Thrombocytosis - possible inflammation, iron deficiency, or myeloproliferative disorder',
            'low': 'Thrombocytopenia - bleeding risk, possible ITP, medication effect, or bone marrow disorder',
            'critical_low': 'Severe thrombocytopenia - high bleeding risk, urgent hematology consult'
        },
        'glucose': {
            'high': 'Hyperglycemia - possible diabetes or prediabetes, check HbA1c',
            'critical_high': 'Severe hyperglycemia - diabetic emergency risk',
            'low': 'Hypoglycemia - medication effect or insulinoma',
            'critical_low': 'Severe hypoglycemia - immediate treatment required'
        },
        'potassium': {
            'high': 'Hyperkalemia - cardiac arrhythmia risk, check medications and renal function',
            'critical_high': 'Severe hyperkalemia - LIFE THREATENING, immediate treatment required',
            'low': 'Hypokalemia - arrhythmia risk, check diuretic use',
            'critical_low': 'Severe hypokalemia - cardiac arrhythmia risk, urgent replacement'
        },
        'creatinine_male': {
            'high': 'Elevated creatinine - possible acute or chronic kidney disease',
            'critical_high': 'Severe renal impairment - may require dialysis'
        },
        'hba1c': {
            'high': 'Elevated HbA1c - diabetes (≥6.5%) or prediabetes (5.7-6.4%)',
            'critical_high': 'Poorly controlled diabetes - urgent diabetes management'
        },
        'tsh': {
            'high': 'Elevated TSH - hypothyroidism, check Free T4',
            'low': 'Suppressed TSH - hyperthyroidism, check Free T4 and T3'
        },
        'cholesterol_total': {
            'high': 'Hypercholesterolemia - cardiovascular risk, lifestyle and statin therapy'
        },
        'ldl': {
            'high': 'Elevated LDL - cardiovascular risk, consider statin therapy'
        },
    }

    def __init__(self):
        """Initialize lab interpreter"""
        logger.info("Lab Interpreter initialized")

    def interpret_result(
        self,
        test_name: str,
        value: float,
        sex: Optional[str] = None,
        age: Optional[int] = None
    ) -> Dict:
        """
        Interpret a single lab result

        Args:
            test_name: Lab test name (e.g., 'glucose', 'wbc')
            value: Test result value
            sex: 'male' or 'female' (for sex-specific ranges)
            age: Patient age (for age-specific ranges)

        Returns:
            Interpretation with status, clinical significance, and recommendations
        """
        try:
            # Adjust test name for sex-specific ranges
            if sex in ['male', 'female']:
                sex_specific_test = f"{test_name}_{sex}"
                if sex_specific_test in self.REFERENCE_RANGES:
                    test_name = sex_specific_test

            # Get reference range
            if test_name not in self.REFERENCE_RANGES:
                return {
                    'status': 'error',
                    'error': f'Unknown test: {test_name}. Available tests: {list(self.REFERENCE_RANGES.keys())[:20]}...'
                }

            ref_range = self.REFERENCE_RANGES[test_name]
            min_val, max_val = ref_range['min'], ref_range['max']

            # Determine status
            if value < min_val:
                if value < min_val * 0.5:  # Critical low
                    status = 'critical_low'
                    flag = '🚨 CRITICAL LOW'
                else:
                    status = 'low'
                    flag = '⚠️ LOW'
            elif value > max_val:
                if value > max_val * 2.0:  # Critical high
                    status = 'critical_high'
                    flag = '🚨 CRITICAL HIGH'
                else:
                    status = 'high'
                    flag = '⚠️ HIGH'
            else:
                status = 'normal'
                flag = '✓ NORMAL'

            # Get interpretation
            interpretation = self._get_interpretation(test_name, status)

            # Generate recommendations
            recommendations = self._get_recommendations(test_name, status, value)

            return {
                'test_name': ref_range['name'],
                'value': value,
                'unit': ref_range['unit'],
                'reference_range': {
                    'min': min_val,
                    'max': max_val
                },
                'status': status,
                'flag': flag,
                'interpretation': interpretation,
                'recommendations': recommendations,
                'is_critical': status in ['critical_low', 'critical_high']
            }

        except Exception as e:
            logger.error(f"Lab interpretation error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def interpret_panel(
        self,
        results: Dict[str, float],
        sex: Optional[str] = None,
        age: Optional[int] = None
    ) -> Dict:
        """
        Interpret a complete lab panel (CBC, CMP, Lipid, etc.)

        Args:
            results: Dictionary of test_name: value pairs
            sex: 'male' or 'female'
            age: Patient age

        Returns:
            Complete panel interpretation with summary and alerts
        """
        try:
            interpretations = {}
            abnormal_results = []
            critical_results = []

            # Interpret each result
            for test_name, value in results.items():
                interpretation = self.interpret_result(test_name, value, sex, age)

                if interpretation.get('status') != 'error':
                    interpretations[test_name] = interpretation

                    if interpretation['status'] != 'normal':
                        abnormal_results.append({
                            'test': test_name,
                            'value': value,
                            'status': interpretation['status']
                        })

                    if interpretation.get('is_critical'):
                        critical_results.append({
                            'test': test_name,
                            'value': value,
                            'interpretation': interpretation['interpretation']
                        })

            # Generate summary
            summary = self._generate_panel_summary(interpretations, abnormal_results, critical_results)

            return {
                'interpretations': interpretations,
                'summary': summary,
                'abnormal_count': len(abnormal_results),
                'critical_count': len(critical_results),
                'abnormal_results': abnormal_results,
                'critical_results': critical_results,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Panel interpretation error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def _get_interpretation(self, test_name: str, status: str) -> str:
        """Get clinical interpretation for test result"""
        # Remove sex suffix for interpretation lookup
        base_test = test_name.replace('_male', '').replace('_female', '')

        if base_test in self.INTERPRETATIONS:
            interp_dict = self.INTERPRETATIONS[base_test]
            return interp_dict.get(status, 'No specific interpretation available')

        return 'Result outside normal range'

    def _get_recommendations(self, test_name: str, status: str, value: float) -> List[str]:
        """Generate follow-up recommendations"""
        recommendations = []

        if status in ['critical_low', 'critical_high']:
            recommendations.append('🚨 URGENT: Notify physician immediately')
            recommendations.append('Repeat test to confirm result')

        if 'glucose' in test_name and status in ['high', 'critical_high']:
            recommendations.append('Check HbA1c if not recently done')
            recommendations.append('Evaluate for diabetes or prediabetes')

        if 'potassium' in test_name and status != 'normal':
            recommendations.append('Review medications (ACE inhibitors, ARBs, diuretics)')
            recommendations.append('Check renal function')

        if 'creatinine' in test_name and status in ['high', 'critical_high']:
            recommendations.append('Calculate eGFR')
            recommendations.append('Evaluate for acute vs chronic kidney disease')

        if 'hemoglobin' in test_name and status == 'low':
            recommendations.append('Check iron studies, B12, and folate')
            recommendations.append('Evaluate for occult blood loss')

        if 'tsh' in test_name and status != 'normal':
            recommendations.append('Check Free T4 and Free T3')

        if 'ldl' in test_name and value > 160:
            recommendations.append('Consider statin therapy')
            recommendations.append('Lifestyle modifications: diet and exercise')

        if not recommendations:
            recommendations.append('Clinical correlation recommended')

        return recommendations

    def _generate_panel_summary(
        self,
        interpretations: Dict,
        abnormal_results: List,
        critical_results: List
    ) -> str:
        """Generate summary of panel results"""
        if critical_results:
            return f"🚨 CRITICAL ABNORMALITIES DETECTED ({len(critical_results)}) - Immediate physician notification required. " \
                   f"{len(abnormal_results)} total abnormal results."
        elif abnormal_results:
            return f"⚠️ {len(abnormal_results)} abnormal result(s) detected. Clinical correlation and follow-up recommended."
        else:
            return "✓ All results within normal limits."

    def list_available_tests(self) -> List[str]:
        """List all available lab tests"""
        return list(self.REFERENCE_RANGES.keys())


if __name__ == "__main__":
    # Demo usage
    interpreter = LabInterpreter()
    print(f"Lab Interpreter initialized with {len(interpreter.REFERENCE_RANGES)} tests")

    # Test case 1: Single abnormal result
    result = interpreter.interpret_result('glucose', 250, sex='male')
    print("\n=== Test Case 1: High Glucose ===")
    print(json.dumps(result, indent=2))

    # Test case 2: Complete panel
    panel_results = {
        'glucose': 95,
        'potassium': 5.8,  # High
        'creatinine': 2.5,  # High (male)
        'hemoglobin': 9.0,  # Low (male)
        'platelets': 50  # Critical low
    }
    result = interpreter.interpret_panel(panel_results, sex='male', age=65)
    print("\n=== Test Case 2: Complete Panel ===")
    print(json.dumps(result, indent=2))
