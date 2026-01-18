from rest_framework import serializers
from App.models import DropdownGroup, DropdownMaster

class DropdownMasterSchema(serializers.ModelSerializer):
    class Meta:
        model = DropdownMaster
        fields = ['id', 'label', 'value', 'is_active', 'sort_order']

class DropdownGroupSchema(serializers.ModelSerializer):
    items = DropdownMasterSchema(many=True, read_only=True)
    class Meta:
        model = DropdownGroup
        fields = ['id', 'label', 'value', 'is_active', 'items']
