"""
Clinical Validation Harness
Validates AI model predictions against expert annotations
Calculates sensitivity, specificity, AUC-ROC, Cohen's kappa
"""

import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics import roc_auc_score, confusion_matrix, cohen_kappa_score
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClinicalValidator:
    """Clinical validation framework for medical AI models"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.validation_results = []

    def validate_classification(
        self,
        predictions: List[int],
        ground_truth: List[int],
        probabilities: List[float] = None,
        class_names: List[str] = None
    ) -> Dict:
        """
        Validate classification model (binary or multi-class)

        Args:
            predictions: Model predictions (0/1 or class indices)
            ground_truth: Expert annotations
            probabilities: Prediction probabilities (for AUC-ROC)
            class_names: Names of classes

        Returns:
            Validation metrics
        """
        predictions = np.array(predictions)
        ground_truth = np.array(ground_truth)

        # Confusion matrix
        cm = confusion_matrix(ground_truth, predictions)

        # Binary classification metrics
        if len(np.unique(ground_truth)) == 2:
            tn, fp, fn, tp = cm.ravel()

            sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0
            accuracy = (tp + tn) / (tp + tn + fp + fn)

            # F1 score
            f1 = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0.0

            # AUC-ROC if probabilities provided
            auc_roc = None
            if probabilities is not None:
                try:
                    auc_roc = roc_auc_score(ground_truth, probabilities)
                except:
                    logger.warning("Could not calculate AUC-ROC")

            metrics = {
                'accuracy': float(accuracy),
                'sensitivity': float(sensitivity),
                'specificity': float(specificity),
                'precision': float(precision),
                'npv': float(npv),
                'f1_score': float(f1),
                'auc_roc': float(auc_roc) if auc_roc is not None else None,
                'confusion_matrix': {
                    'tn': int(tn), 'fp': int(fp),
                    'fn': int(fn), 'tp': int(tp)
                }
            }
        else:
            # Multi-class metrics
            accuracy = np.mean(predictions == ground_truth)
            metrics = {
                'accuracy': float(accuracy),
                'confusion_matrix': cm.tolist()
            }

        # Cohen's kappa (inter-rater agreement)
        kappa = cohen_kappa_score(ground_truth, predictions)
        metrics['cohen_kappa'] = float(kappa)

        # Clinical acceptability thresholds
        metrics['clinical_assessment'] = self._assess_clinical_acceptability(metrics)

        return metrics

    def validate_segmentation(
        self,
        pred_masks: List[np.ndarray],
        gt_masks: List[np.ndarray]
    ) -> Dict:
        """
        Validate segmentation model (Dice coefficient, IoU)

        Args:
            pred_masks: Predicted segmentation masks
            gt_masks: Ground truth masks

        Returns:
            Segmentation metrics
        """
        dice_scores = []
        iou_scores = []

        for pred, gt in zip(pred_masks, gt_masks):
            dice = self._calculate_dice(pred, gt)
            iou = self._calculate_iou(pred, gt)
            dice_scores.append(dice)
            iou_scores.append(iou)

        metrics = {
            'mean_dice': float(np.mean(dice_scores)),
            'std_dice': float(np.std(dice_scores)),
            'mean_iou': float(np.mean(iou_scores)),
            'std_iou': float(np.std(iou_scores)),
            'min_dice': float(np.min(dice_scores)),
            'max_dice': float(np.max(dice_scores))
        }

        metrics['clinical_assessment'] = self._assess_segmentation_quality(metrics)

        return metrics

    def _calculate_dice(self, pred: np.ndarray, gt: np.ndarray) -> float:
        """Calculate Dice coefficient"""
        intersection = np.sum(pred * gt)
        union = np.sum(pred) + np.sum(gt)

        if union == 0:
            return 1.0 if np.sum(pred) == 0 else 0.0

        dice = 2.0 * intersection / union
        return dice

    def _calculate_iou(self, pred: np.ndarray, gt: np.ndarray) -> float:
        """Calculate Intersection over Union (IoU)"""
        intersection = np.sum(pred * gt)
        union = np.sum((pred + gt) > 0)

        if union == 0:
            return 1.0 if intersection == 0 else 0.0

        iou = intersection / union
        return iou

    def _assess_clinical_acceptability(self, metrics: Dict) -> Dict:
        """
        Assess if model meets clinical acceptability thresholds

        FDA guidance for medical AI:
        - Sensitivity ≥ 90% for screening
        - Specificity ≥ 85% for screening
        - AUC-ROC ≥ 0.85
        """
        assessments = []

        # Check sensitivity (for screening/diagnostic)
        if 'sensitivity' in metrics:
            if metrics['sensitivity'] >= 0.90:
                assessments.append('✓ Sensitivity acceptable (≥90%)')
            elif metrics['sensitivity'] >= 0.85:
                assessments.append('⚠️ Sensitivity marginal (85-90%)')
            else:
                assessments.append('✗ Sensitivity too low (<85%)')

        # Check specificity
        if 'specificity' in metrics:
            if metrics['specificity'] >= 0.85:
                assessments.append('✓ Specificity acceptable (≥85%)')
            else:
                assessments.append('✗ Specificity too low (<85%)')

        # Check AUC-ROC
        if metrics.get('auc_roc'):
            if metrics['auc_roc'] >= 0.85:
                assessments.append('✓ AUC-ROC acceptable (≥0.85)')
            else:
                assessments.append('✗ AUC-ROC too low (<0.85)')

        # Check Cohen's kappa (inter-rater agreement)
        if 'cohen_kappa' in metrics:
            if metrics['cohen_kappa'] >= 0.80:
                assessments.append('✓ Excellent agreement (κ≥0.80)')
            elif metrics['cohen_kappa'] >= 0.60:
                assessments.append('⚠️ Substantial agreement (κ=0.60-0.80)')
            else:
                assessments.append('✗ Poor agreement (κ<0.60)')

        # Overall recommendation
        critical_failures = [a for a in assessments if a.startswith('✗')]
        if not critical_failures:
            recommendation = 'APPROVED: Model meets clinical acceptability criteria'
        elif len(critical_failures) == 1:
            recommendation = 'CONDITIONAL: Address identified issues before deployment'
        else:
            recommendation = 'NOT APPROVED: Multiple critical issues, requires retraining'

        return {
            'assessments': assessments,
            'recommendation': recommendation
        }

    def _assess_segmentation_quality(self, metrics: Dict) -> Dict:
        """Assess segmentation quality"""
        assessments = []

        # Dice coefficient thresholds
        if metrics['mean_dice'] >= 0.80:
            assessments.append('✓ Excellent segmentation (Dice ≥0.80)')
        elif metrics['mean_dice'] >= 0.70:
            assessments.append('⚠️ Good segmentation (Dice 0.70-0.80)')
        else:
            assessments.append('✗ Poor segmentation (Dice <0.70)')

        # Consistency check
        if metrics['std_dice'] < 0.10:
            assessments.append('✓ Consistent performance (std <0.10)')
        else:
            assessments.append('⚠️ Variable performance (std ≥0.10)')

        if metrics['mean_dice'] >= 0.75:
            recommendation = 'APPROVED: Segmentation quality acceptable'
        elif metrics['mean_dice'] >= 0.65:
            recommendation = 'CONDITIONAL: Consider refinement'
        else:
            recommendation = 'NOT APPROVED: Requires significant improvement'

        return {
            'assessments': assessments,
            'recommendation': recommendation
        }

    def generate_validation_report(self, metrics: Dict, test_description: str) -> str:
        """Generate markdown validation report"""
        report = f"""# Clinical Validation Report: {self.service_name}

