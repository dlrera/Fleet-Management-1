from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, AssetDocumentViewSet

router = DefaultRouter()
router.register(r'assets', AssetViewSet)
router.register(r'documents', AssetDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]