from rest_framework.routers import DefaultRouter
from App.views.api_navigation_ui_views import NavigationUiGroupViewSet, NavigationUiItemViewSet

router = DefaultRouter()
router.register(r'navigation-ui-groups', NavigationUiGroupViewSet, basename='navigation-ui-group')
router.register(r'navigation-ui-items', NavigationUiItemViewSet, basename='navigation-ui-item')

urlpatterns = router.urls
