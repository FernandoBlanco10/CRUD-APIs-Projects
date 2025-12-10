"""
Custom error handlers and logging configuration.
"""
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from config.settings import settings
from models.song import ErrorResponse


class AppException(Exception):
    """
    Base application exception with error code and details.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "APPLICATION_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class NotFoundError(AppException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            message=f"{resource} with id '{resource_id}' not found",
            error_code="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "id": resource_id}
        )


class ConflictError(AppException):
    """Exception raised when there's a conflict with current state."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=details
        )


class DatabaseError(AppException):
    """Exception raised for database-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details
        )


def setup_logging(app: Flask) -> None:
    """
    Configure logging for the application.
    
    Args:
        app: Flask application instance
    """
    # Create logs directory
    import os
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure root logger
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format=settings.LOG_FORMAT,
        handlers=[
            logging.handlers.RotatingFileHandler(
                os.path.join(logs_dir, "app.log"),
                maxBytes=10485760,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    # Configure Flask logger
    app.logger.setLevel(log_level)
    
    # Log application startup
    app.logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    app.logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    app.logger.info(f"Debug mode: {settings.DEBUG}")
    app.logger.info(f"Database path: {settings.DATABASE_PATH}")


def register_error_handlers(app: Flask) -> None:
    """
    Register custom error handlers with the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(AppException)
    def handle_app_exception(e: AppException):
        """
        Handle custom application exceptions.
        
        Args:
            e: Application exception
            
        Returns:
            JSON response with error details
        """
        app.logger.error(
            f"App exception: {e.message}",
            extra={
                "error_code": e.error_code,
                "status_code": e.status_code,
                "details": e.details,
                "request_id": getattr(request, 'request_id', None)
            }
        )
        
        error_response = ErrorResponse(
            error=e.error_code,
            message=e.message,
            details=e.details
        )
        
        return jsonify(error_response.dict()), e.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        """
        Handle standard HTTP exceptions.
        
        Args:
            e: HTTP exception
            
        Returns:
            JSON response with error details
        """
        app.logger.warning(
            f"HTTP exception: {e.name} - {e.description}",
            extra={
                "status_code": e.code,
                "exception_type": type(e).__name__
            }
        )
        
        error_response = ErrorResponse(
            error=f"HTTP_{e.code}" if e.code else "HTTP_ERROR",
            message=e.description or e.name,
            details={"status_code": e.code}
        )
        
        return jsonify(error_response.dict()), e.code or 500
    
    @app.errorhandler(404)
    def handle_not_found(e):
        """
        Handle 404 Not Found errors.
        
        Args:
            e: 404 exception
            
        Returns:
            JSON response with error details
        """
        app.logger.warning(
            f"Resource not found: {request.path}",
            extra={"request_path": request.path, "method": request.method}
        )
        
        error_response = ErrorResponse(
            error="NOT_FOUND",
            message=f"Endpoint '{request.path}' not found",
            details={
                "path": request.path,
                "method": request.method,
                "available_endpoints": get_available_endpoints()
            }
        )
        
        return jsonify(error_response.dict()), 404
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        """
        Handle 500 Internal Server Error.
        
        Args:
            e: Internal server error
            
        Returns:
            JSON response with error details
        """
        app.logger.error(
            f"Internal server error: {str(e)}",
            exc_info=True,
            extra={"exception_type": type(e).__name__}
        )
        
        error_response = ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            details={"error_id": getattr(e, 'error_id', None)}
        )
        
        return jsonify(error_response.dict()), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_exception(e: Exception):
        """
        Handle unexpected exceptions.
        
        Args:
            e: Unexpected exception
            
        Returns:
            JSON response with error details
        """
        app.logger.error(
            f"Unexpected exception: {str(e)}",
            exc_info=True,
            extra={
                "exception_type": type(e).__name__,
                "exception_module": type(e).__module__
            }
        )
        
        error_response = ErrorResponse(
            error="UNEXPECTED_ERROR",
            message="An unexpected error occurred",
            details={
                "exception_type": type(e).__name__,
                "contact_support": True
            }
        )
        
        return jsonify(error_response.dict()), 500


def get_available_endpoints() -> Dict[str, list]:
    """
    Get list of available API endpoints.
    
    Returns:
        Dictionary mapping HTTP methods to endpoint lists
    """
    return {
        "GET": ["/", "/api/v1/songs", "/api/v1/songs/{id}", "/api/v1/stats"],
        "POST": ["/api/v1/songs"],
        "PUT": ["/api/v1/songs/{id}"],
        "DELETE": ["/api/v1/songs/{id}"]
    }


def log_request(request_data: Dict[str, Any]) -> None:
    """
    Log incoming request details.
    
    Args:
        request_data: Dictionary containing request information
    """
    logger = logging.getLogger(__name__)
    logger.info(
        "Request received",
        extra={
            "method": request_data.get("method"),
            "path": request_data.get("path"),
            "remote_addr": request_data.get("remote_addr"),
            "user_agent": request_data.get("user_agent"),
            "content_length": request_data.get("content_length"),
            "request_id": request_data.get("request_id")
        }
    )


def log_response(response_data: Dict[str, Any]) -> None:
    """
    Log outgoing response details.
    
    Args:
        response_data: Dictionary containing response information
    """
    logger = logging.getLogger(__name__)
    logger.info(
        "Response sent",
        extra={
            "status_code": response_data.get("status_code"),
            "content_type": response_data.get("content_type"),
            "content_length": response_data.get("content_length"),
            "duration_ms": response_data.get("duration_ms"),
            "request_id": response_data.get("request_id")
        }
    )


class RequestLogger:
    """
    Context manager for logging request duration and details.
    """
    
    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds() * 1000
            if exc_type:
                self.logger.error(
                    f"Request failed after {duration:.2f}ms",
                    extra={
                        "duration_ms": duration,
                        "exception_type": exc_type.__name__,
                        "success": False
                    }
                )
            else:
                self.logger.info(
                    f"Request completed in {duration:.2f}ms",
                    extra={
                        "duration_ms": duration,
                        "success": True
                    }
                )


def validate_json_content_type(request) -> None:
    """
    Validate that the request has the correct JSON content type.
    
    Args:
        request: Flask request object
        
    Raises:
        ValidationError: If content type is invalid
    """
    if request.method in ['POST', 'PUT', 'PATCH']:
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            raise ValidationError(
                "Content-Type must be application/json",
                details={"received_content_type": content_type}
            )


def sanitize_error_message(message: str) -> str:
    """
    Sanitize error messages to avoid exposing sensitive information.
    
    Args:
        message: Original error message
        
    Returns:
        Sanitized error message
    """
    # Remove potential sensitive information
    sensitive_patterns = [
        r'password[=\s:]\S+',
        r'token[=\s:]\S+',
        r'api_key[=\s:]\S+',
        r'secret[=\s:]\S+'
    ]
    
    import re
    sanitized = message
    for pattern in sensitive_patterns:
        sanitized = re.sub(pattern, '***', sanitized, flags=re.IGNORECASE)
    
    return sanitized