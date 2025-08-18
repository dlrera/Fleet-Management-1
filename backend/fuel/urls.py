from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FuelTransactionViewSet, FuelSiteViewSet, FuelCardViewSet,
    FuelAlertViewSet, UnitsPolicyViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'transactions', FuelTransactionViewSet, basename='fuel-transactions')
router.register(r'sites', FuelSiteViewSet, basename='fuel-sites')
router.register(r'cards', FuelCardViewSet, basename='fuel-cards')
router.register(r'alerts', FuelAlertViewSet, basename='fuel-alerts')
router.register(r'policy', UnitsPolicyViewSet, basename='fuel-policy')

urlpatterns = [
    path('', include(router.urls)),
]