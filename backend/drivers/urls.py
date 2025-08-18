from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DriverViewSet,
    DriverCertificationViewSet,
    DriverAssetAssignmentViewSet,
    DriverViolationViewSet
)

router = DefaultRouter()
router.register(r'drivers', DriverViewSet)
router.register(r'certifications', DriverCertificationViewSet)
router.register(r'assignments', DriverAssetAssignmentViewSet)
router.register(r'violations', DriverViolationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]