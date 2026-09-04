"""
Error handling and response models for the API
"""

from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Error type classifications"""
    VALIDATION_ERROR = "validation_error"
    FILE_ERROR = "file_error"
    AI_ERROR = "ai_error"
    API_ERROR = "api_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    INTERNAL_ERROR = "internal_error"
    NOT_FOUND_ERROR = "not_found_error"


class APIError(Exception):
    """Base API error class"""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.INTERNAL_ERROR,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        retryable: bool = False
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or {}
        self.retryable = retryable
        super().__init__(self.message)
        
        logger.error(
            f"API Error: {error_type} - {message}",
            extra={
                "error_type": error_type,
                "status_code": status_code,
                "retryable": retryable,
                "details": details
            }
        )


class ValidationError(APIError):
    """Validation error - client provided invalid input"""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message,
            error_type=ErrorType.VALIDATION_ERROR,
            status_code=400,
            details=details,
            retryable=False
        )


class FileError(APIError):
    """File processing error"""
    
    def __init__(self, message: str, details: Optional[Dict] = None, retryable: bool = False):
        super().__init__(
            message,
            error_type=ErrorType.FILE_ERROR,
            status_code=422,
            details=details,
            retryable=retryable
        )


class AIError(APIError):
    """AI service error"""
    
    def __init__(self, message: str, details: Optional[Dict] = None, retryable: bool = True):
        super().__init__(
            message,
            error_type=ErrorType.AI_ERROR,
            status_code=503,
            details=details,
            retryable=retryable
        )


class APIServiceError(APIError):
    """External API service error (OpenAI, Google Vision, etc.)"""
    
    def __init__(self, message: str, details: Optional[Dict] = None, retryable: bool = True):
        super().__init__(
            message,
            error_type=ErrorType.API_ERROR,
            status_code=502,
            details=details,
            retryable=retryable
        )


class TimeoutError(APIError):
    """Request timeout error"""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message,
            error_type=ErrorType.TIMEOUT_ERROR,
            status_code=504,
            details=details,
            retryable=True
        )


class RateLimitError(APIError):
    """Rate limit exceeded error"""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message,
            error_type=ErrorType.RATE_LIMIT_ERROR,
            status_code=429,
            details=details,
            retryable=True
        )


class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = False
    error: str
    error_type: ErrorType
    details: Optional[Dict[str, Any]] = None
    retryable: bool = False
    request_id: Optional[str] = None


class SuccessResponse(BaseModel):
    """Standard success response model"""
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


class SolveResponse(BaseModel):
    """Response model for problem solving"""
    success: bool
    solution: Optional[str] = None
    steps: Optional[list[str]] = None
    code: Optional[str] = None
    explanation: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    retryable: bool = False
    request_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat messages"""
    success: bool
    response: Optional[str] = None
    message_id: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    retryable: bool = False
    request_id: Optional[str] = None


def create_error_response(error: APIError, request_id: str = None) -> ErrorResponse:
    """Convert an APIError to an ErrorResponse"""
    return ErrorResponse(
        success=False,
        error=error.message,
        error_type=error.error_type,
        details=error.details,
        retryable=error.retryable,
        request_id=request_id
    )
