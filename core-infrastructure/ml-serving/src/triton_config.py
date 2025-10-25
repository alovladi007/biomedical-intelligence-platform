"""
NVIDIA Triton Inference Server Configuration
Manages model deployment, versioning, and serving configuration
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported ML platforms"""
    TENSORFLOW = "tensorflow_savedmodel"
    PYTORCH = "pytorch_libtorch"
    ONNX = "onnxruntime_onnx"
    TENSORRT = "tensorrt_plan"
    PYTHON = "python"


class InstanceGroup(Enum):
    """Instance placement"""
    GPU = "KIND_GPU"
    CPU = "KIND_CPU"
    AUTO = "KIND_AUTO"


@dataclass
class ModelInstance:
    """Model instance configuration"""
    count: int = 1
    kind: InstanceGroup = InstanceGroup.GPU
    gpus: Optional[List[int]] = None


@dataclass
class DynamicBatching:
    """Dynamic batching configuration"""
    preferred_batch_size: List[int] = None
    max_queue_delay_microseconds: int = 100
    preserve_ordering: bool = False
    priority_levels: int = 0
    default_priority_level: int = 0

    def __post_init__(self):
        if self.preferred_batch_size is None:
            self.preferred_batch_size = [1, 2, 4, 8]


@dataclass
class ModelInput:
    """Model input specification"""
    name: str
    data_type: str  # TYPE_FP32, TYPE_INT32, etc.
    dims: List[int]  # [-1, 224, 224, 3] for variable batch size


@dataclass
class ModelOutput:
    """Model output specification"""
    name: str
    data_type: str
    dims: List[int]


