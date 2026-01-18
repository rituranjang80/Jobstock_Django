from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from App.serializers.dropdown_schema import DropdownMasterSchema
from App.services.dropdown_services import DropdownService
from App.api.response_mixin import APIResponseMixin

class DropdownListAPI(APIResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        operation_description="Get all active dropdown items for a group (cached in memory)",
        manual_parameters=[
            openapi.Parameter('group', openapi.IN_QUERY, description="Dropdown group text", type=openapi.TYPE_STRING, required=True),
        ],
        tags=['Dropdowns'],
        responses={200: DropdownMasterSchema(many=True)}
    )
    def get(self, request):
        group_text = request.GET.get('group')
        if not group_text:
            return self.api_response(
                status_code=400,
                message='Missing group parameter',
                data=None,
                error_details=None,
                more_error_details=None
            )
        items = DropdownService.get_dropdown_by_group(group_text)
        serializer = DropdownMasterSchema(items, many=True)
        return self.api_response(
            status_code=200,
            message='Dropdown items fetched successfully',
            data=serializer.data,
            error_details=None,
            more_error_details=None
        )
