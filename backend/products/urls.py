from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SUKMasterViewSet, InventoryViewSet

router = DefaultRouter()
router.register('suks', SUKMasterViewSet)
router.register('inventory', InventoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
