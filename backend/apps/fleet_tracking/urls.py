from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LocationPointViewSet, LocationZoneViewSet, ZoneEventViewSet,
    RouteTemplateViewSet, TripViewSet
)

router = DefaultRouter()
router.register(r'location-points', LocationPointViewSet)
router.register(r'zones', LocationZoneViewSet)
router.register(r'zone-events', ZoneEventViewSet)
router.register(r'routes', RouteTemplateViewSet)
router.register(r'trips', TripViewSet)

urlpatterns = [
    path('', include(router.urls)),
]