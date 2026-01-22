"""
Custom exception handlers for API responses.
Provides consistent error responses across the API.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.

    Args:
        exc: The exception instance
        context: Context dictionary with 'view' and 'request' keys

    Returns:
        Response object with standardized error format
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize error response format
        custom_response_data = {
            "error": True,
            "status_code": response.status_code,
            "message": _get_error_message(response.data),
            "details": response.data
            if isinstance(response.data, dict)
            else {"detail": response.data},
        }
        response.data = custom_response_data
    else:
        # Handle unexpected errors
        logger.exception("Unhandled exception in API", exc_info=exc)
        response = Response(
            {
                "error": True,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred. Please try again later.",
                "details": {"detail": str(exc)},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _get_error_message(error_data):
    """
    Extract a human-readable error message from the error data.

    Args:
        error_data: Error data from DRF

    Returns:
        str: Human-readable error message
    """
    if isinstance(error_data, dict):
        # Try to get 'detail' or first error message
        if "detail" in error_data:
            return error_data["detail"]
        elif error_data:
            first_key = list(error_data.keys())[0]
            first_error = error_data[first_key]
            if isinstance(first_error, list) and first_error:
                return f"{first_key}: {first_error[0]}"
            return str(first_error)
    elif isinstance(error_data, list) and error_data:
        return error_data[0]

    return "An error occurred"