## Test Description
{test_description}

## Validation Metrics
"""
        for key, value in metrics.items():
            if key != 'clinical_assessment' and key != 'confusion_matrix':
                if isinstance(value, float):
                    report += f"- **{key}**: {value:.4f}\n"
                else:
                    report += f"- **{key}**: {value}\n"

        if 'confusion_matrix' in metrics:
            cm = metrics['confusion_matrix']
            if isinstance(cm, dict):
                report += f"\n## Confusion Matrix\n"
                report += f"- True Positives: {cm['tp']}\n"
                report += f"- True Negatives: {cm['tn']}\n"
                report += f"- False Positives: {cm['fp']}\n"
                report += f"- False Negatives: {cm['fn']}\n"

        if 'clinical_assessment' in metrics:
            assessment = metrics['clinical_assessment']
            report += f"\n## Clinical Assessment\n"
            for item in assessment['assessments']:
                report += f"- {item}\n"
            report += f"\n### Recommendation\n{assessment['recommendation']}\n"

        return report


if __name__ == "__main__":
    # Demo validation
    validator = ClinicalValidator("Medical Imaging AI - Pneumonia Detection")

    # Simulate validation data
    np.random.seed(42)
    ground_truth = np.random.randint(0, 2, 100)
    predictions = ground_truth.copy()
    # Add some errors
    errors = np.random.choice(100, 10, replace=False)
    predictions[errors] = 1 - predictions[errors]
    probabilities = np.random.rand(100)

    # Validate
    metrics = validator.validate_classification(
        predictions.tolist(),
        ground_truth.tolist(),
        probabilities.tolist(),
        class_names=['Normal', 'Pneumonia']
    )

    # Generate report
    report = validator.generate_validation_report(
        metrics,
        "Pneumonia detection on 100 chest X-rays validated by 2 radiologists"
    )

    print(report)
