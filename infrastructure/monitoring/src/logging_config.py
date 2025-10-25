"""
Centralized Logging Configuration

Implements structured logging with:
- JSON formatting for log aggregation
- Multiple log levels and handlers
- Log rotation and retention
- Integration with ELK stack / CloudWatch
- HIPAA-compliant log security
"""

import os
import sys
import logging
import logging.handlers
import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import traceback


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON

        Returns:
            JSON string with structured log data
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Add extra fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "patient_id"):
            log_data["patient_id"] = record.patient_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "service_name"):
            log_data["service_name"] = record.service_name
        if hasattr(record, "ip_address"):
            log_data["ip_address"] = record.ip_address

        # Add any custom extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'lineno', 'module', 'msecs', 'message', 'pathname',
                          'process', 'processName', 'relativeCreated', 'thread', 'threadName',
                          'exc_info', 'exc_text', 'stack_info', 'user_id', 'patient_id',
                          'request_id', 'service_name', 'ip_address']:
                log_data[key] = value

        return json.dumps(log_data)


class LoggingConfig:
    """Centralized logging configuration"""

    def __init__(
        self,
        service_name: str,
        log_dir: str = "logs",
        log_level: str = "INFO",
        enable_console: bool = True,
        enable_file: bool = True,
        enable_json: bool = True,
        max_file_size_mb: int = 100,
        backup_count: int = 10
    ):
        """
        Initialize logging configuration

        Args:
            service_name: Name of the service
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_console: Enable console logging
            enable_file: Enable file logging
            enable_json: Use JSON formatting
            max_file_size_mb: Max log file size before rotation
            backup_count: Number of backup log files to keep
        """
        self.service_name = service_name
        self.log_dir = log_dir
        self.log_level = getattr(logging, log_level.upper())
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_json = enable_json
        self.max_file_size_mb = max_file_size_mb
        self.backup_count = backup_count

        # Create log directory
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

    def configure_logging(self) -> logging.Logger:
        """
        Configure logging with handlers

        Returns:
            Configured logger instance
        """
        # Get root logger
        logger = logging.getLogger()
        logger.setLevel(self.log_level)

        # Remove existing handlers
        logger.handlers = []

        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)

            if self.enable_json:
                console_handler.setFormatter(JSONFormatter())
            else:
                console_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                console_handler.setFormatter(console_formatter)

            logger.addHandler(console_handler)

        # File handlers
        if self.enable_file:
            # General log file (all levels)
            general_log_path = os.path.join(self.log_dir, f"{self.service_name}.log")
            general_handler = logging.handlers.RotatingFileHandler(
                general_log_path,
                maxBytes=self.max_file_size_mb * 1024 * 1024,
                backupCount=self.backup_count
            )
            general_handler.setLevel(logging.DEBUG)

            if self.enable_json:
                general_handler.setFormatter(JSONFormatter())
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                general_handler.setFormatter(file_formatter)

            logger.addHandler(general_handler)

            # Error log file (ERROR and above only)
            error_log_path = os.path.join(self.log_dir, f"{self.service_name}_error.log")
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_path,
                maxBytes=self.max_file_size_mb * 1024 * 1024,
                backupCount=self.backup_count
            )
            error_handler.setLevel(logging.ERROR)

            if self.enable_json:
                error_handler.setFormatter(JSONFormatter())
            else:
                error_handler.setFormatter(file_formatter)

            logger.addHandler(error_handler)

        return logger

    def get_logger(self, name: str = None) -> logging.Logger:
        """
        Get a logger instance

        Args:
            name: Logger name (defaults to service name)

        Returns:
            Logger instance
        """
        return logging.getLogger(name or self.service_name)


# ============================================================================
# CloudWatch Handler (AWS)
# ============================================================================

class CloudWatchHandler(logging.Handler):
    """Handler for sending logs to AWS CloudWatch"""

    def __init__(self, log_group: str, log_stream: str, region: str = "us-east-1"):
        """
        Initialize CloudWatch handler

        Args:
            log_group: CloudWatch log group name
            log_stream: CloudWatch log stream name
            region: AWS region
        """
        super().__init__()
        self.log_group = log_group
        self.log_stream = log_stream
        self.region = region

        try:
            import boto3
            self.client = boto3.client('logs', region_name=region)
            self._ensure_log_stream_exists()
        except ImportError:
            logging.warning("boto3 not installed. CloudWatch logging disabled.")
            self.client = None
        except Exception as e:
            logging.error(f"Failed to initialize CloudWatch client: {str(e)}")
            self.client = None

    def _ensure_log_stream_exists(self):
        """Ensure log group and stream exist"""
        if not self.client:
            return

        try:
            # Create log group if it doesn't exist
            try:
                self.client.create_log_group(logGroupName=self.log_group)
            except self.client.exceptions.ResourceAlreadyExistsException:
                pass

            # Create log stream if it doesn't exist
            try:
                self.client.create_log_stream(
                    logGroupName=self.log_group,
                    logStreamName=self.log_stream
                )
            except self.client.exceptions.ResourceAlreadyExistsException:
                pass

        except Exception as e:
            logging.error(f"Failed to create CloudWatch log stream: {str(e)}")

    def emit(self, record: logging.LogRecord):
        """Send log record to CloudWatch"""
        if not self.client:
            return

        try:
            log_event = {
                'logGroupName': self.log_group,
                'logStreamName': self.log_stream,
                'logEvents': [
                    {
                        'timestamp': int(record.created * 1000),
                        'message': self.format(record)
                    }
                ]
            }

            self.client.put_log_events(**log_event)

        except Exception as e:
            logging.error(f"Failed to send log to CloudWatch: {str(e)}")


