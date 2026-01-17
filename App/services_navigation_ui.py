from App.repository_navigation_ui import NavigationUiRepository
from App.serializers_navigation_ui import NavigationUiGroupSerializer, NavigationUiItemSerializer

class NavigationUiService:
    @staticmethod
    def list_groups():
        groups = NavigationUiRepository.get_all_groups()
        return NavigationUiGroupSerializer(groups, many=True).data

    @staticmethod
    def retrieve_group(pk):
        group = NavigationUiRepository.get_group(pk)
        return NavigationUiGroupSerializer(group).data

    @staticmethod
    def create_group(data):
        group = NavigationUiRepository.create_group(data)
        return NavigationUiGroupSerializer(group).data

    @staticmethod
    def update_group(pk, data):
        group = NavigationUiRepository.update_group(pk, data)
        return NavigationUiGroupSerializer(group).data

    @staticmethod
    def delete_group(pk):
        NavigationUiRepository.delete_group(pk)

    @staticmethod
    def list_items():
        items = NavigationUiRepository.get_all_items()
        return NavigationUiItemSerializer(items, many=True).data

    @staticmethod
    def retrieve_item(pk):
        item = NavigationUiRepository.get_item(pk)
        return NavigationUiItemSerializer(item).data

    @staticmethod
    def create_item(data):
        item = NavigationUiRepository.create_item(data)
        return NavigationUiItemSerializer(item).data

    @staticmethod
    def update_item(pk, data):
        item = NavigationUiRepository.update_item(pk, data)
        return NavigationUiItemSerializer(item).data

    @staticmethod
    def delete_item(pk):
        NavigationUiRepository.delete_item(pk)
