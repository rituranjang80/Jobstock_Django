from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from App.models import DropdownGroup, DropdownMaster
from App.serializers.dropdown_schema import DropdownGroupSchema, DropdownMasterSchema
from App.api.viewset_response_mixin import APIViewSetResponseMixin


class DropdownGroupViewSet(APIViewSetResponseMixin, ModelViewSet):
    queryset = DropdownGroup.objects.all()
    serializer_class = DropdownGroupSchema
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Dropdowns']
    pagination_class = None

    @swagger_auto_schema(
        operation_description="List all dropdown groups with their items.",
        tags=['Dropdowns'],
        responses={200: DropdownGroupSchema(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class DropdownMasterViewSet(APIViewSetResponseMixin, ModelViewSet):
    queryset = DropdownMaster.objects.all()
    serializer_class = DropdownMasterSchema
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Dropdowns']

    @swagger_auto_schema(
        operation_description="List all dropdown items.",
        tags=['Dropdowns'],
        responses={200: DropdownMasterSchema(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
