from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StorageProviderViewSet

router = DefaultRouter()
router.register(r'providers', StorageProviderViewSet, basename='storage-provider')

urlpatterns = [
    path('', include(router.urls)),
]
