"""
GPU Resource Scheduler
Manages GPU allocation and scheduling for ML model inference
"""

import logging
import subprocess
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPUStatus(Enum):
    """GPU availability status"""
    AVAILABLE = "available"
    IN_USE = "in_use"
    RESERVED = "reserved"
    OFFLINE = "offline"


class SchedulingStrategy(Enum):
    """GPU scheduling strategies"""
    FIRST_FIT = "first_fit"  # Assign to first available GPU
    BEST_FIT = "best_fit"    # Assign to GPU with most free memory
    ROUND_ROBIN = "round_robin"  # Distribute evenly
    LEAST_LOADED = "least_loaded"  # GPU with lowest utilization


class GPUScheduler:
    """
    GPU Resource Scheduler for ML inference

    Features:
    - GPU discovery and monitoring
    - Dynamic GPU allocation
    - Load balancing across GPUs
    - Resource quota management
    - Performance monitoring
    """

    def __init__(
        self,
        scheduling_strategy: SchedulingStrategy = SchedulingStrategy.LEAST_LOADED,
        enable_mps: bool = False  # CUDA Multi-Process Service
    ):
        """
        Initialize GPU scheduler

        Args:
            scheduling_strategy: Strategy for GPU allocation
            enable_mps: Enable CUDA MPS for GPU sharing
        """
        self.scheduling_strategy = scheduling_strategy
        self.enable_mps = enable_mps

        # GPU assignments
        self.gpu_assignments: Dict[int, List[str]] = {}  # gpu_id -> [model_names]
        self.model_allocations: Dict[str, int] = {}  # model_name -> gpu_id

        # Round-robin counter
        self.round_robin_counter = 0

        # Discover available GPUs
        self.gpus = self._discover_gpus()

        logger.info(f"GPU Scheduler initialized: {len(self.gpus)} GPUs found")
        logger.info(f"Strategy: {scheduling_strategy.value}")

    # ==================== GPU DISCOVERY ====================

    def _discover_gpus(self) -> List[Dict]:
        """
        Discover available GPUs using nvidia-smi

        Returns:
            List of GPU information dictionaries
        """
        try:
            # Run nvidia-smi
            result = subprocess.run(
                [
                    'nvidia-smi',
                    '--query-gpu=index,name,memory.total,memory.free,memory.used,utilization.gpu,temperature.gpu,power.draw',
                    '--format=csv,noheader,nounits'
                ],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.warning("nvidia-smi command failed - no GPUs available")
                return []

            gpus = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = [p.strip() for p in line.split(',')]

                if len(parts) >= 8:
                    gpu_info = {
                        'gpu_id': int(parts[0]),
                        'name': parts[1],
                        'memory_total_mb': int(parts[2]),
                        'memory_free_mb': int(parts[3]),
                        'memory_used_mb': int(parts[4]),
                        'utilization_percent': int(parts[5]) if parts[5] != '[N/A]' else 0,
                        'temperature_c': int(parts[6]) if parts[6] != '[N/A]' else 0,
                        'power_draw_w': float(parts[7]) if parts[7] != '[N/A]' else 0.0,
                        'status': GPUStatus.AVAILABLE.value,
                        'assigned_models': []
                    }

                    gpus.append(gpu_info)
                    self.gpu_assignments[gpu_info['gpu_id']] = []

            logger.info(f"Discovered {len(gpus)} GPUs")

            return gpus

        except FileNotFoundError:
            logger.warning("nvidia-smi not found - running in CPU-only mode")
            return []
        except Exception as e:
            logger.error(f"GPU discovery failed: {str(e)}")
            return []

    def get_gpu_stats(self) -> List[Dict]:
        """
        Get current GPU statistics

        Returns:
            Updated list of GPU info
        """
        return self._discover_gpus()

    # ==================== GPU ALLOCATION ====================

    def allocate_gpu(
        self,
        model_name: str,
        memory_required_mb: Optional[int] = None,
        prefer_gpu_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Allocate GPU for model

        Args:
            model_name: Model identifier
            memory_required_mb: Required GPU memory (MB)
            prefer_gpu_id: Preferred GPU ID

        Returns:
            Allocated GPU ID or None if no GPU available
        """
        if not self.gpus:
            logger.warning("No GPUs available - falling back to CPU")
            return None

        # Check if model already allocated
        if model_name in self.model_allocations:
            existing_gpu = self.model_allocations[model_name]
            logger.info(f"Model {model_name} already on GPU {existing_gpu}")
            return existing_gpu

        # Get current GPU stats
        gpu_stats = self.get_gpu_stats()

        # Filter by preferred GPU
        if prefer_gpu_id is not None:
            gpu_stats = [g for g in gpu_stats if g['gpu_id'] == prefer_gpu_id]
            if not gpu_stats:
                logger.warning(f"Preferred GPU {prefer_gpu_id} not available")
                gpu_stats = self.gpus

        # Filter by memory requirement
        if memory_required_mb:
            gpu_stats = [g for g in gpu_stats if g['memory_free_mb'] >= memory_required_mb]

        if not gpu_stats:
            logger.error("No GPU with sufficient memory available")
            return None

        # Select GPU based on strategy
        selected_gpu = self._select_gpu(gpu_stats)

        if selected_gpu:
            gpu_id = selected_gpu['gpu_id']

            # Record allocation
            self.gpu_assignments[gpu_id].append(model_name)
            self.model_allocations[model_name] = gpu_id

            logger.info(f"Allocated GPU {gpu_id} for {model_name}")
            logger.info(f"GPU {gpu_id} memory: {selected_gpu['memory_free_mb']}MB free / {selected_gpu['memory_total_mb']}MB total")

            return gpu_id

        return None

    def _select_gpu(self, available_gpus: List[Dict]) -> Optional[Dict]:
        """
        Select GPU based on scheduling strategy

        Args:
            available_gpus: List of available GPUs

        Returns:
            Selected GPU info
        """
        if not available_gpus:
            return None

        strategy = self.scheduling_strategy

        if strategy == SchedulingStrategy.FIRST_FIT:
            # First available GPU
            return available_gpus[0]

        elif strategy == SchedulingStrategy.BEST_FIT:
            # GPU with most free memory
            return max(available_gpus, key=lambda g: g['memory_free_mb'])

        elif strategy == SchedulingStrategy.ROUND_ROBIN:
            # Distribute evenly
            selected = available_gpus[self.round_robin_counter % len(available_gpus)]
            self.round_robin_counter += 1
            return selected

        elif strategy == SchedulingStrategy.LEAST_LOADED:
            # GPU with lowest utilization
            return min(available_gpus, key=lambda g: g['utilization_percent'])

        else:
            return available_gpus[0]

    def deallocate_gpu(self, model_name: str) -> bool:
        """
        Deallocate GPU for model

        Args:
            model_name: Model identifier

        Returns:
            Success status
        """
        if model_name not in self.model_allocations:
            logger.warning(f"Model {model_name} not allocated")
            return False

        gpu_id = self.model_allocations[model_name]

        # Remove allocation
        if model_name in self.gpu_assignments[gpu_id]:
            self.gpu_assignments[gpu_id].remove(model_name)

        del self.model_allocations[model_name]

        logger.info(f"Deallocated GPU {gpu_id} from {model_name}")

        return True

    # ==================== RESOURCE MONITORING ====================

    def get_gpu_utilization(self, gpu_id: int) -> Optional[Dict]:
        """
        Get detailed utilization for specific GPU

        Args:
            gpu_id: GPU identifier

        Returns:
            Utilization statistics
        """
        gpu_stats = self.get_gpu_stats()

        for gpu in gpu_stats:
            if gpu['gpu_id'] == gpu_id:
                return {
                    'gpu_id': gpu_id,
                    'memory_utilization_percent': (gpu['memory_used_mb'] / gpu['memory_total_mb'] * 100) if gpu['memory_total_mb'] > 0 else 0,
                    'compute_utilization_percent': gpu['utilization_percent'],
                    'memory_free_mb': gpu['memory_free_mb'],
                    'memory_used_mb': gpu['memory_used_mb'],
                    'memory_total_mb': gpu['memory_total_mb'],
                    'temperature_c': gpu['temperature_c'],
                    'power_draw_w': gpu['power_draw_w'],
                    'assigned_models': self.gpu_assignments.get(gpu_id, []),
                    'model_count': len(self.gpu_assignments.get(gpu_id, []))
                }

        return None

    def get_cluster_utilization(self) -> Dict:
        """
        Get overall cluster utilization

        Returns:
            Cluster-wide statistics
        """
        gpu_stats = self.get_gpu_stats()

        if not gpu_stats:
            return {
                'total_gpus': 0,
                'available_gpus': 0,
                'total_memory_mb': 0,
                'used_memory_mb': 0,
                'free_memory_mb': 0,
                'avg_utilization_percent': 0,
                'total_models': 0
            }

        total_memory = sum(g['memory_total_mb'] for g in gpu_stats)
        used_memory = sum(g['memory_used_mb'] for g in gpu_stats)
        free_memory = sum(g['memory_free_mb'] for g in gpu_stats)
        avg_util = sum(g['utilization_percent'] for g in gpu_stats) / len(gpu_stats)

        available_count = len([g for g in gpu_stats if g['memory_free_mb'] > 1000])  # >1GB free

        return {
            'total_gpus': len(gpu_stats),
            'available_gpus': available_count,
            'total_memory_mb': total_memory,
            'used_memory_mb': used_memory,
            'free_memory_mb': free_memory,
            'memory_utilization_percent': (used_memory / total_memory * 100) if total_memory > 0 else 0,
            'avg_compute_utilization_percent': avg_util,
            'total_models': sum(len(models) for models in self.gpu_assignments.values()),
            'models_per_gpu': {gpu_id: len(models) for gpu_id, models in self.gpu_assignments.items()}
        }

    # ==================== LOAD BALANCING ====================

    def rebalance_gpus(self) -> Dict:
        """
        Rebalance models across GPUs to optimize utilization

        Returns:
            Rebalancing report
        """
        logger.info("Starting GPU rebalancing...")

        gpu_stats = self.get_gpu_stats()

        if not gpu_stats or len(gpu_stats) < 2:
            return {'message': 'Not enough GPUs for rebalancing'}

        # Calculate current load distribution
        current_load = {
            g['gpu_id']: {
                'model_count': len(self.gpu_assignments.get(g['gpu_id'], [])),
                'utilization': g['utilization_percent']
            }
            for g in gpu_stats
        }

        # Find overloaded and underloaded GPUs
        avg_models_per_gpu = sum(len(models) for models in self.gpu_assignments.values()) / len(gpu_stats)

        overloaded = [(gpu_id, info) for gpu_id, info in current_load.items() if info['model_count'] > avg_models_per_gpu * 1.5]
        underloaded = [(gpu_id, info) for gpu_id, info in current_load.items() if info['model_count'] < avg_models_per_gpu * 0.5]

        migrations = []

        # Move models from overloaded to underloaded GPUs
        for over_gpu_id, over_info in overloaded:
            for under_gpu_id, under_info in underloaded:
                if self.gpu_assignments[over_gpu_id]:
                    # Move one model
                    model_to_move = self.gpu_assignments[over_gpu_id].pop()

                    # Update allocations
                    self.gpu_assignments[under_gpu_id].append(model_to_move)
                    self.model_allocations[model_to_move] = under_gpu_id

                    migrations.append({
                        'model': model_to_move,
                        'from_gpu': over_gpu_id,
                        'to_gpu': under_gpu_id
                    })

                    logger.info(f"Migrated {model_to_move}: GPU {over_gpu_id} → GPU {under_gpu_id}")

                    break

        return {
            'migrations_performed': len(migrations),
            'migrations': migrations,
            'new_distribution': {gpu_id: len(models) for gpu_id, models in self.gpu_assignments.items()}
        }

    # ==================== HEALTH MONITORING ====================

    def check_gpu_health(self) -> Dict:
        """
        Check GPU health status

        Returns:
            Health report
        """
        gpu_stats = self.get_gpu_stats()

        issues = []

        for gpu in gpu_stats:
            gpu_id = gpu['gpu_id']

            # Temperature check
            if gpu['temperature_c'] > 85:
                issues.append({
                    'gpu_id': gpu_id,
                    'severity': 'warning',
                    'issue': 'high_temperature',
                    'value': gpu['temperature_c'],
                    'threshold': 85
                })

            # Memory check
            memory_util = (gpu['memory_used_mb'] / gpu['memory_total_mb'] * 100) if gpu['memory_total_mb'] > 0 else 0
            if memory_util > 95:
                issues.append({
                    'gpu_id': gpu_id,
                    'severity': 'critical',
                    'issue': 'memory_exhaustion',
                    'value': memory_util,
                    'threshold': 95
                })

            # Utilization check (potential underutilization)
            if gpu['utilization_percent'] < 10 and len(self.gpu_assignments.get(gpu_id, [])) > 0:
                issues.append({
                    'gpu_id': gpu_id,
                    'severity': 'info',
                    'issue': 'low_utilization',
                    'value': gpu['utilization_percent'],
                    'threshold': 10
                })

        health_status = 'healthy' if not issues else 'degraded' if all(i['severity'] != 'critical' for i in issues) else 'unhealthy'

        return {
            'status': health_status,
            'timestamp': datetime.utcnow().isoformat(),
            'total_gpus': len(gpu_stats),
            'issues_found': len(issues),
            'issues': issues
        }

    # ==================== CONFIGURATION ====================

    def get_model_allocation(self, model_name: str) -> Optional[int]:
        """Get GPU ID for model"""
        return self.model_allocations.get(model_name)

    def list_gpu_assignments(self) -> Dict[int, List[str]]:
        """List all GPU assignments"""
        return self.gpu_assignments.copy()


if __name__ == "__main__":
    # Example usage
    scheduler = GPUScheduler(scheduling_strategy=SchedulingStrategy.LEAST_LOADED)

    print(f"GPUs available: {len(scheduler.gpus)}")

    if scheduler.gpus:
        # Allocate GPU for models
        gpu_id = scheduler.allocate_gpu("chest_xray_classifier", memory_required_mb=4000)
        print(f"Allocated GPU {gpu_id} for chest_xray_classifier")

        gpu_id = scheduler.allocate_gpu("genomic_predictor", memory_required_mb=2000)
        print(f"Allocated GPU {gpu_id} for genomic_predictor")

        # Get cluster utilization
        cluster_stats = scheduler.get_cluster_utilization()
        print(f"\nCluster utilization: {cluster_stats['avg_compute_utilization_percent']:.1f}%")
        print(f"Memory used: {cluster_stats['used_memory_mb']}/{cluster_stats['total_memory_mb']} MB")

        # Check health
        health = scheduler.check_gpu_health()
        print(f"\nHealth status: {health['status']}")
        print(f"Issues found: {health['issues_found']}")

    print("\nGPU Scheduler ready")
