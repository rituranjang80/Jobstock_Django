from rest_framework.views import exception_handler
from App.utils.response import ApiException


def custom_exception_handler(exc, context):
    # If it's our ApiException, re-raise so middleware can handle it
    if isinstance(exc, ApiException):
        raise exc
    # Otherwise, use DRF's default handler
    return exception_handler(exc, context)
