from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CapitalPlanViewSet,
    CapitalPlanItemViewSet,
    CapitalPlanScenarioViewSet,
    AssetLifecycleViewSet,
    CapitalProjectViewSet
)

app_name = 'capital_planning'

router = DefaultRouter()
router.register(r'plans', CapitalPlanViewSet, basename='capitalplan')
router.register(r'items', CapitalPlanItemViewSet, basename='capitalplanitem')
router.register(r'scenarios', CapitalPlanScenarioViewSet, basename='capitalplanscenario')
router.register(r'asset-lifecycle', AssetLifecycleViewSet, basename='assetlifecycle')
router.register(r'projects', CapitalProjectViewSet, basename='capitalproject')

urlpatterns = [
    path('', include(router.urls)),
]