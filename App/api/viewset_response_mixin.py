from App.api.response_mixin import api_response
from rest_framework.response import Response

class APIViewSetResponseMixin:
    """
    Mixin for DRF ModelViewSet to standardize list/response output.
    """
    def finalize_response(self, request, response, *args, **kwargs):
        # Only wrap if not already in standard format
        if isinstance(response, Response) and not (isinstance(response.data, dict) and set(response.data.keys()) >= {"status_code", "message", "data", "error_details", "more_error_details"}):
            data = response.data
            status_code = response.status_code
            json_resp = api_response(
                data=data,
                status_code=status_code,
                message="Success" if status_code < 400 else "Error",
                error_details=None,
                more_error_details=None
            )
            # JsonResponse has .content (bytes), decode and load as dict
            import json
            response.data = json.loads(json_resp.content.decode())
        return super().finalize_response(request, response, *args, **kwargs)
