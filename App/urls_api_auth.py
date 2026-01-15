from django.urls import path
from App.api.auth_api import SignupAPI, LoginAPI, LogoutAPI,JWTLoginAPI

urlpatterns = [
    path('signup/', SignupAPI.as_view(), name='api_signup'),
    path('login/', LoginAPI.as_view(), name='api_login'),
    path('logout/', LogoutAPI.as_view(), name='api_logout'),
    path('api/auth/jwt-login/', JWTLoginAPI.as_view(), name='jwt-login'),
]


