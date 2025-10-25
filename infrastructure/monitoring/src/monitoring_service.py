"""
Monitoring Service with Prometheus Metrics and Alerting

Features:
- Prometheus metrics collection
- Custom metrics for medical AI services
- Health check monitoring
- Alerting to Slack/PagerDuty
- Performance dashboards
"""

import os
import time
import requests
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    generate_latest, REGISTRY, CONTENT_TYPE_LATEST
)
from fastapi import Response
import asyncio

logger = logging.getLogger(__name__)


# ============================================================================
# Prometheus Metrics
# ============================================================================

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['service', 'method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['service', 'method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Model prediction metrics
model_predictions_total = Counter(
    'model_predictions_total',
    'Total model predictions',
    ['service', 'model_name', 'model_version', 'status']
)

model_prediction_duration_seconds = Histogram(
    'model_prediction_duration_seconds',
    'Model prediction duration in seconds',
    ['service', 'model_name'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

model_prediction_confidence = Histogram(
    'model_prediction_confidence',
    'Model prediction confidence scores',
    ['service', 'model_name'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
)

# Database metrics
db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections',
    ['service']
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['service', 'operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

# Authentication metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['service', 'method', 'status']
)

mfa_attempts_total = Counter(
    'mfa_attempts_total',
    'Total MFA attempts',
    ['service', 'status']
)

# PHI access metrics (HIPAA compliance)
phi_access_total = Counter(
    'phi_access_total',
    'Total PHI access events',
    ['service', 'user_role', 'resource_type']
)

# Error metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['service', 'error_type', 'severity']
)

# Service health metrics
service_health = Gauge(
    'service_health',
    'Service health status (1=healthy, 0=unhealthy)',
    ['service']
)

service_info = Info(
    'service',
    'Service information',
)


# ============================================================================
# Monitoring Service
# ============================================================================

class MonitoringService:
    """Service for monitoring and alerting"""

    def __init__(
        self,
        service_name: str,
        slack_webhook_url: str = None,
        pagerduty_api_key: str = None,
        alert_thresholds: Dict = None
    ):
        """
        Initialize monitoring service

        Args:
            service_name: Name of the service
            slack_webhook_url: Slack webhook URL for alerts
            pagerduty_api_key: PagerDuty API key
            alert_thresholds: Custom alert thresholds
        """
        self.service_name = service_name
        self.slack_webhook_url = slack_webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.pagerduty_api_key = pagerduty_api_key or os.getenv('PAGERDUTY_API_KEY')

        # Default alert thresholds
        self.alert_thresholds = alert_thresholds or {
            'error_rate_percent': 5.0,  # Alert if error rate > 5%
            'response_time_p95_seconds': 5.0,  # Alert if p95 response time > 5s
            'model_prediction_time_seconds': 30.0,  # Alert if prediction > 30s
            'failed_login_attempts_per_hour': 10,  # Alert if > 10 failed logins/hour
            'service_down_minutes': 5,  # Alert if service down > 5 min
        }

        # Alert state tracking
        self.alert_state = {}
        self.last_alert_time = {}

        # Set service info
        service_info.info({
            'service_name': service_name,
            'version': '1.0.0',
            'environment': os.getenv('ENVIRONMENT', 'production')
        })

    # ========================================================================
    # Metrics Recording
    # ========================================================================

    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_seconds: float
    ):
        """Record HTTP request metrics"""
        http_requests_total.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint,
            status=status_code
        ).inc()

        http_request_duration_seconds.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint
        ).observe(duration_seconds)

    def record_model_prediction(
        self,
        model_name: str,
        model_version: str,
        duration_seconds: float,
        confidence_score: float = None,
        status: str = 'success'
    ):
        """Record model prediction metrics"""
        model_predictions_total.labels(
            service=self.service_name,
            model_name=model_name,
            model_version=model_version,
            status=status
        ).inc()

        model_prediction_duration_seconds.labels(
            service=self.service_name,
            model_name=model_name
        ).observe(duration_seconds)

        if confidence_score is not None:
            model_prediction_confidence.labels(
                service=self.service_name,
                model_name=model_name
            ).observe(confidence_score)

    def record_db_query(self, operation: str, duration_seconds: float):
        """Record database query metrics"""
        db_query_duration_seconds.labels(
            service=self.service_name,
            operation=operation
        ).observe(duration_seconds)

    def record_auth_attempt(self, method: str, status: str):
        """Record authentication attempt"""
        auth_attempts_total.labels(
            service=self.service_name,
            method=method,
            status=status
        ).inc()

    def record_mfa_attempt(self, status: str):
        """Record MFA attempt"""
        mfa_attempts_total.labels(
            service=self.service_name,
            status=status
        ).inc()

    def record_phi_access(self, user_role: str, resource_type: str):
        """Record PHI access (HIPAA compliance)"""
        phi_access_total.labels(
            service=self.service_name,
            user_role=user_role,
            resource_type=resource_type
        ).inc()

    def record_error(self, error_type: str, severity: str = 'error'):
        """Record error"""
        errors_total.labels(
            service=self.service_name,
            error_type=error_type,
            severity=severity
        ).inc()

    def set_service_health(self, is_healthy: bool):
        """Set service health status"""
        service_health.labels(service=self.service_name).set(1 if is_healthy else 0)

    def set_active_db_connections(self, count: int):
        """Set active database connections count"""
        db_connections_active.labels(service=self.service_name).set(count)

    # ========================================================================
    # Health Checking
    # ========================================================================

    async def check_service_health(self, url: str, timeout: int = 5) -> bool:
        """
        Check if a service is healthy

        Args:
            url: Service health endpoint URL
            timeout: Request timeout in seconds

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {url}: {str(e)}")
            return False

    async def monitor_services(
        self,
        services: Dict[str, str],
        check_interval: int = 60
    ):
        """
        Continuously monitor service health

        Args:
            services: Dict of service_name -> health_check_url
            check_interval: Check interval in seconds
        """
        while True:
            for service_name, health_url in services.items():
                is_healthy = await self.check_service_health(health_url)
                service_health.labels(service=service_name).set(1 if is_healthy else 0)

                if not is_healthy:
                    await self.send_alert(
                        title=f"Service Down: {service_name}",
                        message=f"{service_name} health check failed at {health_url}",
                        severity="critical"
                    )

            await asyncio.sleep(check_interval)

    # ========================================================================
    # Alerting
    # ========================================================================

    async def send_slack_alert(self, title: str, message: str, severity: str = "warning"):
        """
        Send alert to Slack

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (info, warning, error, critical)
        """
        if not self.slack_webhook_url:
            logger.warning("Slack webhook URL not configured")
            return

        # Color coding based on severity
        colors = {
            'info': '#36a64f',      # Green
            'warning': '#ff9900',   # Orange
            'error': '#ff0000',     # Red
            'critical': '#8b0000'   # Dark red
        }

        payload = {
            "attachments": [
                {
                    "color": colors.get(severity, '#808080'),
                    "title": f"[{severity.upper()}] {title}",
                    "text": message,
                    "footer": f"{self.service_name}",
                    "ts": int(time.time())
                }
            ]
        }

        try:
            response = requests.post(self.slack_webhook_url, json=payload, timeout=5)
            if response.status_code != 200:
                logger.error(f"Failed to send Slack alert: {response.text}")
        except Exception as e:
            logger.error(f"Error sending Slack alert: {str(e)}")

    async def send_pagerduty_alert(self, title: str, message: str, severity: str = "error"):
        """
        Send alert to PagerDuty

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (info, warning, error, critical)
        """
        if not self.pagerduty_api_key:
            logger.warning("PagerDuty API key not configured")
            return

        # PagerDuty severity mapping
        pagerduty_severity = {
            'info': 'info',
            'warning': 'warning',
            'error': 'error',
            'critical': 'critical'
        }.get(severity, 'error')

        payload = {
            "routing_key": self.pagerduty_api_key,
            "event_action": "trigger",
            "payload": {
                "summary": title,
                "severity": pagerduty_severity,
                "source": self.service_name,
                "custom_details": {
                    "message": message
                }
            }
        }

        try:
            response = requests.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload,
                timeout=5
            )
            if response.status_code != 202:
                logger.error(f"Failed to send PagerDuty alert: {response.text}")
        except Exception as e:
            logger.error(f"Error sending PagerDuty alert: {str(e)}")

    async def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "warning",
        channels: List[str] = None
    ):
        """
        Send alert to configured channels

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            channels: List of channels ('slack', 'pagerduty')
        """
        if channels is None:
            channels = ['slack', 'pagerduty']

        # Prevent alert spam (max 1 alert per title per 5 minutes)
        alert_key = f"{title}_{severity}"
        now = datetime.utcnow()

        if alert_key in self.last_alert_time:
            time_since_last = (now - self.last_alert_time[alert_key]).total_seconds()
            if time_since_last < 300:  # 5 minutes
                logger.debug(f"Suppressing duplicate alert: {title}")
                return

        self.last_alert_time[alert_key] = now

        # Send to channels
        if 'slack' in channels:
            await self.send_slack_alert(title, message, severity)

        if 'pagerduty' in channels and severity in ['error', 'critical']:
            await self.send_pagerduty_alert(title, message, severity)

        logger.warning(f"ALERT [{severity}]: {title} - {message}")

    # ========================================================================
    # Metrics Endpoint
    # ========================================================================

    def get_metrics(self) -> Response:
        """
        Get Prometheus metrics

        Returns:
            FastAPI Response with Prometheus metrics
        """
        return Response(
            content=generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST
        )


# ============================================================================
# Monitoring Middleware (for FastAPI)
# ============================================================================

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically record HTTP request metrics"""

    def __init__(self, app, monitoring_service: MonitoringService):
        super().__init__(app)
        self.monitoring_service = monitoring_service

    async def dispatch(self, request: Request, call_next):
        """Record request metrics"""
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Record metrics
        self.monitoring_service.record_http_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration_seconds=duration
        )

        return response


# ============================================================================
# Context Managers for Metrics
# ============================================================================

from contextlib import contextmanager


@contextmanager
def track_prediction_time(monitoring_service: MonitoringService, model_name: str, model_version: str):
    """
    Context manager to track model prediction time

    Usage:
        with track_prediction_time(monitoring, "chest_xray_classifier", "v1.0"):
            predictions = model.predict(image)
    """
    start_time = time.time()
    success = True

    try:
        yield
    except Exception:
        success = False
        raise
    finally:
        duration = time.time() - start_time
        monitoring_service.record_model_prediction(
            model_name=model_name,
            model_version=model_version,
            duration_seconds=duration,
            status='success' if success else 'error'
        )


@contextmanager
def track_db_query(monitoring_service: MonitoringService, operation: str):
    """
    Context manager to track database query time

    Usage:
        with track_db_query(monitoring, "select_patient"):
            patient = db.query(Patient).filter(...).first()
    """
    start_time = time.time()

    try:
        yield
    finally:
        duration = time.time() - start_time
        monitoring_service.record_db_query(operation, duration)
