"""
API URL Configuration for Fleet Management System
This file centralizes all API endpoints for the fleet management system.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Import app-specific routers if needed for custom configurations
# from apps.fleet_assets.views import AssetViewSet


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_root(request, format=None):
    """
    API Root endpoint that provides navigation to all available endpoints
    """
    return Response({
        'message': 'Fleet Management System API',
        'version': '1.0',
        'authentication': {
            'obtain_token': request.build_absolute_uri('/api/auth/token/'),
            'note': 'Include token in header: Authorization: Token <your-token>'
        },
        'endpoints': {
            'assets': {
                'departments': request.build_absolute_uri('/api/assets/departments/'),
                'assets': request.build_absolute_uri('/api/assets/assets/'),
                'asset_documents': request.build_absolute_uri('/api/assets/asset-documents/'),
                'asset_images': request.build_absolute_uri('/api/assets/asset-images/'),
            },
            'drivers': {
                'drivers': request.build_absolute_uri('/api/drivers/drivers/'),
                'certifications': request.build_absolute_uri('/api/drivers/certifications/'),
                'incidents': request.build_absolute_uri('/api/drivers/incidents/'),
                'training': request.build_absolute_uri('/api/drivers/training/'),
            },
            'maintenance': {
                'maintenance_types': request.build_absolute_uri('/api/maintenance/maintenance-types/'),
                'schedules': request.build_absolute_uri('/api/maintenance/schedules/'),
                'records': request.build_absolute_uri('/api/maintenance/records/'),
                'parts': request.build_absolute_uri('/api/maintenance/parts/'),
                'part_usage': request.build_absolute_uri('/api/maintenance/part-usage/'),
            },
            'work_orders': {
                'work_orders': request.build_absolute_uri('/api/work-orders/work-orders/'),
                'photos': request.build_absolute_uri('/api/work-orders/photos/'),
                'documents': request.build_absolute_uri('/api/work-orders/documents/'),
                'comments': request.build_absolute_uri('/api/work-orders/comments/'),
                'checklists': request.build_absolute_uri('/api/work-orders/checklists/'),
                'checklist_items': request.build_absolute_uri('/api/work-orders/checklist-items/'),
            },
            'tracking': {
                'location_points': request.build_absolute_uri('/api/tracking/location-points/'),
                'zones': request.build_absolute_uri('/api/tracking/zones/'),
                'zone_events': request.build_absolute_uri('/api/tracking/zone-events/'),
                'routes': request.build_absolute_uri('/api/tracking/routes/'),
                'trips': request.build_absolute_uri('/api/tracking/trips/'),
            }
        },
        'special_endpoints': {
            'asset_statistics': request.build_absolute_uri('/api/assets/assets/statistics/'),
            'driver_statistics': request.build_absolute_uri('/api/drivers/drivers/statistics/'),
            'maintenance_due': request.build_absolute_uri('/api/maintenance/schedules/due_maintenance/'),
            'work_order_dashboard': request.build_absolute_uri('/api/work-orders/work-orders/dashboard/'),
            'live_tracking': request.build_absolute_uri('/api/tracking/trips/live_tracking/'),
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_health(request):
    """
    Health check endpoint
    """
    return Response({
        'status': 'healthy',
        'message': 'Fleet Management API is running',
        'user': request.user.username,
        'timestamp': request.META.get('HTTP_DATE')
    })


urlpatterns = [
    # API Root and health endpoints
    path('', api_root, name='api-root'),
    path('health/', api_health, name='api-health'),
    
    # Authentication endpoints
    path('auth/', include([
        path('token/', obtain_auth_token, name='api-token-auth'),
    ])),
    
    # Fleet Management App URLs
    path('assets/', include('apps.fleet_assets.urls')),
    path('drivers/', include('apps.fleet_drivers.urls')),
    path('maintenance/', include('apps.fleet_maintenance.urls')),
    path('work-orders/', include('apps.fleet_workorders.urls')),
    path('tracking/', include('apps.fleet_tracking.urls')),
    
    # Authentication app URLs
    path('accounts/', include('apps.authentication.urls')),
]