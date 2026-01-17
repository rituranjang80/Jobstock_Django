from rest_framework import serializers
from App.models_navigation_ui import NavigationUiGroup, NavigationUiItem

class NavigationUiItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = NavigationUiItem
        fields = '__all__'

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return NavigationUiItemSerializer(children, many=True).data

class NavigationUiGroupSerializer(serializers.ModelSerializer):
    items = NavigationUiItemSerializer(many=True, read_only=True)

    class Meta:
        model = NavigationUiGroup
        fields = '__all__'
