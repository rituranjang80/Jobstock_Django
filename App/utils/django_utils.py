import jwt
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

def get_user_role_from_request(request):
    """
    Extract user role from JWT token in the request (Authorization header).
    Returns the role as a string, or None if not found/invalid.
    """
    auth = JWTAuthentication()
    header = auth.get_header(request)
    if header is None:
        return None
    raw_token = auth.get_raw_token(header)
    if raw_token is None:
        return None
    try:
        validated_token = auth.get_validated_token(raw_token)
        # Try to get role from token payload first
        role = validated_token.get('role', None)
        if role:
             return role
        # If not found, decode the JWT manually (handles both sliding and access tokens)
        try:
            payload = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=["HS256", "RS256"], options={"verify_aud": False})
            role = payload.get('role')
            if role:
                return role
        except Exception:
            pass
        # Fallback: get from user object
        user = auth.get_user(validated_token)
        return getattr(user, 'role', None)
    except (InvalidToken, TokenError, AttributeError):
        return None
from rest_framework.test import APIRequestFactory

def call_drf_post_view(view_class, url, data):
    """
    Generic function to call a DRF APIView's post method with data and return the response.
    Args:
        view_class: The APIView class (not instance), e.g., ZohoRefreshTokenAPIView
        url: The URL string (not used for routing, but required by factory)
        data: The POST data as a dict
    Returns:
        DRF Response object
    """
    factory = APIRequestFactory()
    request = factory.post(url, data, format='json')
    view = view_class.as_view()
    response = view(request)
    return response
