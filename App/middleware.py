"""
Error Logging Middleware for Django Application
Automatically captures and logs internal errors to the database.
Filters out library/framework errors to focus on application code.
"""

import logging
import sys
import traceback
import hashlib
import os
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse, HttpResponse
from django.utils import timezone


class ErrorLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log every request, every response, and all errors for Django/DRF APIs.
    Returns standardized JSON error responses for API requests.
    Generic, reusable, and distributable.
    """
    INTERNAL_PATHS = [
        'App/', 'Jobstock/', 'templates/',
    ]
    EXCLUDE_PATHS = [
        'site-packages/', 'lib/python', 'venv/', 'venv0/', 'django/', 'jazzmin/', 'celery/', 'rest_framework/', '__pycache__/',
    ]
    SENSITIVE_FIELDS = [
        'password', 'password1', 'password2', 'old_password', 'new_password', 'confirm_password', 'csrfmiddlewaretoken', 'token', 'api_key', 'secret', 'credit_card', 'cvv', 'ssn',
    ]

    def process_request(self, request):
        # Log every incoming request
        try:
            logger = logging.getLogger("restapi.request")
            request_data = self._get_safe_request_data(request)
            logger.info(f"API Request: {request.method} {request.path}", extra={
                "user": getattr(request, 'user', None),
                "data": request_data,
                "ip": self._get_client_ip(request),
            })
        except Exception as e:
            print(f"Request logging failed: {e}")
        return None

    def process_response(self, request, response):
        # Log every outgoing response
        try:
            logger = logging.getLogger("restapi.response")
            logger.info(f"API Response: {request.method} {request.path}", extra={
                "user": getattr(request, 'user', None),
                "status_code": getattr(response, 'status_code', None),
                "response": getattr(response, 'data', str(response)),
            })
            # Log all DB queries if in DEBUG mode
            from django.conf import settings
            if getattr(settings, 'DEBUG', False):
                try:
                    from django.db import connection
                    query_logger = logging.getLogger("restapi.dbqueries")
                    for q in connection.queries:
                        query_logger.info(f"SQL Query: {q.get('sql')} (Time: {q.get('time')})")
                except Exception as e:
                    print(f"DB query logging failed: {e}")
        except Exception as e:
            print(f"Response logging failed: {e}")
       #self.process_exception(request, response)
        return response

    def process_exception(self, request, exception):
        # Only insert error in database and return error object, no logging
        from App.utils.response import ApiException
        try:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # Collect all application frames (not libraries) in the traceback
            tb = exc_traceback
            app_stack = []
            internal_frame = None
            while tb is not None:
                frame = tb.tb_frame
                filename = frame.f_code.co_filename.replace('\\', '/').replace('\\', '/')
                is_internal = any(path in filename for path in self.INTERNAL_PATHS)
                is_excluded = any(path in filename for path in self.EXCLUDE_PATHS)
                if is_internal and not is_excluded:
                    app_stack.append({
                        'file_path': self._get_relative_path(filename),
                        'function_name': frame.f_code.co_name,
                        'line_number': frame.f_lineno
                    })
                    internal_frame = frame
                tb = tb.tb_next
            # Use the last application frame for main error location
            if app_stack:
                last_app = app_stack[-1]
                file_path = last_app['file_path']
                function_name = last_app['function_name']
                line_number = last_app['line_number']
            else:
                file_path = None
                function_name = None
                line_number = None
            error_hash = self._generate_error_hash(file_path, function_name, line_number, exc_type.__name__ if exc_type else "Unknown")
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            error_traceback = ''.join(tb_lines)
            request_data = self._get_safe_request_data(request)
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:2000]
            severity = self._determine_severity(exc_type)
            error_obj = None
            if app_stack:
                try:
                    from App.models import ErrorLog
                    existing_error = ErrorLog.objects.filter(error_hash=error_hash).first()
                    if existing_error:
                        existing_error.increment_occurrence()
                        error_obj = existing_error
                    else:
                        error_obj = ErrorLog.objects.create(
                            user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                            error_type=exc_type.__name__ if exc_type else "Unknown",
                            error_message=str(exc_value)[:5000],
                            error_traceback=error_traceback[:10000],
                            error_hash=error_hash,
                            file_path=file_path,
                            function_name=function_name,
                            line_number=line_number,
                            request_method=request.method,
                            request_path=request.path[:2000],
                            request_data=request_data,
                            ip_address=ip_address,
                            user_agent=user_agent,
                            status_code=501,
                            severity=severity,
                            environment=self._get_environment(),
                        )
                except Exception as e:
                    error_obj = {
                        "error": "Error logging to DB failed",
                        "details": str(e)
                    }
            # Return error object as JSON, including application call stack
            if request.path.startswith('/api/') or request.META.get('CONTENT_TYPE', '').startswith('application/json'):
                # If error_obj is a model instance, serialize its fields
                if hasattr(error_obj, 'id'):
                    # Extract all actual error messages if error_message is a dict
                    import re
                    raw_error = getattr(error_obj, "error_message", None)
                    def flatten_error_messages(err):
                        messages = []
                        if isinstance(err, dict):
                            for v in err.values():
                                if isinstance(v, list):
                                    for item in v:
                                        # If DRF ErrorDetail, get string
                                        msg = str(item)
                                        # Remove code info if present
                                        msg = re.sub(r"ErrorDetail\(string='(.*?)', code='.*?'\)", r"\1", msg)
                                        messages.append(msg)
                                else:
                                    messages.append(str(v))
                        elif isinstance(err, list):
                            for item in err:
                                messages.append(str(item))
                        elif err:
                            messages.append(str(err))
                        return messages
                    error_messages = flatten_error_messages(raw_error)
                    error_json = {
                        "success": False,
                        "error_id": getattr(error_obj, "id", None),
                        "error_type": getattr(error_obj, "error_type", None),
                        "error_message": raw_error,
                        "error_messages": error_messages,
                        "file_path": getattr(error_obj, "file_path", None),
                        "function_name": getattr(error_obj, "function_name", None),
                        "line_number": getattr(error_obj, "line_number", None),
                        "request_method": getattr(error_obj, "request_method", None),
                        "request_path": getattr(error_obj, "request_path", None),
                        "request_data":request_data if 'request_data' in locals() else getattr(error_obj, "request_data", None),
                        "ip_address": getattr(error_obj, "ip_address", None),
                        "user_agent": getattr(error_obj, "user_agent", None),
                        "status_code": getattr(error_obj, "status_code", None),
                        "severity": getattr(error_obj, "severity", None),
                        "environment": getattr(error_obj, "environment", None),
                        "app_call_stack": app_stack,
                        "error_traceback": getattr(error_obj, "error_traceback", None)
                    }
                else:
                    error_json = error_obj
                return JsonResponse(error_json, status=501)
        except Exception as e:
            return JsonResponse({"error": "Error logging middleware failed", "details": str(e)}, status=501)
        return None
    
    def _get_internal_frame(self, tb):
        """
        Extract the first frame from internal application code.
        Skip frames from libraries and framework code.
        """
        while tb is not None:
            frame = tb.tb_frame
            filename = frame.f_code.co_filename
            
            # Normalize path separators
            filename = filename.replace('\\', '/')
            
            # Check if this is internal code
            is_internal = any(path in filename for path in self.INTERNAL_PATHS)
            is_excluded = any(path in filename for path in self.EXCLUDE_PATHS)
            
            if is_internal and not is_excluded:
                return frame
            
            tb = tb.tb_next
        
        return None
    
    def _get_relative_path(self, absolute_path):
        """Get path relative to project root"""
        try:
            base_dir = str(settings.BASE_DIR)
            absolute_path = absolute_path.replace('\\', '/')
            base_dir = base_dir.replace('\\', '/')
            
            if absolute_path.startswith(base_dir):
                return absolute_path[len(base_dir):].lstrip('/')
            return absolute_path
        except:
            return absolute_path
    
    def _generate_error_hash(self, file_path, function_name, line_number, error_type):
        """Generate unique hash for error deduplication"""
        hash_string = f"{file_path}:{function_name}:{line_number}:{error_type}"
        return hashlib.sha256(hash_string.encode()).hexdigest()[:64]
    
    def _get_safe_request_data(self, request):
        """Get request data with sensitive fields filtered, including DRF request.data and JSON body"""
        data = {}
        try:
            # Get GET parameters
            if request.GET:
                data['GET'] = {
                    k: '***FILTERED***' if k.lower() in self.SENSITIVE_FIELDS else v
                    for k, v in request.GET.items()
                }
            # Get POST parameters
            if request.POST:
                data['POST'] = {
                    k: '***FILTERED***' if k.lower() in self.SENSITIVE_FIELDS else v
                    for k, v in request.POST.items()
                }
            # Get DRF request.data if available (for API views)
            drf_data = None
            if hasattr(request, 'data'):
                drf_data = request.data
                if isinstance(drf_data, dict):
                    filtered_drf = {
                        k: '***FILTERED***' if k.lower() in self.SENSITIVE_FIELDS else v
                        for k, v in drf_data.items()
                    }
                    data['DATA'] = filtered_drf
                else:
                    data['DATA'] = str(drf_data)
            # Get JSON body if present and not already captured
            if request.method in ['POST', 'PUT', 'PATCH'] and 'DATA' not in data:
                content_type = request.META.get('CONTENT_TYPE', '')
                if 'application/json' in content_type:
                    try:
                        import json
                        body_unicode = request.body.decode('utf-8')
                        if body_unicode:
                            json_data = json.loads(body_unicode)
                            filtered_json = {
                                k: '***FILTERED***' if k.lower() in self.SENSITIVE_FIELDS else v
                                for k, v in json_data.items()
                            }
                            data['JSON'] = filtered_json
                    except Exception:
                        data['JSON'] = {'_error': 'Could not parse JSON body'}
            # If no data found, mark as empty
            if not data:
                data = {'_empty': True}
            # Limit data size
            data_str = str(data)
            if len(data_str) > 5000:
                data = {'_truncated': True, 'size': len(data_str)}
        except Exception:
            data = {'_error': 'Could not extract request data'}
        return data
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _determine_severity(self, exc_type):
        """Determine error severity based on exception type"""
        critical_errors = [
            'DatabaseError',
            'OperationalError',
            'IntegrityError',
            'SystemError',
            'MemoryError',
        ]
        
        high_errors = [
            'ValueError',
            'KeyError',
            'AttributeError',
            'TypeError',
            'IndexError',
        ]
        
        low_errors = [
            'ValidationError',
            'PermissionDenied',
            'Http404',
        ]
        
        exc_name = exc_type.__name__
        
        if exc_name in critical_errors:
            return 'critical'
        elif exc_name in high_errors:
            return 'high'
        elif exc_name in low_errors:
            return 'low'
        else:
            return 'medium'
    
    def _get_environment(self):
        """Get current environment"""
        return 'production' if not settings.DEBUG else 'development'
