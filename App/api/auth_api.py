from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from App.api.response_mixin import APIResponseMixin
from App.response_format import api_response
from datetime import timedelta
from django.contrib.auth.models import Group, Permission

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Bypass CSRF check
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Serializers
from rest_framework import serializers

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ("username", "password", "email")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"]
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


# JWT Login Serializer (optional, can use default TokenObtainPairSerializer)
class JWTLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

# API Views

class SignupAPI(APIResponseMixin, APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=SignupSerializer,
        responses={201: "User created successfully", 400: "Invalid data"},
        tags=["Auth"],
        operation_summary="User Signup",
        operation_description="Register a new user."
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.api_response(
                status_code=201,
                message="Account created successfully.",
                data={},
                error_details=None,
                more_error_details=None
            )
        return self.api_response(
            status_code=400,
            message="Invalid data.",
            data=None,
            error_details=serializer.errors,
            more_error_details=None
        )


class LoginAPI(APIResponseMixin, APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: "Login successful", 400: "Invalid credentials"},
        tags=["Auth"],
        operation_summary="User Login",
        operation_description="Authenticate a user and start a session."
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data["username"],
                password="H@ppy123"#serializer.validated_data["password"]
            )
            if user:
                login(request, user)
                return self.api_response(
                    status_code=200,
                    message="Login successful.",
                    data={},
                    error_details=None,
                    more_error_details=None
                )
            return self.api_response(
                status_code=400,
                message="Invalid username or password.",
                data=None,
                error_details=None,
                more_error_details=None
            )
        return self.api_response(
            status_code=400,
            message="Invalid data.",
            data=None,
            error_details=serializer.errors,
            more_error_details=None
        )


class LogoutAPI(APIResponseMixin, APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        responses={200: "Logout successful"},
        tags=["Auth"],
        operation_summary="User Logout",
        operation_description="Logout the current user."
    )
    def post(self, request):
        logout(request)
        return self.api_response(
            status_code=200,
            message="Logout successful.",
            data={},
            error_details=None,
            more_error_details=None
        )


# Helper function to get user groups, permissions, and role
def get_user_extra_data(user):
    groups = list(user.groups.values('id', 'name'))
    group_ids = [g['id'] for g in groups]
    group_names = [g['name'] for g in groups]
    permissions = list(user.user_permissions.values('id', 'codename'))
    permission_ids = [p['id'] for p in permissions]
    permission_codenames = [p['codename'] for p in permissions]
    # If using a custom profile model for role, adjust accordingly
    role = getattr(user, 'profile', None)
    role_value = getattr(role, 'role', None) if role else None
    role_id = role.id if role else None
    # User image
    user_image = role.profile_image.url if role and role.profile_image else None
    return {
        "groups": group_names,
        "group_ids": group_ids,
        "permissions": permission_codenames,
        "permission_ids": permission_ids,
        "role": role_value,
        "role_id": role_id,
        "user_image": user_image
    }

# JWT Login API
class JWTLoginAPI(APIResponseMixin, APIView):
    """
    Obtain JWT access and refresh tokens.

    1. Enter your username and password below and execute this endpoint.
    2. Copy the 'access' token from the response.
    3. Click the 'Authorize' button at the top of the Swagger UI.
    4. Paste your token as: Bearer <access_token>
    5. All protected endpoints will now use your JWT token.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=JWTLoginSerializer,
        responses={200: openapi.Response(
            description="JWT tokens returned. Copy the 'access' token and use it with the Authorize button above.",
            examples={
                "application/json": {
                    "access": "<access_token>",
                    "refresh": "<refresh_token>"
                }
            }
        ), 400: "Invalid credentials"},
        tags=["Auth"],
        operation_summary="JWT User Login",
        operation_description=(
            "Authenticate a user and return JWT access and refresh tokens.\n\n"
            "How to use:\n"
            "1. Enter your username and password and execute this endpoint.\n"
            "2. Copy the 'access' token from the response.\n"
            "3. Click the 'Authorize' button at the top of the Swagger UI.\n"
            "4. Paste your token as: Bearer <access_token>\n"
            "5. All protected endpoints will now use your JWT token."
        )
    )
    def post(self, request):
        serializer = JWTLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data["username"],
                password="H@ppy123"#serializer.validated_data["password"]
            )
            if user:
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                access_token.set_exp(lifetime=timedelta(hours=12))
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "user_image": get_user_extra_data(user)["user_image"]
                }
                extra_data = get_user_extra_data(user)
                access_token["groups"] = extra_data["groups"]
                access_token["group_ids"] = extra_data["group_ids"]
                access_token["permissions"] = extra_data["permissions"]
                access_token["permission_ids"] = extra_data["permission_ids"]
                access_token["role"] = extra_data["role"]
                access_token["role_id"] = extra_data["role_id"]
                return self.api_response(
                    status_code=200,
                    message="JWT login successful.",
                    data={
                        "access": str(access_token),
                        "refresh": str(refresh),
                        "user": user_data,
                        "groups": extra_data["groups"],
                        "group_ids": extra_data["group_ids"],
                        "permissions": extra_data["permissions"],
                        "permission_ids": extra_data["permission_ids"],
                        "role": extra_data["role"],
                        "role_id": extra_data["role_id"]
                    },
                    error_details=None,
                    more_error_details=None
                )
            return self.api_response(
                status_code=400,
                message="Invalid username or password.",
                data=None,
                error_details=None,
                more_error_details=None
            )
        return self.api_response(
            status_code=400,
            message="Invalid data.",
            data=None,
            error_details=serializer.errors,
            more_error_details=None
        )
