"""
Generic Django REST API Error Handling Middleware
Reusable for any Django project. Logs all errors, modifies responses, and provides hooks for filtering and customizing error output.
"""
import logging
import traceback
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework.views import exception_handler
from rest_framework import status

logger = logging.getLogger("restapi.error")

class RestApiErrorMiddleware(MiddlewareMixin):
    """
    Middleware to catch, log, and format all errors in Django REST API requests.
    - Logs request, response, and error details
    - Handles validation, permission, and server errors
    - Allows filtering/modifying error responses
    """
    def process_exception(self, request, exception):
        # Build error context
        error_type = type(exception).__name__
        error_message = str(exception)
        tb = traceback.format_exc()
        request_data = getattr(request, 'data', None) or getattr(request, 'POST', None) or {}
        log_context = {
            "path": request.path,
            "method": request.method,
            "user": getattr(request, 'user', None),
            "data": request_data,
            "error_type": error_type,
            "error_message": error_message,
            "traceback": tb,
        }
        logger.error(f"REST API Error: {error_type}: {error_message}", extra=log_context)

        # Use DRF's exception handler for standard formatting
        drf_response = exception_handler(exception, None)
        if drf_response is not None:
            # Optionally filter/modify response here
            drf_response.data['error_type'] = error_type
            drf_response.data['error_message'] = error_message
            drf_response.data['request_path'] = request.path
            drf_response.data['request_method'] = request.method
            return drf_response
        # Fallback for non-DRF errors
        return JsonResponse({
            "success": False,
            "error_type": error_type,
            "error_message": error_message,
            "request_path": request.path,
            "request_method": request.method,
            "traceback": tb,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Usage:
# 1. Add 'restapi_error_middleware.RestApiErrorMiddleware' to MIDDLEWARE in settings.py
# 2. Works for all Django/DRF REST API endpoints
# 3. Logs errors to 'restapi.error' logger (configure handlers as needed)
# 4. Modify/filter error responses in process_exception as required
