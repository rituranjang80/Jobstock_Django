from App.response_format import api_response
from rest_framework.response import Response
import json

class APIResponseMixin:
    """
    Mixin to provide a generic, reusable API response for all API views.
    Use self.api_response() instead of DRF's Response directly.
    """
    def api_response(self, *, data=None, status_code=200, message="", error_details=None, more_error_details=None, **kwargs):
        # Use the project-wide api_response utility, but return as DRF Response
        resp = api_response(
            data=data,
            status_code=status_code,
            message=message,
            error_details=error_details,
            more_error_details=more_error_details,
            **kwargs
        )
        # api_response returns a Django JsonResponse, decode its content to dict
        content_dict = json.loads(resp.content.decode())
        return Response(content_dict, status=status_code)
