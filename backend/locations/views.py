from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from assets.models import Asset
from authentication.permissions import GranularLocationPermission, GranularZonePermission

from .models import LocationUpdate, LocationZone, AssetLocationSummary
from .serializers import (
    LocationUpdateSerializer,
    LocationZoneSerializer,
    AssetLocationSummarySerializer,
    BulkLocationUpdateSerializer,
    LocationHistorySerializer,
    ManualLocationEntrySerializer
)


class LocationUpdateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing location updates
    """
    queryset = LocationUpdate.objects.select_related('asset').all()
    serializer_class = LocationUpdateSerializer
    permission_classes = [GranularLocationPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Filtering options
    filterset_fields = ['source', 'asset__vehicle_type', 'asset__status']
    search_fields = ['asset__asset_id', 'address']
    ordering_fields = ['timestamp', 'created_at']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by asset
        asset_id = self.request.query_params.get('asset_id')
        if asset_id:
            queryset = queryset.filter(asset__asset_id=asset_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        # Filter by coordinates (bounding box)
        north = self.request.query_params.get('north')
        south = self.request.query_params.get('south')
        east = self.request.query_params.get('east')
        west = self.request.query_params.get('west')
        
        if all([north, south, east, west]):
            queryset = queryset.filter(
                latitude__lte=north,
                latitude__gte=south,
                longitude__lte=east,
                longitude__gte=west
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest location for all assets"""
        summaries = AssetLocationSummary.objects.select_related(
            'asset', 'current_zone'
        ).all()
        
        # Filter by asset status if requested
        status_filter = request.query_params.get('status')
        if status_filter:
            summaries = summaries.filter(asset__status=status_filter)
        
        serializer = AssetLocationSummarySerializer(summaries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def manual_entry(self, request):
        """Create a manual location entry"""
        serializer = ManualLocationEntrySerializer(data=request.data)
        if serializer.is_valid():
            location_update = serializer.save()
            response_serializer = LocationUpdateSerializer(location_update)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create location updates for telematics feeds"""
        serializer = BulkLocationUpdateSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response({
                'message': f'Successfully created {result["created_count"]} location updates',
                'created_count': result['created_count']
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='asset/(?P<asset_id>[^/.]+)')
    def asset_history(self, request, asset_id=None):
        """Get location history for a specific asset"""
        try:
            asset = Asset.objects.get(asset_id=asset_id)
        except Asset.DoesNotExist:
            return Response(
                {'error': f'Asset with ID {asset_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get location history with optional date filtering
        queryset = LocationUpdate.objects.filter(asset=asset)
        
        # Apply date filters
        days = request.query_params.get('days', 7)  # Default to last 7 days
        try:
            days = int(days)
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(timestamp__gte=start_date)
        except ValueError:
            pass
        
        # Order chronologically (oldest first) for path tracing
        queryset = queryset.order_by('timestamp')
        
        # Limit results for performance
        limit = request.query_params.get('limit', 100)
        try:
            limit = int(limit)
            queryset = queryset[:limit]
        except ValueError:
            queryset = queryset[:100]
        
        serializer = LocationHistorySerializer(queryset, many=True)
        return Response({
            'asset': {
                'id': str(asset.id),
                'asset_id': asset.asset_id,
                'make': asset.make,
                'model': asset.model
            },
            'locations': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get location tracking statistics"""
        total_updates = LocationUpdate.objects.count()
        today_updates = LocationUpdate.objects.filter(
            timestamp__date=timezone.now().date()
        ).count()
        
        # Assets with recent locations (last 24 hours)
        recent_threshold = timezone.now() - timedelta(hours=24)
        assets_with_recent_locations = AssetLocationSummary.objects.filter(
            timestamp__gte=recent_threshold
        ).values('asset').distinct().count()
        
        # Total trackable assets
        total_assets = Asset.objects.exclude(status='retired').count()
        
        # Source breakdown
        source_stats = {}
        for source, _ in LocationUpdate.SOURCE_CHOICES:
            count = LocationUpdate.objects.filter(source=source).count()
            source_stats[source] = count
        
        return Response({
            'total_updates': total_updates,
            'today_updates': today_updates,
            'assets_with_recent_locations': assets_with_recent_locations,
            'total_trackable_assets': total_assets,
            'tracking_coverage': round((assets_with_recent_locations / max(total_assets, 1)) * 100, 1),
            'source_breakdown': source_stats
        })


class LocationZoneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing location zones
    """
    queryset = LocationZone.objects.all()
    serializer_class = LocationZoneSerializer
    permission_classes = [GranularZonePermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['zone_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def assets_in_zone(self, request, pk=None):
        """Get all assets currently in this zone"""
        zone = self.get_object()
        assets_in_zone = AssetLocationSummary.objects.filter(
            current_zone=zone
        ).select_related('asset')
        
        serializer = AssetLocationSummarySerializer(assets_in_zone, many=True)
        return Response({
            'zone': LocationZoneSerializer(zone).data,
            'assets': serializer.data,
            'count': len(serializer.data)
        })
    
    @action(detail=True, methods=['post'])
    def check_point(self, request, pk=None):
        """Check if a point is within this zone"""
        zone = self.get_object()
        
        try:
            latitude = float(request.data.get('latitude'))
            longitude = float(request.data.get('longitude'))
        except (TypeError, ValueError):
            return Response(
                {'error': 'Valid latitude and longitude are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_within = zone.contains_point(latitude, longitude)
        
        return Response({
            'zone': zone.name,
            'point': {'latitude': latitude, 'longitude': longitude},
            'is_within_zone': is_within
        })


class AssetLocationSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for asset location summaries (for map display)
    """
    queryset = AssetLocationSummary.objects.select_related(
        'asset', 'current_zone'
    ).all()
    serializer_class = AssetLocationSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    
    filterset_fields = ['source', 'asset__vehicle_type', 'asset__status']
    search_fields = ['asset__asset_id', 'address']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by zone
        zone_id = self.request.query_params.get('zone_id')
        if zone_id:
            queryset = queryset.filter(current_zone_id=zone_id)
        
        # Filter by recency
        hours = self.request.query_params.get('within_hours')
        if hours:
            try:
                hours = int(hours)
                threshold = timezone.now() - timedelta(hours=hours)
                queryset = queryset.filter(timestamp__gte=threshold)
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def map_data(self, request):
        """Optimized endpoint for map display"""
        queryset = self.get_queryset()
        
        # Only include assets with recent locations (last 24 hours by default)
        hours = request.query_params.get('within_hours', 24)
        try:
            hours = int(hours)
            threshold = timezone.now() - timedelta(hours=hours)
            queryset = queryset.filter(timestamp__gte=threshold)
        except ValueError:
            pass
        
        serializer = AssetLocationSummarySerializer(queryset, many=True)
        
        # Also include zones for map display
        zones = LocationZone.objects.filter(is_active=True)
        zone_serializer = LocationZoneSerializer(zones, many=True)
        
        return Response({
            'assets': serializer.data,
            'zones': zone_serializer.data,
            'last_updated': timezone.now().isoformat()
        })
