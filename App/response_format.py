"""
Reusable API response structure for all Django REST APIs in the project.
"""
from typing import Any, Optional, Dict
from django.http import JsonResponse


def api_response(
    data: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
    message: str = "",
    error_details: Any = None,
    more_error_details: Any = None,
    **kwargs
) -> JsonResponse:
    """
    Returns a standardized JSON response for all APIs.
    Args:
        data: Main data payload (dict or list)
        status_code: HTTP status code (default 200)
        message: Message string
        error_details: Error details (optional)
        more_error_details: More error details (optional)
        kwargs: Any extra fields to include in data
    Returns:
        JsonResponse with standard structure
    """
    response = {
        "status_code": status_code,
        "message": message,
        "error_details": error_details,
        "more_error_details": more_error_details,
        "data": data if data is not None else {},
    }
    return JsonResponse(response, status=status_code)
