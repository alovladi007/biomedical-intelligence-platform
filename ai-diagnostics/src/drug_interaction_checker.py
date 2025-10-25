"""
Drug Interaction Checker
Checks for drug-drug interactions, contraindications, and dosage warnings
Uses FDA drug interaction database and clinical decision support rules
"""

import logging
from typing import List, Dict, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DrugInteractionChecker:
    """
    Drug interaction checking service

    Severity levels:
    - Critical: Life-threatening interaction
    - Major: Serious interaction requiring intervention
    - Moderate: May require monitoring
    - Minor: Usually clinically insignificant
    """

    # Drug interaction database (subset - would be expanded with full FDA database)
    DRUG_INTERACTIONS = {
        ('warfarin', 'aspirin'): {
            'severity': 'major',
            'effect': 'Increased bleeding risk',
            'mechanism': 'Both drugs inhibit platelet function and coagulation',
            'recommendation': 'Use with caution. Monitor INR closely. Consider alternative antiplatelet if possible.',
            'management': 'Reduce warfarin dose, frequent INR monitoring, patient education on bleeding signs'
        },
        ('warfarin', 'ibuprofen'): {
            'severity': 'major',
            'effect': 'Increased bleeding risk',
            'mechanism': 'NSAIDs interfere with platelet function',
            'recommendation': 'Avoid combination. Use acetaminophen for pain instead.',
            'management': 'Discontinue NSAID, monitor for bleeding'
        },
        ('lisinopril', 'spironolactone'): {
            'severity': 'major',
            'effect': 'Hyperkalemia risk',
            'mechanism': 'Both drugs increase serum potassium',
            'recommendation': 'Monitor serum potassium closely. Consider alternative diuretic.',
            'management': 'Check potassium weekly initially, adjust doses'
        },
        ('metformin', 'contrast_dye'): {
            'severity': 'major',
            'effect': 'Lactic acidosis risk',
            'mechanism': 'Contrast can cause renal failure, metformin accumulation',
            'recommendation': 'Hold metformin 48 hours before and after contrast procedure',
            'management': 'Withhold metformin, ensure adequate hydration, check renal function'
        },
        ('simvastatin', 'clarithromycin'): {
            'severity': 'critical',
            'effect': 'Rhabdomyolysis risk',
            'mechanism': 'CYP3A4 inhibition increases statin levels',
            'recommendation': 'CONTRAINDICATED. Use alternative antibiotic.',
            'management': 'Discontinue simvastatin during clarithromycin therapy'
        },
        ('fluoxetine', 'tramadol'): {
            'severity': 'major',
            'effect': 'Serotonin syndrome risk',
            'mechanism': 'Both drugs increase serotonin levels',
            'recommendation': 'Use with caution. Monitor for serotonin syndrome symptoms.',
            'management': 'Patient education, dose reduction if symptoms occur'
        },
        ('methotrexate', 'trimethoprim'): {
            'severity': 'major',
            'effect': 'Bone marrow suppression',
            'mechanism': 'Additive folate antagonism',
            'recommendation': 'Avoid combination. Use alternative antibiotic.',
            'management': 'Monitor CBC, consider leucovorin rescue'
        },
        ('digoxin', 'furosemide'): {
            'severity': 'moderate',
            'effect': 'Digoxin toxicity risk',
            'mechanism': 'Furosemide-induced hypokalemia increases digoxin toxicity',
            'recommendation': 'Monitor potassium and digoxin levels',
            'management': 'Potassium supplementation, regular digoxin level monitoring'
        },
        ('levothyroxine', 'calcium'): {
            'severity': 'moderate',
            'effect': 'Decreased levothyroxine absorption',
            'mechanism': 'Calcium binds levothyroxine in GI tract',
            'recommendation': 'Separate administration by 4 hours',
            'management': 'Take levothyroxine on empty stomach, calcium with meals'
        },
        ('clopidogrel', 'omeprazole'): {
            'severity': 'moderate',
            'effect': 'Reduced clopidogrel efficacy',
            'mechanism': 'CYP2C19 inhibition reduces clopidogrel activation',
            'recommendation': 'Consider alternative PPI (pantoprazole) or H2 blocker',
            'management': 'Switch to pantoprazole or separate administration'
        },
    }

    # Drug-food interactions
    FOOD_INTERACTIONS = {
        'warfarin': {
            'food': 'Vitamin K-rich foods (leafy greens, broccoli)',
            'effect': 'Decreased anticoagulation effect',
            'recommendation': 'Maintain consistent vitamin K intake'
        },
        'levothyroxine': {
            'food': 'Soy products, high-fiber foods',
            'effect': 'Decreased absorption',
            'recommendation': 'Take on empty stomach, 30-60 min before breakfast'
        },
        'tetracycline': {
            'food': 'Dairy products, calcium supplements',
            'effect': 'Decreased antibiotic absorption',
            'recommendation': 'Avoid dairy 2 hours before and after dose'
        },
        'sildenafil': {
            'food': 'Grapefruit juice',
            'effect': 'Increased drug levels, increased side effects',
            'recommendation': 'Avoid grapefruit juice'
        },
    }

    # Contraindications (drug-condition interactions)
    CONTRAINDICATIONS = {
        'metformin': {
            'conditions': ['severe_renal_impairment', 'hepatic_impairment'],
            'reason': 'Lactic acidosis risk',
            'recommendation': 'Contraindicated. Consider alternative antidiabetic.'
        },
        'nsaids': {
            'conditions': ['peptic_ulcer', 'severe_heart_failure', 'severe_renal_impairment'],
            'reason': 'GI bleeding, fluid retention, renal toxicity',
            'recommendation': 'Avoid if possible. Use acetaminophen alternative.'
        },
        'beta_blockers': {
            'conditions': ['asthma', 'severe_bradycardia', 'heart_block'],
            'reason': 'Bronchoconstriction, further heart rate reduction',
            'recommendation': 'Contraindicated. Use calcium channel blocker alternative.'
        },
    }

    def __init__(self):
        """Initialize drug interaction checker"""
        logger.info("Drug Interaction Checker initialized")

    def check_interactions(self, medications: List[str]) -> Dict:
        """
        Check for drug-drug interactions in medication list

        Args:
            medications: List of medication names (generic names preferred)

        Returns:
            Dictionary with interactions by severity level
        """
        try:
            # Normalize medication names
            medications = [med.lower().strip() for med in medications]

            # Find interactions
            critical_interactions = []
            major_interactions = []
            moderate_interactions = []
            minor_interactions = []

            # Check all drug pairs
            for i in range(len(medications)):
                for j in range(i + 1, len(medications)):
                    drug1, drug2 = medications[i], medications[j]

                    # Check both orderings
                    interaction = self.DRUG_INTERACTIONS.get((drug1, drug2)) or \
                                self.DRUG_INTERACTIONS.get((drug2, drug1))

                    if interaction:
                        interaction_detail = {
                            'drug1': drug1,
                            'drug2': drug2,
                            'severity': interaction['severity'],
                            'effect': interaction['effect'],
                            'mechanism': interaction['mechanism'],
                            'recommendation': interaction['recommendation'],
                            'management': interaction['management']
                        }

                        if interaction['severity'] == 'critical':
                            critical_interactions.append(interaction_detail)
                        elif interaction['severity'] == 'major':
                            major_interactions.append(interaction_detail)
                        elif interaction['severity'] == 'moderate':
                            moderate_interactions.append(interaction_detail)
                        else:
                            minor_interactions.append(interaction_detail)

            # Overall risk assessment
            if critical_interactions:
                overall_risk = 'critical'
                alert_message = '🚨 CRITICAL DRUG INTERACTIONS DETECTED - Immediate pharmacist/physician review required'
            elif major_interactions:
                overall_risk = 'major'
                alert_message = '⚠️ Major drug interactions detected - Physician review recommended'
            elif moderate_interactions:
                overall_risk = 'moderate'
                alert_message = 'Moderate interactions present - Monitoring recommended'
            else:
                overall_risk = 'low'
                alert_message = 'No significant interactions detected'

            return {
                'overall_risk': overall_risk,
                'alert_message': alert_message,
                'interactions': {
                    'critical': critical_interactions,
                    'major': major_interactions,
                    'moderate': moderate_interactions,
                    'minor': minor_interactions
                },
                'total_interactions': len(critical_interactions) + len(major_interactions) +
                                    len(moderate_interactions) + len(minor_interactions),
                'medications_checked': medications,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Drug interaction check error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def check_food_interactions(self, medication: str) -> Dict:
        """Check for drug-food interactions"""
        medication = medication.lower().strip()

        if medication in self.FOOD_INTERACTIONS:
            interaction = self.FOOD_INTERACTIONS[medication]
            return {
                'has_interaction': True,
                'medication': medication,
                'food': interaction['food'],
                'effect': interaction['effect'],
                'recommendation': interaction['recommendation'],
                'status': 'success'
            }
        else:
            return {
                'has_interaction': False,
                'medication': medication,
                'message': 'No significant food interactions found',
                'status': 'success'
            }

    def check_contraindications(self, medication: str, conditions: List[str]) -> Dict:
        """Check for drug-condition contraindications"""
        medication = medication.lower().strip()
        conditions = [c.lower().strip() for c in conditions]

        contraindications = []

        if medication in self.CONTRAINDICATIONS:
            drug_contraindications = self.CONTRAINDICATIONS[medication]
            contraindicated_conditions = drug_contraindications['conditions']

            for condition in conditions:
                if condition in contraindicated_conditions:
                    contraindications.append({
                        'condition': condition,
                        'reason': drug_contraindications['reason'],
                        'recommendation': drug_contraindications['recommendation']
                    })

        if contraindications:
            return {
                'has_contraindications': True,
                'medication': medication,
                'contraindications': contraindications,
                'alert_message': '⚠️ CONTRAINDICATION DETECTED - Do not prescribe',
                'status': 'success'
            }
        else:
            return {
                'has_contraindications': False,
                'medication': medication,
                'message': 'No contraindications found for given conditions',
                'status': 'success'
            }

    def get_drug_info(self, medication: str) -> Dict:
        """Get comprehensive drug information"""
        medication = medication.lower().strip()

        # Check all interactions involving this drug
        interactions = []
        for (drug1, drug2), interaction in self.DRUG_INTERACTIONS.items():
            if drug1 == medication or drug2 == medication:
                other_drug = drug2 if drug1 == medication else drug1
                interactions.append({
                    'interacting_drug': other_drug,
                    'severity': interaction['severity'],
                    'effect': interaction['effect']
                })

        # Food interactions
        food_interaction = self.FOOD_INTERACTIONS.get(medication)

        # Contraindications
        contraindications = self.CONTRAINDICATIONS.get(medication)

        return {
            'medication': medication,
            'known_interactions': len(interactions),
            'interactions': interactions[:10],  # Limit to top 10
            'food_interaction': food_interaction,
            'contraindications': contraindications,
            'status': 'success'
        }


if __name__ == "__main__":
    # Demo usage
    checker = DrugInteractionChecker()
    print("Drug Interaction Checker initialized")

    # Test case 1: Critical interaction
    result = checker.check_interactions(['simvastatin', 'clarithromycin'])
    print("\n=== Test Case 1: Critical Interaction ===")
    print(json.dumps(result, indent=2))

    # Test case 2: Multiple interactions
    result = checker.check_interactions(['warfarin', 'aspirin', 'ibuprofen'])
    print("\n=== Test Case 2: Multiple Interactions ===")
    print(json.dumps(result, indent=2))

    # Test case 3: Food interaction
    result = checker.check_food_interactions('levothyroxine')
    print("\n=== Test Case 3: Food Interaction ===")
    print(json.dumps(result, indent=2))
