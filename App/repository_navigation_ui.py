from App.models_navigation_ui import NavigationUiGroup, NavigationUiItem
from django.db import transaction

class NavigationUiRepository:
    @staticmethod
    def get_all_groups():
        return NavigationUiGroup.objects.prefetch_related('items').all()

    @staticmethod
    def get_group(pk):
        return NavigationUiGroup.objects.prefetch_related('items').get(pk=pk)

    @staticmethod
    def create_group(data):
        return NavigationUiGroup.objects.create(**data)

    @staticmethod
    def update_group(pk, data):
        group = NavigationUiGroup.objects.get(pk=pk)
        for key, value in data.items():
            setattr(group, key, value)
        group.save()
        return group

    @staticmethod
    def delete_group(pk):
        NavigationUiGroup.objects.filter(pk=pk).delete()

    @staticmethod
    def get_all_items():
        return NavigationUiItem.objects.all()

    @staticmethod
    def get_item(pk):
        return NavigationUiItem.objects.get(pk=pk)

    @staticmethod
    def create_item(data):
        return NavigationUiItem.objects.create(**data)

    @staticmethod
    def update_item(pk, data):
        item = NavigationUiItem.objects.get(pk=pk)
        for key, value in data.items():
            setattr(item, key, value)
        item.save()
        return item

    @staticmethod
    def delete_item(pk):
        NavigationUiItem.objects.filter(pk=pk).delete()
