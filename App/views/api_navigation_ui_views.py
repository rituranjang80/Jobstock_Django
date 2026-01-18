from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from App.services_navigation_ui import NavigationUiService
from App.serializers_navigation_ui import NavigationUiGroupSerializer, NavigationUiItemSerializer

class NavigationUiGroupViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Auth"], responses={200: NavigationUiGroupSerializer(many=True)})
    def list(self, request):
        try:
            data = NavigationUiService.list_groups()
            return Response(data)
        except Exception as e:
            raise e

    @swagger_auto_schema(tags=["Auth"], responses={200: NavigationUiGroupSerializer()})
    def retrieve(self, request, pk=None):
        try:
            data = NavigationUiService.retrieve_group(pk)
            return Response(data)
        except Exception as e:
            raise e

    @swagger_auto_schema(tags=["Auth"], request_body=NavigationUiGroupSerializer, responses={201: NavigationUiGroupSerializer()})
    def create(self, request):
        try:
            data = NavigationUiService.create_group(request.data)
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise e

    @swagger_auto_schema(tags=["Auth"], request_body=NavigationUiGroupSerializer, responses={200: NavigationUiGroupSerializer()})
    def update(self, request, pk=None):
        try:
            data = NavigationUiService.update_group(pk, request.data)
            return Response(data)
        except Exception as e:
            raise e

    @swagger_auto_schema(tags=["Auth"], responses={204: 'No Content'})
    def destroy(self, request, pk=None):
        try:
            NavigationUiService.delete_group(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise e

class NavigationUiItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Auth"], responses={200: NavigationUiItemSerializer(many=True)})
    def list(self, request):
        try:
            data = NavigationUiService.list_items()
            return Response(data)
        except Exception as e:
            raise e

    @swagger_auto_schema(tags=["Auth"], responses={200: NavigationUiItemSerializer()})
    def retrieve(self, request, pk=None):
        try:
            data = NavigationUiService.retrieve_item(pk)
            return Response(data)
        except Exception as e:
            raise e

    @swagger_auto_schema(tags=["Auth"], request_body=NavigationUiItemSerializer, responses={201: NavigationUiItemSerializer()})
    def create(self, request):
        try:
            data = NavigationUiService.create_item(request.data)
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise e

    @swagger_auto_schema(tags=["Auth"], request_body=NavigationUiItemSerializer, responses={200: NavigationUiItemSerializer()})
    def update(self, request, pk=None):
        try:
            data = NavigationUiService.update_item(pk, request.data)
            return Response(data)
        except Exception as e:
            raise e

    @swagger_auto_schema(tags=["Auth"], responses={204: 'No Content'})
    def destroy(self, request, pk=None):
        try:
            NavigationUiService.delete_item(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise e
