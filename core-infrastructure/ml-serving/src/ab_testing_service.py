"""
A/B Testing Service for ML Models
Enables controlled rollout and comparison of model versions in production
"""

import logging
import random
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

# Statistical analysis
import numpy as np
from scipy import stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SplitStrategy(Enum):
    """Traffic splitting strategies"""
    RANDOM = "random"
    HASH_BASED = "hash_based"  # Consistent per user
    WEIGHTED = "weighted"
    CANARY = "canary"  # Small percentage to new version


class ExperimentStatus(Enum):
    """Experiment lifecycle status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ABTestingService:
    """
    A/B Testing service for model deployment

    Features:
    - Traffic splitting (random, hash-based, weighted)
    - Canary deployments
    - Statistical significance testing
    - Performance monitoring
    - Automatic rollback on degradation
    """

    def __init__(self, min_sample_size: int = 100, confidence_level: float = 0.95):
        """
        Initialize A/B testing service

        Args:
            min_sample_size: Minimum samples before statistical testing
            confidence_level: Statistical confidence level (default: 95%)
        """
        self.min_sample_size = min_sample_size
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level

        # Active experiments
        self.experiments: Dict[str, Dict] = {}

        # Metrics storage (in production, use database)
        self.metrics: Dict[str, List[Dict]] = {}

        logger.info(f"A/B Testing service initialized (min_sample={min_sample_size}, α={self.alpha})")

    # ==================== EXPERIMENT MANAGEMENT ====================

    def create_experiment(
        self,
        experiment_id: str,
        model_name: str,
        control_version: int,
        treatment_version: int,
        traffic_split: float = 0.5,
        split_strategy: SplitStrategy = SplitStrategy.RANDOM,
        success_metric: str = "accuracy",
        duration_hours: int = 24,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create new A/B testing experiment

        Args:
            experiment_id: Unique experiment identifier
            model_name: Model being tested
            control_version: Baseline model version (A)
            treatment_version: New model version (B)
            traffic_split: Percentage to treatment (0.0-1.0)
            split_strategy: Traffic splitting strategy
            success_metric: Primary metric for comparison
            duration_hours: Experiment duration
            metadata: Additional experiment metadata

        Returns:
            Experiment configuration
        """
        if experiment_id in self.experiments:
            raise ValueError(f"Experiment {experiment_id} already exists")

        experiment = {
            'experiment_id': experiment_id,
            'model_name': model_name,
            'control_version': control_version,
            'treatment_version': treatment_version,
            'traffic_split': traffic_split,
            'split_strategy': split_strategy.value,
            'success_metric': success_metric,
            'status': ExperimentStatus.DRAFT.value,
            'start_time': None,
            'end_time': None,
            'duration_hours': duration_hours,
            'metadata': metadata or {},
            'created_at': datetime.utcnow().isoformat()
        }

        self.experiments[experiment_id] = experiment
        self.metrics[experiment_id] = []

        logger.info(f"Created experiment: {experiment_id}")

        return experiment

    def start_experiment(self, experiment_id: str) -> bool:
        """Start running experiment"""
        if experiment_id not in self.experiments:
            logger.error(f"Experiment not found: {experiment_id}")
            return False

        experiment = self.experiments[experiment_id]
        experiment['status'] = ExperimentStatus.RUNNING.value
        experiment['start_time'] = datetime.utcnow().isoformat()

        # Calculate end time
        start_time = datetime.fromisoformat(experiment['start_time'])
        end_time = start_time + timedelta(hours=experiment['duration_hours'])
        experiment['end_time'] = end_time.isoformat()

        logger.info(f"Started experiment: {experiment_id}")

        return True

    def stop_experiment(self, experiment_id: str) -> bool:
        """Stop experiment and mark as completed"""
        if experiment_id not in self.experiments:
            return False

        experiment = self.experiments[experiment_id]
        experiment['status'] = ExperimentStatus.COMPLETED.value
        experiment['completed_at'] = datetime.utcnow().isoformat()

        logger.info(f"Stopped experiment: {experiment_id}")

        return True

    # ==================== TRAFFIC SPLITTING ====================

    def route_request(
        self,
        experiment_id: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Tuple[int, str]:
        """
        Route request to control or treatment version

        Args:
            experiment_id: Experiment ID
            user_id: User identifier (for hash-based routing)
            request_id: Request identifier

        Returns:
            (model_version, variant) where variant is 'control' or 'treatment'
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")

        experiment = self.experiments[experiment_id]

        if experiment['status'] != ExperimentStatus.RUNNING.value:
            # Experiment not running, use control
            return experiment['control_version'], 'control'

        strategy = SplitStrategy(experiment['split_strategy'])
        traffic_split = experiment['traffic_split']

        # Route based on strategy
        if strategy == SplitStrategy.RANDOM:
            use_treatment = random.random() < traffic_split

        elif strategy == SplitStrategy.HASH_BASED:
            if not user_id:
                # Fall back to random if no user_id
                use_treatment = random.random() < traffic_split
            else:
                # Consistent routing based on user_id hash
                hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
                use_treatment = (hash_value % 100) < (traffic_split * 100)

        elif strategy == SplitStrategy.WEIGHTED:
            use_treatment = random.random() < traffic_split

        elif strategy == SplitStrategy.CANARY:
            # Canary: small percentage to treatment
            use_treatment = random.random() < traffic_split

        else:
            use_treatment = False

        if use_treatment:
            return experiment['treatment_version'], 'treatment'
        else:
            return experiment['control_version'], 'control'

    # ==================== METRICS COLLECTION ====================

    def record_prediction(
        self,
        experiment_id: str,
        variant: str,
        prediction: Any,
        ground_truth: Optional[Any] = None,
        latency_ms: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Record model prediction for experiment

        Args:
            experiment_id: Experiment ID
            variant: 'control' or 'treatment'
            prediction: Model prediction
            ground_truth: True label (if available)
            latency_ms: Inference latency in milliseconds
            metadata: Additional metadata

        Returns:
            Success status
        """
        if experiment_id not in self.metrics:
            self.metrics[experiment_id] = []

        record = {
            'timestamp': datetime.utcnow().isoformat(),
            'variant': variant,
            'prediction': prediction,
            'ground_truth': ground_truth,
            'latency_ms': latency_ms,
            'metadata': metadata or {}
        }

        self.metrics[experiment_id].append(record)

        return True

    def record_metric(
        self,
        experiment_id: str,
        variant: str,
        metric_name: str,
        metric_value: float,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Record custom metric value

        Args:
            experiment_id: Experiment ID
            variant: 'control' or 'treatment'
            metric_name: Metric name
            metric_value: Metric value
            metadata: Additional metadata

        Returns:
            Success status
        """
        if experiment_id not in self.metrics:
            self.metrics[experiment_id] = []

        record = {
            'timestamp': datetime.utcnow().isoformat(),
            'variant': variant,
            'metric_name': metric_name,
            'metric_value': metric_value,
            'metadata': metadata or {}
        }

        self.metrics[experiment_id].append(record)

        return True

    # ==================== STATISTICAL ANALYSIS ====================

    def analyze_experiment(self, experiment_id: str) -> Dict:
        """
        Perform statistical analysis of experiment results

        Args:
            experiment_id: Experiment ID

        Returns:
            Analysis results with statistical tests
        """
        if experiment_id not in self.experiments:
            return {'error': 'Experiment not found'}

        experiment = self.experiments[experiment_id]
        metrics = self.metrics.get(experiment_id, [])

        if not metrics:
            return {
                'experiment_id': experiment_id,
                'status': 'insufficient_data',
                'message': 'No metrics collected yet'
            }

        # Separate control and treatment metrics
        control_metrics = [m for m in metrics if m['variant'] == 'control']
        treatment_metrics = [m for m in metrics if m['variant'] == 'treatment']

        # Sample sizes
        control_n = len(control_metrics)
        treatment_n = len(treatment_metrics)

        if control_n < self.min_sample_size or treatment_n < self.min_sample_size:
            return {
                'experiment_id': experiment_id,
                'status': 'insufficient_data',
                'control_sample_size': control_n,
                'treatment_sample_size': treatment_n,
                'required_sample_size': self.min_sample_size,
                'message': f'Need at least {self.min_sample_size} samples per variant'
            }

        # Extract metric values (assuming metric_value field exists)
        control_values = [m.get('metric_value') for m in control_metrics if 'metric_value' in m]
        treatment_values = [m.get('metric_value') for m in treatment_metrics if 'metric_value' in m]

        if not control_values or not treatment_values:
            return {
                'experiment_id': experiment_id,
                'status': 'no_metric_values',
                'message': 'No metric values found'
            }

        # Calculate statistics
        control_mean = np.mean(control_values)
        treatment_mean = np.mean(treatment_values)
        control_std = np.std(control_values, ddof=1)
        treatment_std = np.std(treatment_values, ddof=1)

        # Perform t-test
        t_statistic, p_value = stats.ttest_ind(treatment_values, control_values)

        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((control_n - 1) * control_std**2 + (treatment_n - 1) * treatment_std**2) / (control_n + treatment_n - 2))
        cohens_d = (treatment_mean - control_mean) / pooled_std if pooled_std > 0 else 0

        # Determine statistical significance
        is_significant = p_value < self.alpha

        # Calculate confidence interval for difference
        se_diff = pooled_std * np.sqrt(1/control_n + 1/treatment_n)
        t_critical = stats.t.ppf(1 - self.alpha/2, control_n + treatment_n - 2)
        ci_lower = (treatment_mean - control_mean) - t_critical * se_diff
        ci_upper = (treatment_mean - control_mean) + t_critical * se_diff

        # Determine winner
        if is_significant:
            winner = 'treatment' if treatment_mean > control_mean else 'control'
        else:
            winner = 'no_clear_winner'

        analysis = {
            'experiment_id': experiment_id,
            'status': 'complete',
            'sample_sizes': {
                'control': control_n,
                'treatment': treatment_n
            },
            'means': {
                'control': float(control_mean),
                'treatment': float(treatment_mean),
                'absolute_difference': float(treatment_mean - control_mean),
                'relative_improvement': float((treatment_mean - control_mean) / control_mean * 100) if control_mean != 0 else 0
            },
            'std_deviations': {
                'control': float(control_std),
                'treatment': float(treatment_std)
            },
            'statistical_test': {
                'test': 'independent_t_test',
                't_statistic': float(t_statistic),
                'p_value': float(p_value),
                'significance_level': self.alpha,
                'is_significant': is_significant
            },
            'effect_size': {
                'cohens_d': float(cohens_d),
                'interpretation': self._interpret_effect_size(cohens_d)
            },
            'confidence_interval': {
                'level': self.confidence_level,
                'lower': float(ci_lower),
                'upper': float(ci_upper)
            },
            'winner': winner,
            'recommendation': self._get_recommendation(winner, cohens_d, is_significant)
        }

        logger.info(f"Analysis complete for {experiment_id}: winner={winner}, p={p_value:.4f}")

        return analysis

    def calculate_latency_comparison(self, experiment_id: str) -> Dict:
        """Compare inference latency between variants"""
        metrics = self.metrics.get(experiment_id, [])

        control_latencies = [m['latency_ms'] for m in metrics if m['variant'] == 'control' and 'latency_ms' in m and m['latency_ms'] is not None]
        treatment_latencies = [m['latency_ms'] for m in metrics if m['variant'] == 'treatment' and 'latency_ms' in m and m['latency_ms'] is not None]

        if not control_latencies or not treatment_latencies:
            return {'error': 'No latency data available'}

        return {
            'control': {
                'mean_ms': float(np.mean(control_latencies)),
                'median_ms': float(np.median(control_latencies)),
                'p95_ms': float(np.percentile(control_latencies, 95)),
                'p99_ms': float(np.percentile(control_latencies, 99))
            },
            'treatment': {
                'mean_ms': float(np.mean(treatment_latencies)),
                'median_ms': float(np.median(treatment_latencies)),
                'p95_ms': float(np.percentile(treatment_latencies, 95)),
                'p99_ms': float(np.percentile(treatment_latencies, 99))
            },
            'difference': {
                'mean_ms': float(np.mean(treatment_latencies) - np.mean(control_latencies)),
                'relative_change_pct': float((np.mean(treatment_latencies) - np.mean(control_latencies)) / np.mean(control_latencies) * 100)
            }
        }

    # ==================== HELPER METHODS ====================

    def _interpret_effect_size(self, cohens_d: float) -> str:
        """Interpret Cohen's d effect size"""
        abs_d = abs(cohens_d)

        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"

    def _get_recommendation(self, winner: str, cohens_d: float, is_significant: bool) -> str:
        """Get deployment recommendation"""
        if not is_significant:
            return "Continue experiment - no significant difference yet"

        if winner == 'treatment':
            if abs(cohens_d) >= 0.5:
                return "DEPLOY treatment version - significant improvement with meaningful effect size"
            else:
                return "Consider deploying treatment version - statistically significant but small effect"
        elif winner == 'control':
            return "ROLLBACK to control version - treatment performs worse"
        else:
            return "No clear winner - consider extended testing"

    def get_experiment_summary(self, experiment_id: str) -> Dict:
        """Get experiment summary"""
        if experiment_id not in self.experiments:
            return {'error': 'Experiment not found'}

        experiment = self.experiments[experiment_id]
        metrics_count = len(self.metrics.get(experiment_id, []))

        control_count = len([m for m in self.metrics.get(experiment_id, []) if m['variant'] == 'control'])
        treatment_count = len([m for m in self.metrics.get(experiment_id, []) if m['variant'] == 'treatment'])

        return {
            'experiment_id': experiment_id,
            'model_name': experiment['model_name'],
            'control_version': experiment['control_version'],
            'treatment_version': experiment['treatment_version'],
            'status': experiment['status'],
            'traffic_split': experiment['traffic_split'],
            'total_requests': metrics_count,
            'control_requests': control_count,
            'treatment_requests': treatment_count,
            'start_time': experiment.get('start_time'),
            'end_time': experiment.get('end_time')
        }


if __name__ == "__main__":
    # Example usage
    ab_service = ABTestingService(min_sample_size=30, confidence_level=0.95)

    # Create experiment
    experiment = ab_service.create_experiment(
        experiment_id="chest_xray_v1_vs_v2",
        model_name="chest_xray_classifier",
        control_version=1,
        treatment_version=2,
        traffic_split=0.5,
        split_strategy=SplitStrategy.HASH_BASED,
        success_metric="accuracy",
        duration_hours=48
    )

    print(f"Created experiment: {experiment['experiment_id']}")

    # Start experiment
    ab_service.start_experiment("chest_xray_v1_vs_v2")

    # Simulate routing
    user_id = "patient_12345"
    version, variant = ab_service.route_request("chest_xray_v1_vs_v2", user_id=user_id)
    print(f"User {user_id} routed to: {variant} (version {version})")

    print("\nA/B Testing service ready")
