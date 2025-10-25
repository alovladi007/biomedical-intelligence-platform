"""
Pharmacogenomics Predictor
Predicts drug response based on genetic variants
Implements CPIC (Clinical Pharmacogenetics Implementation Consortium) guidelines
"""

import logging
from typing import Dict, List, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PharmacogenomicsPredictor:
    """
    Pharmacogenomics prediction service

    Implements CPIC guidelines for drug-gene interactions
    """

    # CYP2D6 phenotypes and drug recommendations
    CYP2D6_GUIDELINES = {
        'poor_metabolizer': {
            'activity_score': '0',
            'drugs': {
                'codeine': {'recommendation': 'Avoid codeine. Use alternative analgesic.', 'evidence': 'Strong'},
                'tramadol': {'recommendation': 'Avoid tramadol. Use alternative analgesic.', 'evidence': 'Strong'},
                'tamoxifen': {'recommendation': 'Consider alternative therapy or higher dose.', 'evidence': 'Moderate'},
            }
        },
        'intermediate_metabolizer': {
            'activity_score': '0.5-1.0',
            'drugs': {
                'codeine': {'recommendation': 'Use alternative analgesic or reduce dose 50%.', 'evidence': 'Moderate'},
                'tramadol': {'recommendation': 'Consider 50% dose reduction or alternative.', 'evidence': 'Moderate'},
            }
        },
        'normal_metabolizer': {
            'activity_score': '1.0-2.0',
            'drugs': {
                'codeine': {'recommendation': 'Use standard dosing.', 'evidence': 'Strong'},
                'tramadol': {'recommendation': 'Use standard dosing.', 'evidence': 'Strong'},
                'tamoxifen': {'recommendation': 'Use standard dosing.', 'evidence': 'Strong'},
            }
        },
        'ultrarapid_metabolizer': {
            'activity_score': '>2.0',
            'drugs': {
                'codeine': {'recommendation': 'Avoid codeine due to toxicity risk. Use alternative.', 'evidence': 'Strong'},
                'tramadol': {'recommendation': 'Avoid tramadol. Use alternative analgesic.', 'evidence': 'Moderate'},
            }
        }
    }

    # CYP2C19 phenotypes
    CYP2C19_GUIDELINES = {
        'poor_metabolizer': {
            'drugs': {
                'clopidogrel': {'recommendation': 'Use alternative antiplatelet (prasugrel, ticagrelor).', 'evidence': 'Strong'},
                'voriconazole': {'recommendation': 'Reduce dose 50% and monitor levels.', 'evidence': 'Strong'},
                'escitalopram': {'recommendation': 'Reduce dose 50%.', 'evidence': 'Moderate'},
            }
        },
        'intermediate_metabolizer': {
            'drugs': {
                'clopidogrel': {'recommendation': 'Consider alternative antiplatelet.', 'evidence': 'Moderate'},
            }
        },
        'normal_metabolizer': {
            'drugs': {
                'clopidogrel': {'recommendation': 'Use standard dosing.', 'evidence': 'Strong'},
                'voriconazole': {'recommendation': 'Use standard dosing.', 'evidence': 'Strong'},
            }
        },
        'rapid_metabolizer': {
            'drugs': {
                'voriconazole': {'recommendation': 'Increase dose or use alternative.', 'evidence': 'Moderate'},
                'escitalopram': {'recommendation': 'May require higher dose.', 'evidence': 'Moderate'},
            }
        },
        'ultrarapid_metabolizer': {
            'drugs': {
                'clopidogrel': {'recommendation': 'Use standard dosing (enhanced effect).', 'evidence': 'Moderate'},
                'voriconazole': {'recommendation': 'Avoid voriconazole. Use alternative antifungal.', 'evidence': 'Strong'},
            }
        }
    }

    # TPMT deficiency
    TPMT_GUIDELINES = {
        'deficient': {
            'drugs': {
                'azathioprine': {'recommendation': 'Reduce dose to 10% of standard. Monitor CBC weekly.', 'evidence': 'Strong'},
                'mercaptopurine': {'recommendation': 'Reduce dose to 10% of standard. Monitor CBC weekly.', 'evidence': 'Strong'},
            }
        },
        'intermediate': {
            'drugs': {
                'azathioprine': {'recommendation': 'Reduce dose 30-70%. Monitor CBC.', 'evidence': 'Strong'},
                'mercaptopurine': {'recommendation': 'Reduce dose 30-70%. Monitor CBC.', 'evidence': 'Strong'},
            }
        },
        'normal': {
            'drugs': {
                'azathioprine': {'recommendation': 'Use standard dosing.', 'evidence': 'Strong'},
                'mercaptopurine': {'recommendation': 'Use standard dosing.', 'evidence': 'Strong'},
            }
        }
    }

    # DPYD deficiency (5-FU toxicity)
    DPYD_GUIDELINES = {
        'poor_metabolizer': {
            'drugs': {
                '5-fluorouracil': {'recommendation': 'AVOID 5-FU. Life-threatening toxicity risk.', 'evidence': 'Strong'},
                'capecitabine': {'recommendation': 'AVOID capecitabine. Life-threatening toxicity risk.', 'evidence': 'Strong'},
            }
        },
        'intermediate': {
            'drugs': {
                '5-fluorouracil': {'recommendation': 'Reduce dose 50%. Monitor closely.', 'evidence': 'Strong'},
                'capecitabine': {'recommendation': 'Reduce dose 50%. Monitor closely.', 'evidence': 'Strong'},
            }
        },
        'normal': {
            'drugs': {
                '5-fluorouracil': {'recommendation': 'Use standard dosing.', 'evidence': 'Strong'},
                'capecitabine': {'recommendation': 'Use standard dosing.', 'evidence': 'Strong'},
            }
        }
    }

    # Warfarin dosing (CYP2C9 + VKORC1)
    WARFARIN_DOSING = {
        ('CYP2C9_*1/*1', 'VKORC1_GG'): {'dose': '5-7 mg/day', 'sensitivity': 'standard'},
        ('CYP2C9_*1/*1', 'VKORC1_AG'): {'dose': '5-7 mg/day', 'sensitivity': 'standard'},
        ('CYP2C9_*1/*1', 'VKORC1_AA'): {'dose': '3-4 mg/day', 'sensitivity': 'intermediate'},
        ('CYP2C9_*1/*2', 'VKORC1_GG'): {'dose': '5-7 mg/day', 'sensitivity': 'standard'},
        ('CYP2C9_*1/*2', 'VKORC1_AG'): {'dose': '3-4 mg/day', 'sensitivity': 'intermediate'},
        ('CYP2C9_*1/*2', 'VKORC1_AA'): {'dose': '3-4 mg/day', 'sensitivity': 'high'},
        ('CYP2C9_*1/*3', 'VKORC1_GG'): {'dose': '3-4 mg/day', 'sensitivity': 'intermediate'},
        ('CYP2C9_*1/*3', 'VKORC1_AG'): {'dose': '3-4 mg/day', 'sensitivity': 'high'},
        ('CYP2C9_*1/*3', 'VKORC1_AA'): {'dose': '0.5-2 mg/day', 'sensitivity': 'very_high'},
        ('CYP2C9_*2/*2', 'VKORC1_GG'): {'dose': '3-4 mg/day', 'sensitivity': 'intermediate'},
        ('CYP2C9_*2/*2', 'VKORC1_AG'): {'dose': '3-4 mg/day', 'sensitivity': 'high'},
        ('CYP2C9_*2/*2', 'VKORC1_AA'): {'dose': '0.5-2 mg/day', 'sensitivity': 'very_high'},
        ('CYP2C9_*2/*3', 'VKORC1_AA'): {'dose': '0.5-2 mg/day', 'sensitivity': 'very_high'},
        ('CYP2C9_*3/*3', 'VKORC1_AA'): {'dose': '0.5-2 mg/day', 'sensitivity': 'very_high'},
    }

    def __init__(self):
        """Initialize pharmacogenomics predictor"""
        logger.info("Pharmacogenomics Predictor initialized")

    def predict_drug_response(
        self,
        gene: str,
        phenotype: str,
        drug: str
    ) -> Dict:
        """
        Predict drug response based on genetic phenotype

        Args:
            gene: Gene name (e.g., 'CYP2D6', 'CYP2C19', 'TPMT')
            phenotype: Phenotype (e.g., 'poor_metabolizer', 'normal_metabolizer')
            drug: Drug name

        Returns:
            Drug-gene interaction recommendation
        """
        try:
            gene = gene.upper()

            # Get guidelines for gene
            if gene == 'CYP2D6':
                guidelines = self.CYP2D6_GUIDELINES.get(phenotype, {})
            elif gene == 'CYP2C19':
                guidelines = self.CYP2C19_GUIDELINES.get(phenotype, {})
            elif gene == 'TPMT':
                guidelines = self.TPMT_GUIDELINES.get(phenotype, {})
            elif gene == 'DPYD':
                guidelines = self.DPYD_GUIDELINES.get(phenotype, {})
            else:
                return {
                    'status': 'error',
                    'error': f'Unknown gene: {gene}. Available genes: CYP2D6, CYP2C19, TPMT, DPYD'
                }

            if not guidelines:
                return {
                    'status': 'error',
                    'error': f'Unknown phenotype: {phenotype} for gene {gene}'
                }

            # Get drug-specific recommendation
            drug_info = guidelines.get('drugs', {}).get(drug.lower())

            if not drug_info:
                return {
                    'gene': gene,
                    'phenotype': phenotype,
                    'drug': drug,
                    'recommendation': f'No specific guidelines for {drug} with {gene} {phenotype}',
                    'evidence_level': 'None',
                    'status': 'success'
                }

            return {
                'gene': gene,
                'phenotype': phenotype,
                'drug': drug,
                'recommendation': drug_info['recommendation'],
                'evidence_level': drug_info['evidence'],
                'actionable': True,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Drug response prediction error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def calculate_warfarin_dose(
        self,
        cyp2c9_genotype: str,
        vkorc1_genotype: str,
        age: Optional[int] = None,
        weight: Optional[float] = None
    ) -> Dict:
        """
        Calculate personalized warfarin dose

        Args:
            cyp2c9_genotype: CYP2C9 genotype (e.g., '*1/*1', '*1/*2')
            vkorc1_genotype: VKORC1 genotype (e.g., 'GG', 'AG', 'AA')
            age: Patient age (years)
            weight: Patient weight (kg)

        Returns:
            Warfarin dosing recommendation
        """
        try:
            # Lookup base dose
            genotype_key = (cyp2c9_genotype, vkorc1_genotype)
            dosing_info = self.WARFARIN_DOSING.get(genotype_key)

            if not dosing_info:
                # Default to intermediate if not found
                dosing_info = {'dose': '3-5 mg/day', 'sensitivity': 'intermediate'}

            # Adjust for age (older patients require lower doses)
            age_adjustment = ""
            if age and age > 65:
                age_adjustment = "Consider reducing dose by 10-20% for age >65"
            elif age and age > 75:
                age_adjustment = "Consider reducing dose by 20-30% for age >75"

            # Adjust for weight
            weight_adjustment = ""
            if weight and weight < 50:
                weight_adjustment = "Consider reducing dose for low body weight (<50 kg)"

            return {
                'cyp2c9_genotype': cyp2c9_genotype,
                'vkorc1_genotype': vkorc1_genotype,
                'recommended_dose': dosing_info['dose'],
                'sensitivity': dosing_info['sensitivity'],
                'age_adjustment': age_adjustment or 'None',
                'weight_adjustment': weight_adjustment or 'None',
                'monitoring': 'Check INR after 3-4 doses, then weekly until stable, then monthly',
                'target_inr': '2.0-3.0 for most indications',
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Warfarin dosing error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def get_all_drug_interactions(self, genotypes: Dict[str, str]) -> List[Dict]:
        """
        Get all relevant drug-gene interactions for patient's genotypes

        Args:
            genotypes: Dictionary of gene: phenotype pairs
                      e.g., {'CYP2D6': 'poor_metabolizer', 'CYP2C19': 'normal_metabolizer'}

        Returns:
            List of all relevant drug recommendations
        """
        recommendations = []

        for gene, phenotype in genotypes.items():
            gene = gene.upper()

            # Get guidelines
            if gene == 'CYP2D6':
                guidelines = self.CYP2D6_GUIDELINES.get(phenotype, {})
            elif gene == 'CYP2C19':
                guidelines = self.CYP2C19_GUIDELINES.get(phenotype, {})
            elif gene == 'TPMT':
                guidelines = self.TPMT_GUIDELINES.get(phenotype, {})
            elif gene == 'DPYD':
                guidelines = self.DPYD_GUIDELINES.get(phenotype, {})
            else:
                continue

            # Extract all drug recommendations
            for drug, drug_info in guidelines.get('drugs', {}).items():
                recommendations.append({
                    'gene': gene,
                    'phenotype': phenotype,
                    'drug': drug,
                    'recommendation': drug_info['recommendation'],
                    'evidence_level': drug_info['evidence']
                })

        return recommendations


if __name__ == "__main__":
    predictor = PharmacogenomicsPredictor()
    print("Pharmacogenomics Predictor initialized")

    # Test case 1: CYP2D6 poor metabolizer with codeine
    result = predictor.predict_drug_response('CYP2D6', 'poor_metabolizer', 'codeine')
    print("\n=== CYP2D6 Poor Metabolizer + Codeine ===")
    print(json.dumps(result, indent=2))

    # Test case 2: Warfarin dosing
    result = predictor.calculate_warfarin_dose('CYP2C9_*1/*2', 'VKORC1_AG', age=70, weight=65)
    print("\n=== Warfarin Dosing ===")
    print(json.dumps(result, indent=2))

    # Test case 3: Multiple genotypes
    genotypes = {
        'CYP2D6': 'poor_metabolizer',
        'CYP2C19': 'normal_metabolizer',
        'TPMT': 'normal'
    }
    recommendations = predictor.get_all_drug_interactions(genotypes)
    print(f"\n=== All Drug Interactions ({len(recommendations)} found) ===")
    for rec in recommendations[:5]:
        print(json.dumps(rec, indent=2))
