from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'updates', views.LocationUpdateViewSet, basename='locationupdate')
router.register(r'zones', views.LocationZoneViewSet, basename='locationzone')
router.register(r'current', views.AssetLocationSummaryViewSet, basename='assetlocationsummary')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]

# Available endpoints:
# GET /api/locations/updates/ - List all location updates with filtering
# POST /api/locations/updates/ - Create new location update
# GET /api/locations/updates/{id}/ - Get specific location update
# PUT/PATCH /api/locations/updates/{id}/ - Update location update
# DELETE /api/locations/updates/{id}/ - Delete location update

# GET /api/locations/updates/latest/ - Get latest location for all assets
# POST /api/locations/updates/manual_entry/ - Create manual location entry
# POST /api/locations/updates/bulk_create/ - Bulk create location updates
# GET /api/locations/updates/asset/{asset_id}/ - Get location history for asset
# GET /api/locations/updates/stats/ - Get location tracking statistics

# GET /api/locations/zones/ - List all location zones
# POST /api/locations/zones/ - Create new zone
# GET /api/locations/zones/{id}/ - Get specific zone
# PUT/PATCH /api/locations/zones/{id}/ - Update zone
# DELETE /api/locations/zones/{id}/ - Delete zone
# GET /api/locations/zones/{id}/assets_in_zone/ - Get assets in zone
# POST /api/locations/zones/{id}/check_point/ - Check if point is in zone

# GET /api/locations/current/ - List current asset locations (read-only)
# GET /api/locations/current/{id}/ - Get specific asset current location
# GET /api/locations/current/map_data/ - Optimized data for map display