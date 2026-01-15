from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
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

class SignupAPI(APIView):
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
            return Response({"message": "Account created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(APIView):
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
                password=serializer.validated_data["password"]
            )
            if user:
                login(request, user)
                return Response({"message": "Login successful."}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPI(APIView):
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
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)


# JWT Login API
class JWTLoginAPI(APIView):
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
                password=serializer.validated_data["password"]
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
