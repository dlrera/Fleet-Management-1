from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MaintenanceTypeViewSet, MaintenanceScheduleViewSet, MaintenanceRecordViewSet,
    MaintenancePartViewSet, MaintenancePartUsageViewSet
)

router = DefaultRouter()
router.register(r'maintenance-types', MaintenanceTypeViewSet)
router.register(r'schedules', MaintenanceScheduleViewSet)
router.register(r'records', MaintenanceRecordViewSet)
router.register(r'parts', MaintenancePartViewSet)
router.register(r'part-usage', MaintenancePartUsageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]