from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from App.services.setting_service import SettingService

class SettingListCreateAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all settings or create a new setting.",
        responses={200: openapi.Response('List of settings'), 201: openapi.Response('Created setting')},
        tags=['Settings']
    )
    def get(self, request):
        settings = SettingService.list_settings()
        return Response(settings, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new setting.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'key': openapi.Schema(type=openapi.TYPE_STRING, description='Setting key'),
                'value': openapi.Schema(type=openapi.TYPE_OBJECT, description='Setting value (JSON)'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description'),
            },
            required=['key', 'value']
        ),
        responses={201: openapi.Response('Created setting')},
        tags=['Settings']
    )
    def post(self, request):
        result = SettingService.create_setting(request.data)
        if isinstance(result, dict) and 'id' in result:
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

class SettingDetailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a setting by ID.",
        responses={200: openapi.Response('Setting detail'), 404: 'Not found'},
        tags=['Settings']
    )
    def get(self, request, setting_id):
        setting = SettingService.get_setting(setting_id)
        if not setting:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(setting, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a setting by ID.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'key': openapi.Schema(type=openapi.TYPE_STRING, description='Setting key'),
                'value': openapi.Schema(type=openapi.TYPE_OBJECT, description='Setting value (JSON)'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description'),
            }
        ),
        responses={200: openapi.Response('Updated setting'), 404: 'Not found'},
        tags=['Settings']
    )
    def put(self, request, setting_id):
        result = SettingService.update_setting(setting_id, request.data)
        if result is None:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        if isinstance(result, dict) and 'id' in result:
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a setting by ID.",
        responses={204: 'No content', 404: 'Not found'},
        tags=['Settings']
    )
    def delete(self, request, setting_id):
        success = SettingService.delete_setting(setting_id)
        if not success:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