class TritonModelConfig:
    """
    NVIDIA Triton Model Configuration Generator

    Creates config.pbtxt files for model deployment on Triton Inference Server
    """

    # Supported data types
    DATA_TYPES = {
        'float32': 'TYPE_FP32',
        'float16': 'TYPE_FP16',
        'int32': 'TYPE_INT32',
        'int64': 'TYPE_INT64',
        'uint8': 'TYPE_UINT8',
        'bool': 'TYPE_BOOL',
        'string': 'TYPE_STRING'
    }

    def __init__(self, model_repository_path: str = "./model_repository"):
        """
        Initialize Triton configuration manager

        Args:
            model_repository_path: Path to model repository
        """
        self.model_repository_path = Path(model_repository_path)
        self.model_repository_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Model repository: {self.model_repository_path}")

    def create_model_config(
        self,
        model_name: str,
        platform: Platform,
        inputs: List[ModelInput],
        outputs: List[ModelOutput],
        max_batch_size: int = 8,
        instance_config: Optional[ModelInstance] = None,
        dynamic_batching: Optional[DynamicBatching] = None,
        version_policy: str = "latest",
        num_versions: int = 1,
        optimization_level: int = 1,
        **kwargs
    ) -> str:
        """
        Create Triton model configuration

        Args:
            model_name: Name of the model
            platform: ML platform (TensorFlow, PyTorch, ONNX, etc.)
            inputs: List of model inputs
            outputs: List of model outputs
            max_batch_size: Maximum batch size (0 for non-batching models)
            instance_config: Instance group configuration
            dynamic_batching: Dynamic batching settings
            version_policy: "latest", "all", or "specific"
            num_versions: Number of versions to keep (for "latest")
            optimization_level: Graph optimization level (0-3)

        Returns:
            Path to generated config file
        """
        # Create model directory
        model_dir = self.model_repository_path / model_name
        model_dir.mkdir(parents=True, exist_ok=True)

        # Default instance config
        if instance_config is None:
            instance_config = ModelInstance()

        # Build configuration
        config_lines = []

        # Model name and platform
        config_lines.append(f'name: "{model_name}"')
        config_lines.append(f'platform: "{platform.value}"')
        config_lines.append(f'max_batch_size: {max_batch_size}')
        config_lines.append('')

        # Inputs
        for input_spec in inputs:
            config_lines.append('input [')
            config_lines.append('  {')
            config_lines.append(f'    name: "{input_spec.name}"')
            config_lines.append(f'    data_type: {input_spec.data_type}')
            dims_str = ', '.join(map(str, input_spec.dims))
            config_lines.append(f'    dims: [ {dims_str} ]')
            config_lines.append('  }')
            config_lines.append(']')

        config_lines.append('')

        # Outputs
        for output_spec in outputs:
            config_lines.append('output [')
            config_lines.append('  {')
            config_lines.append(f'    name: "{output_spec.name}"')
            config_lines.append(f'    data_type: {output_spec.data_type}')
            dims_str = ', '.join(map(str, output_spec.dims))
            config_lines.append(f'    dims: [ {dims_str} ]')
            config_lines.append('  }')
            config_lines.append(']')

        config_lines.append('')

        # Instance group
        config_lines.append('instance_group [')
        config_lines.append('  {')
        config_lines.append(f'    count: {instance_config.count}')
        config_lines.append(f'    kind: {instance_config.kind.value}')

        if instance_config.gpus:
            gpus_str = ', '.join(map(str, instance_config.gpus))
            config_lines.append(f'    gpus: [ {gpus_str} ]')

        config_lines.append('  }')
        config_lines.append(']')
        config_lines.append('')

        # Dynamic batching
        if dynamic_batching:
            config_lines.append('dynamic_batching {')

            if dynamic_batching.preferred_batch_size:
                sizes_str = ', '.join(map(str, dynamic_batching.preferred_batch_size))
                config_lines.append(f'  preferred_batch_size: [ {sizes_str} ]')

            config_lines.append(f'  max_queue_delay_microseconds: {dynamic_batching.max_queue_delay_microseconds}')

            if dynamic_batching.preserve_ordering:
                config_lines.append('  preserve_ordering: true')

            if dynamic_batching.priority_levels > 0:
                config_lines.append(f'  priority_levels: {dynamic_batching.priority_levels}')
                config_lines.append(f'  default_priority_level: {dynamic_batching.default_priority_level}')

            config_lines.append('}')
            config_lines.append('')

        # Version policy
        config_lines.append('version_policy: {')
        if version_policy == "latest":
            config_lines.append(f'  latest {{ num_versions: {num_versions} }}')
        elif version_policy == "all":
            config_lines.append('  all { }')
        elif version_policy == "specific":
            versions = kwargs.get('versions', [1])
            versions_str = ', '.join(map(str, versions))
            config_lines.append(f'  specific {{ versions: [ {versions_str} ] }}')
        config_lines.append('}')
        config_lines.append('')

        # Optimization
        if platform in [Platform.TENSORFLOW, Platform.ONNX]:
            config_lines.append('optimization {')
            config_lines.append(f'  graph {{')
            config_lines.append(f'    level: {optimization_level}')
            config_lines.append('  }')
            config_lines.append('}')
            config_lines.append('')

        # Model warmup (optional)
        if kwargs.get('enable_warmup', False):
            config_lines.append('model_warmup [')
            config_lines.append('  {')
            config_lines.append('    name: "warmup_batch_1"')
            config_lines.append('    batch_size: 1')
            config_lines.append('    inputs {')
            for input_spec in inputs:
                config_lines.append(f'      key: "{input_spec.name}"')
                config_lines.append('      value: {')
                config_lines.append('        data_type: TYPE_FP32')
                config_lines.append('        dims: [ 1 ]')
                config_lines.append('        zero_data: true')
                config_lines.append('      }')
            config_lines.append('    }')
            config_lines.append('  }')
            config_lines.append(']')

        # Write config file
        config_path = model_dir / 'config.pbtxt'
        config_content = '\n'.join(config_lines)

        with open(config_path, 'w') as f:
            f.write(config_content)

        logger.info(f"Created model config: {config_path}")

        return str(config_path)

    def create_ensemble_config(
        self,
        ensemble_name: str,
        pipeline_steps: List[Dict[str, Any]],
        max_batch_size: int = 8
    ) -> str:
        """
        Create ensemble model configuration (model pipeline)

        Args:
            ensemble_name: Name of ensemble
            pipeline_steps: List of pipeline steps with model names and input/output mappings
            max_batch_size: Maximum batch size

        Example pipeline_steps:
        [
            {
                'model_name': 'preprocessing',
                'model_version': -1,  # latest
                'input_map': {'raw_image': 'INPUT'},
                'output_map': {'preprocessed': 'preprocessed_image'}
            },
            {
                'model_name': 'classification',
                'model_version': -1,
                'input_map': {'image': 'preprocessed_image'},
                'output_map': {'probabilities': 'OUTPUT'}
            }
        ]

        Returns:
            Path to generated ensemble config
        """
        ensemble_dir = self.model_repository_path / ensemble_name
        ensemble_dir.mkdir(parents=True, exist_ok=True)

        config_lines = []

        config_lines.append(f'name: "{ensemble_name}"')
        config_lines.append('platform: "ensemble"')
        config_lines.append(f'max_batch_size: {max_batch_size}')
        config_lines.append('')

        # Ensemble scheduling
        config_lines.append('ensemble_scheduling {')

        for i, step in enumerate(pipeline_steps):
            config_lines.append('  step [')
            config_lines.append('    {')
            config_lines.append(f'      model_name: "{step["model_name"]}"')
            config_lines.append(f'      model_version: {step["model_version"]}')

            # Input mapping
            for internal_name, external_name in step['input_map'].items():
                config_lines.append('      input_map {')
                config_lines.append(f'        key: "{internal_name}"')
                config_lines.append(f'        value: "{external_name}"')
                config_lines.append('      }')

            # Output mapping
            for internal_name, external_name in step['output_map'].items():
                config_lines.append('      output_map {')
                config_lines.append(f'        key: "{internal_name}"')
                config_lines.append(f'        value: "{external_name}"')
                config_lines.append('      }')

            config_lines.append('    }')
            config_lines.append('  ]')

        config_lines.append('}')

        # Write config
        config_path = ensemble_dir / 'config.pbtxt'
        config_content = '\n'.join(config_lines)

        with open(config_path, 'w') as f:
            f.write(config_content)

        logger.info(f"Created ensemble config: {config_path}")

        return str(config_path)

    def create_version_directory(self, model_name: str, version: int) -> Path:
        """
        Create version directory for model files

        Args:
            model_name: Name of model
            version: Version number

        Returns:
            Path to version directory
        """
        version_dir = self.model_repository_path / model_name / str(version)
        version_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Created version directory: {version_dir}")

        return version_dir

    def list_models(self) -> List[str]:
        """List all models in repository"""
        models = []

        for item in self.model_repository_path.iterdir():
            if item.is_dir() and (item / 'config.pbtxt').exists():
                models.append(item.name)

        return sorted(models)

    def get_model_versions(self, model_name: str) -> List[int]:
        """Get all versions of a model"""
        model_dir = self.model_repository_path / model_name

        if not model_dir.exists():
            return []

        versions = []
        for item in model_dir.iterdir():
            if item.is_dir() and item.name.isdigit():
                versions.append(int(item.name))

        return sorted(versions)

    def generate_medical_imaging_config(
        self,
        model_name: str = "medical_imaging_classifier",
        image_size: int = 224,
        num_classes: int = 10
    ) -> str:
        """
        Generate configuration for medical imaging models

        Args:
            model_name: Model name
            image_size: Input image size
            num_classes: Number of output classes

        Returns:
            Path to config file
        """
        inputs = [
            ModelInput(
                name="input_image",
                data_type="TYPE_FP32",
                dims=[3, image_size, image_size]  # CHW format
            )
        ]

        outputs = [
            ModelOutput(
                name="probabilities",
                data_type="TYPE_FP32",
                dims=[num_classes]
            )
        ]

        return self.create_model_config(
            model_name=model_name,
            platform=Platform.PYTORCH,
            inputs=inputs,
            outputs=outputs,
            max_batch_size=16,
            instance_config=ModelInstance(count=2, kind=InstanceGroup.GPU),
            dynamic_batching=DynamicBatching(
                preferred_batch_size=[1, 2, 4, 8, 16],
                max_queue_delay_microseconds=500
            ),
            version_policy="latest",
            num_versions=3,
            enable_warmup=True
        )

    def generate_genomic_predictor_config(
        self,
        model_name: str = "genomic_variant_predictor",
        sequence_length: int = 1000,
        num_features: int = 4
    ) -> str:
        """
        Generate configuration for genomic prediction models

        Args:
            model_name: Model name
            sequence_length: DNA sequence length
            num_features: Number of input features (A, C, G, T)

        Returns:
            Path to config file
        """
        inputs = [
            ModelInput(
                name="sequence",
                data_type="TYPE_FP32",
                dims=[sequence_length, num_features]
            )
        ]

        outputs = [
            ModelOutput(
                name="pathogenicity_score",
                data_type="TYPE_FP32",
                dims=[1]
            ),
            ModelOutput(
                name="clinical_significance",
                data_type="TYPE_INT32",
                dims=[1]
            )
        ]

        return self.create_model_config(
            model_name=model_name,
            platform=Platform.TENSORFLOW,
            inputs=inputs,
            outputs=outputs,
            max_batch_size=32,
            instance_config=ModelInstance(count=1, kind=InstanceGroup.GPU),
            dynamic_batching=DynamicBatching(
                preferred_batch_size=[1, 4, 8, 16, 32],
                max_queue_delay_microseconds=1000
            ),
            version_policy="latest",
            num_versions=2
        )


if __name__ == "__main__":
    # Example usage
    config_manager = TritonModelConfig(model_repository_path="./model_repository")

    # Medical imaging model
    print("Creating medical imaging model config...")
    config_path = config_manager.generate_medical_imaging_config(
        model_name="chest_xray_classifier",
        image_size=224,
        num_classes=14  # 14 pathologies
    )
    print(f"Config created: {config_path}")

    # Genomic predictor model
    print("\nCreating genomic predictor config...")
    config_path = config_manager.generate_genomic_predictor_config(
        model_name="variant_pathogenicity_predictor",
        sequence_length=1000,
        num_features=4
    )
    print(f"Config created: {config_path}")

    # List models
    models = config_manager.list_models()
    print(f"\nModels in repository: {models}")

    print("\nTriton configuration manager ready")
