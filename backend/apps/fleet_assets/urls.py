from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, AssetViewSet, AssetDocumentViewSet, AssetImageViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'assets', AssetViewSet)
router.register(r'asset-documents', AssetDocumentViewSet)
router.register(r'asset-images', AssetImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]