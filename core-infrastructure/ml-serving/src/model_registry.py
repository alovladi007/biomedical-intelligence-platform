"""
MLflow Model Registry Service
Manages ML model lifecycle: registration, versioning, staging, production deployment
"""

import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import json

# MLflow
import mlflow
from mlflow.tracking import MlflowClient
from mlflow.entities import ViewType
from mlflow.exceptions import MlflowException

# Model conversion
import torch
import tensorflow as tf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelStage:
    """Model lifecycle stages"""
    NONE = "None"
    STAGING = "Staging"
    PRODUCTION = "Production"
    ARCHIVED = "Archived"


class ModelRegistry:
    """
    MLflow-based model registry for biomedical AI models

    Features:
    - Model registration and versioning
    - Stage transitions (None → Staging → Production)
    - Model comparison and A/B testing
    - Metadata tracking (metrics, params, tags)
    - Model artifact management
    """

    def __init__(
        self,
        tracking_uri: str = "http://localhost:5000",
        registry_uri: Optional[str] = None,
        artifact_location: Optional[str] = None
    ):
        """
        Initialize model registry

        Args:
            tracking_uri: MLflow tracking server URI
            registry_uri: Model registry URI (defaults to tracking_uri)
            artifact_location: S3 bucket or local path for artifacts
        """
        self.tracking_uri = tracking_uri
        self.registry_uri = registry_uri or tracking_uri
        self.artifact_location = artifact_location

        # Set MLflow URIs
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_registry_uri(self.registry_uri)

        # Initialize client
        self.client = MlflowClient(tracking_uri=self.tracking_uri, registry_uri=self.registry_uri)

        logger.info(f"Model registry initialized: {self.registry_uri}")

    # ==================== MODEL REGISTRATION ====================

    def register_pytorch_model(
        self,
        model: torch.nn.Module,
        model_name: str,
        example_input: Optional[torch.Tensor] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Register PyTorch model

        Args:
            model: PyTorch model
            model_name: Registered model name
            example_input: Example input tensor for tracing
            metadata: Model metadata (architecture, training info)
            tags: Key-value tags

        Returns:
            Model version info
        """
        try:
            # Start MLflow run
            with mlflow.start_run() as run:
                # Log model
                if example_input is not None:
                    mlflow.pytorch.log_model(
                        pytorch_model=model,
                        artifact_path="model",
                        registered_model_name=model_name,
                        signature=mlflow.models.infer_signature(
                            example_input.numpy(),
                            model(example_input).detach().numpy()
                        )
                    )
                else:
                    mlflow.pytorch.log_model(
                        pytorch_model=model,
                        artifact_path="model",
                        registered_model_name=model_name
                    )

                # Log metadata
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(key, value)
                        else:
                            mlflow.log_param(key, value)

                # Log tags
                if tags:
                    mlflow.set_tags(tags)

                # Add default tags
                mlflow.set_tag("framework", "pytorch")
                mlflow.set_tag("registered_at", datetime.utcnow().isoformat())

                run_id = run.info.run_id

            # Get registered model version
            model_version = self._get_latest_version(model_name)

            logger.info(f"Registered PyTorch model: {model_name} v{model_version}")

            return {
                'model_name': model_name,
                'version': model_version,
                'run_id': run_id,
                'stage': ModelStage.NONE,
                'framework': 'pytorch'
            }

        except Exception as e:
            logger.error(f"PyTorch model registration failed: {str(e)}")
            raise

    def register_tensorflow_model(
        self,
        model: tf.keras.Model,
        model_name: str,
        example_input: Optional[Any] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Register TensorFlow/Keras model

        Args:
            model: TensorFlow Keras model
            model_name: Registered model name
            example_input: Example input for signature inference
            metadata: Model metadata
            tags: Key-value tags

        Returns:
            Model version info
        """
        try:
            with mlflow.start_run() as run:
                # Log model
                if example_input is not None:
                    predictions = model.predict(example_input)
                    signature = mlflow.models.infer_signature(example_input, predictions)

                    mlflow.tensorflow.log_model(
                        model=model,
                        artifact_path="model",
                        registered_model_name=model_name,
                        signature=signature
                    )
                else:
                    mlflow.tensorflow.log_model(
                        model=model,
                        artifact_path="model",
                        registered_model_name=model_name
                    )

                # Log metadata
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(key, value)
                        else:
                            mlflow.log_param(key, value)

                # Log tags
                if tags:
                    mlflow.set_tags(tags)

                mlflow.set_tag("framework", "tensorflow")
                mlflow.set_tag("registered_at", datetime.utcnow().isoformat())

                run_id = run.info.run_id

            model_version = self._get_latest_version(model_name)

            logger.info(f"Registered TensorFlow model: {model_name} v{model_version}")

            return {
                'model_name': model_name,
                'version': model_version,
                'run_id': run_id,
                'stage': ModelStage.NONE,
                'framework': 'tensorflow'
            }

        except Exception as e:
            logger.error(f"TensorFlow model registration failed: {str(e)}")
            raise

    # ==================== STAGE MANAGEMENT ====================

    def transition_stage(
        self,
        model_name: str,
        version: int,
        stage: str,
        archive_existing: bool = True
    ) -> bool:
        """
        Transition model to new stage

        Args:
            model_name: Model name
            version: Model version
            stage: Target stage (Staging, Production, Archived)
            archive_existing: Archive models currently in target stage

        Returns:
            Success status
        """
        try:
            # Archive existing models in target stage
            if archive_existing and stage in [ModelStage.STAGING, ModelStage.PRODUCTION]:
                existing_models = self.client.get_latest_versions(
                    model_name,
                    stages=[stage]
                )

                for existing in existing_models:
                    self.client.transition_model_version_stage(
                        name=model_name,
                        version=existing.version,
                        stage=ModelStage.ARCHIVED
                    )
                    logger.info(f"Archived {model_name} v{existing.version}")

            # Transition to new stage
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage
            )

            logger.info(f"Transitioned {model_name} v{version} to {stage}")

            return True

        except Exception as e:
            logger.error(f"Stage transition failed: {str(e)}")
            return False

    def promote_to_production(self, model_name: str, version: int) -> bool:
        """
        Promote model version to production

        Args:
            model_name: Model name
            version: Version to promote

        Returns:
            Success status
        """
        return self.transition_stage(model_name, version, ModelStage.PRODUCTION)

    def promote_to_staging(self, model_name: str, version: int) -> bool:
        """
        Promote model version to staging

        Args:
            model_name: Model name
            version: Version to promote

        Returns:
            Success status
        """
        return self.transition_stage(model_name, version, ModelStage.STAGING)

    # ==================== MODEL RETRIEVAL ====================

    def get_production_model(self, model_name: str) -> Optional[Dict]:
        """
        Get current production model

        Args:
            model_name: Model name

        Returns:
            Model info or None
        """
        try:
            versions = self.client.get_latest_versions(
                model_name,
                stages=[ModelStage.PRODUCTION]
            )

            if versions:
                version = versions[0]
                return {
                    'model_name': model_name,
                    'version': version.version,
                    'stage': version.current_stage,
                    'run_id': version.run_id,
                    'source': version.source,
                    'creation_timestamp': version.creation_timestamp,
                    'last_updated_timestamp': version.last_updated_timestamp
                }

            return None

        except Exception as e:
            logger.error(f"Failed to get production model: {str(e)}")
            return None

    def get_model_version(self, model_name: str, version: int) -> Optional[Dict]:
        """Get specific model version info"""
        try:
            model_version = self.client.get_model_version(model_name, version)

            return {
                'model_name': model_name,
                'version': model_version.version,
                'stage': model_version.current_stage,
                'run_id': model_version.run_id,
                'source': model_version.source,
                'creation_timestamp': model_version.creation_timestamp,
                'last_updated_timestamp': model_version.last_updated_timestamp,
                'description': model_version.description,
                'tags': model_version.tags
            }

        except Exception as e:
            logger.error(f"Failed to get model version: {str(e)}")
            return None

    def list_model_versions(
        self,
        model_name: str,
        stage: Optional[str] = None
    ) -> List[Dict]:
        """
        List all versions of a model

        Args:
            model_name: Model name
            stage: Filter by stage (optional)

        Returns:
            List of model version info
        """
        try:
            if stage:
                versions = self.client.get_latest_versions(model_name, stages=[stage])
            else:
                versions = self.client.search_model_versions(f"name='{model_name}'")

            results = []
            for version in versions:
                results.append({
                    'version': version.version,
                    'stage': version.current_stage,
                    'run_id': version.run_id,
                    'creation_timestamp': version.creation_timestamp
                })

            return sorted(results, key=lambda x: x['version'], reverse=True)

        except Exception as e:
            logger.error(f"Failed to list model versions: {str(e)}")
            return []

    # ==================== MODEL COMPARISON ====================

    def compare_models(
        self,
        model_name: str,
        version1: int,
        version2: int,
        metrics: Optional[List[str]] = None
    ) -> Dict:
        """
        Compare two model versions

        Args:
            model_name: Model name
            version1: First version
            version2: Second version
            metrics: List of metrics to compare

        Returns:
            Comparison results
        """
        try:
            # Get model version info
            v1_info = self.client.get_model_version(model_name, version1)
            v2_info = self.client.get_model_version(model_name, version2)

            # Get run metrics
            v1_run = self.client.get_run(v1_info.run_id)
            v2_run = self.client.get_run(v2_info.run_id)

            comparison = {
                'model_name': model_name,
                'version1': {
                    'version': version1,
                    'stage': v1_info.current_stage,
                    'metrics': v1_run.data.metrics,
                    'params': v1_run.data.params
                },
                'version2': {
                    'version': version2,
                    'stage': v2_info.current_stage,
                    'metrics': v2_run.data.metrics,
                    'params': v2_run.data.params
                },
                'metric_diff': {}
            }

            # Calculate metric differences
            if metrics:
                for metric in metrics:
                    if metric in v1_run.data.metrics and metric in v2_run.data.metrics:
                        diff = v2_run.data.metrics[metric] - v1_run.data.metrics[metric]
                        comparison['metric_diff'][metric] = {
                            'v1': v1_run.data.metrics[metric],
                            'v2': v2_run.data.metrics[metric],
                            'diff': diff,
                            'improvement': diff > 0
                        }

            return comparison

        except Exception as e:
            logger.error(f"Model comparison failed: {str(e)}")
            return {}

    # ==================== ROLLBACK ====================

    def rollback_to_version(
        self,
        model_name: str,
        version: int,
        stage: str = ModelStage.PRODUCTION
    ) -> bool:
        """
        Rollback to previous model version

        Args:
            model_name: Model name
            version: Version to rollback to
            stage: Target stage

        Returns:
            Success status
        """
        try:
            # Transition target version to stage
            success = self.transition_stage(model_name, version, stage)

            if success:
                logger.info(f"Rolled back {model_name} to v{version} in {stage}")
            else:
                logger.error(f"Rollback failed for {model_name} v{version}")

            return success

        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return False

    # ==================== METADATA MANAGEMENT ====================

    def update_model_description(
        self,
        model_name: str,
        version: int,
        description: str
    ) -> bool:
        """Update model version description"""
        try:
            self.client.update_model_version(
                name=model_name,
                version=version,
                description=description
            )

            logger.info(f"Updated description for {model_name} v{version}")
            return True

        except Exception as e:
            logger.error(f"Failed to update description: {str(e)}")
            return False

    def add_model_tags(
        self,
        model_name: str,
        version: int,
        tags: Dict[str, str]
    ) -> bool:
        """Add tags to model version"""
        try:
            for key, value in tags.items():
                self.client.set_model_version_tag(model_name, version, key, value)

            logger.info(f"Added tags to {model_name} v{version}: {tags}")
            return True

        except Exception as e:
            logger.error(f"Failed to add tags: {str(e)}")
            return False

    # ==================== HELPER METHODS ====================

    def _get_latest_version(self, model_name: str) -> int:
        """Get latest version number for a model"""
        try:
            versions = self.client.search_model_versions(f"name='{model_name}'")

            if versions:
                return max([int(v.version) for v in versions])
            else:
                return 1

        except Exception as e:
            logger.error(f"Failed to get latest version: {str(e)}")
            return 1

    def delete_model_version(self, model_name: str, version: int) -> bool:
        """Delete a model version (use with caution)"""
        try:
            self.client.delete_model_version(model_name, version)
            logger.info(f"Deleted {model_name} v{version}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete model version: {str(e)}")
            return False

    def get_registry_stats(self) -> Dict:
        """Get registry statistics"""
        try:
            all_models = self.client.search_registered_models()

            stats = {
                'total_models': len(all_models),
                'by_stage': {
                    ModelStage.PRODUCTION: 0,
                    ModelStage.STAGING: 0,
                    ModelStage.ARCHIVED: 0,
                    ModelStage.NONE: 0
                },
                'total_versions': 0
            }

            for model in all_models:
                versions = self.client.search_model_versions(f"name='{model.name}'")
                stats['total_versions'] += len(versions)

                for version in versions:
                    stage = version.current_stage
                    stats['by_stage'][stage] = stats['by_stage'].get(stage, 0) + 1

            return stats

        except Exception as e:
            logger.error(f"Failed to get registry stats: {str(e)}")
            return {}


if __name__ == "__main__":
    # Example usage
    registry = ModelRegistry(
        tracking_uri="http://localhost:5000",
        artifact_location="s3://biomedical-models"
    )

    print("Model Registry initialized")
    print(f"Tracking URI: {registry.tracking_uri}")

    # Get registry statistics
    stats = registry.get_registry_stats()
    print(f"\nRegistry Statistics:")
    print(f"Total models: {stats.get('total_models', 0)}")
    print(f"Total versions: {stats.get('total_versions', 0)}")
    print(f"Production models: {stats.get('by_stage', {}).get('Production', 0)}")

    print("\nModel Registry ready for medical AI models")
