from App.api.response_mixin import APIResponseMixin
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
        settings = SettingService.get_all_settings()
        return self.api_response(
            status_code=200,
            message="Settings fetched successfully",
            data=settings
        )

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
        return self.api_response(
            status_code=201 if result.get('success') else 400,
            message=result.get('message', ''),
            data=result.get('data'),
            error_details=result.get('errors'),
            more_error_details=None
        )

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
            return self.api_response(
                status_code=404,
                message='Not found',
                data=None
            )
        return self.api_response(
            status_code=200,
            message='Setting fetched successfully',
            data=setting
        )

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
        if not result['success']:
            return self.api_response(
                status_code=404,
                message='Not found',
                data=None
            )
        return self.api_response(
            status_code=200,
            message=result.get('message', ''),
            data=result.get('data'),
            error_details=result.get('errors'),
            more_error_details=None
        )

    @swagger_auto_schema(
        operation_description="Delete a setting by ID.",
        responses={204: 'No content', 404: 'Not found'},
        tags=['Settings']
    )
    def delete(self, request, setting_id):
        result = SettingService.delete_setting(setting_id)
        if not result['success']:
            return self.api_response(
                status_code=404,
                message='Not found',
                data=None
            )
        return self.api_response(
            status_code=204,
            message='Setting deleted successfully',
            data=None
        )
