from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DriverViewSet, DriverCertificationViewSet, DriverIncidentViewSet, DriverTrainingViewSet
)

router = DefaultRouter()
router.register(r'drivers', DriverViewSet)
router.register(r'certifications', DriverCertificationViewSet)
router.register(r'incidents', DriverIncidentViewSet)
router.register(r'training', DriverTrainingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]