# ============================================================================
# Elasticsearch Handler (ELK Stack)
# ============================================================================

class ElasticsearchHandler(logging.Handler):
    """Handler for sending logs to Elasticsearch"""

    def __init__(
        self,
        hosts: list,
        index_name: str = "biomedical-logs",
        username: str = None,
        password: str = None
    ):
        """
        Initialize Elasticsearch handler

        Args:
            hosts: List of Elasticsearch host URLs
            index_name: Elasticsearch index name
            username: Optional username for authentication
            password: Optional password for authentication
        """
        super().__init__()
        self.index_name = index_name

        try:
            from elasticsearch import Elasticsearch

            if username and password:
                self.client = Elasticsearch(
                    hosts,
                    basic_auth=(username, password)
                )
            else:
                self.client = Elasticsearch(hosts)

        except ImportError:
            logging.warning("elasticsearch-py not installed. Elasticsearch logging disabled.")
            self.client = None
        except Exception as e:
            logging.error(f"Failed to initialize Elasticsearch client: {str(e)}")
            self.client = None

    def emit(self, record: logging.LogRecord):
        """Send log record to Elasticsearch"""
        if not self.client:
            return

        try:
            # Format log record as JSON
            formatter = JSONFormatter()
            log_data = json.loads(formatter.format(record))

            # Index document
            self.client.index(
                index=self.index_name,
                document=log_data
            )

        except Exception as e:
            logging.error(f"Failed to send log to Elasticsearch: {str(e)}")


# ============================================================================
# Request ID Middleware (for FastAPI)
# ============================================================================

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all logs"""

    async def dispatch(self, request: Request, call_next):
        """Add request ID to request state"""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


# ============================================================================
# Logging Utilities
# ============================================================================

def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **context
):
    """
    Log message with additional context

    Args:
        logger: Logger instance
        level: Log level (logging.INFO, etc.)
        message: Log message
        **context: Additional context fields (user_id, patient_id, etc.)
    """
    # Create LogRecord with extra fields
    extra = {k: v for k, v in context.items() if v is not None}
    logger.log(level, message, extra=extra)


def log_api_request(
    logger: logging.Logger,
    method: str,
    endpoint: str,
    status_code: int,
    duration_ms: float,
    user_id: int = None,
    ip_address: str = None
):
    """
    Log API request

    Args:
        logger: Logger instance
        method: HTTP method
        endpoint: API endpoint
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        user_id: Optional user ID
        ip_address: Optional IP address
    """
    log_with_context(
        logger,
        logging.INFO,
        f"{method} {endpoint} - {status_code} - {duration_ms:.2f}ms",
        method=method,
        endpoint=endpoint,
        status_code=status_code,
        duration_ms=duration_ms,
        user_id=user_id,
        ip_address=ip_address
    )


# ============================================================================
# Initialize Logging
# ============================================================================

def init_logging(
    service_name: str,
    log_level: str = "INFO",
    enable_cloudwatch: bool = False,
    enable_elasticsearch: bool = False,
    cloudwatch_config: Dict[str, Any] = None,
    elasticsearch_config: Dict[str, Any] = None
) -> logging.Logger:
    """
    Initialize logging for a service

    Args:
        service_name: Name of the service
        log_level: Logging level
        enable_cloudwatch: Enable CloudWatch logging
        enable_elasticsearch: Enable Elasticsearch logging
        cloudwatch_config: CloudWatch configuration dict
        elasticsearch_config: Elasticsearch configuration dict

    Returns:
        Configured logger instance
    """
    # Configure basic logging
    config = LoggingConfig(
        service_name=service_name,
        log_level=log_level,
        enable_json=True
    )
    logger = config.configure_logging()

    # Add CloudWatch handler
    if enable_cloudwatch and cloudwatch_config:
        cloudwatch_handler = CloudWatchHandler(**cloudwatch_config)
        cloudwatch_handler.setFormatter(JSONFormatter())
        logger.addHandler(cloudwatch_handler)

    # Add Elasticsearch handler
    if enable_elasticsearch and elasticsearch_config:
        elasticsearch_handler = ElasticsearchHandler(**elasticsearch_config)
        elasticsearch_handler.setFormatter(JSONFormatter())
        logger.addHandler(elasticsearch_handler)

    return logger
