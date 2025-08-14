from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Max, Min, Sum
from django.utils import timezone
from datetime import datetime, timedelta, date

from .models import LocationPoint, LocationZone, ZoneEvent, RouteTemplate, Trip
from .serializers import (
    LocationPointSerializer, LocationZoneSerializer, ZoneEventSerializer,
    RouteTemplateSerializer, TripListSerializer, TripDetailSerializer,
    TripCreateUpdateSerializer, LiveTrackingSerializer, GeoFenceAlertSerializer
)


class LocationPointViewSet(viewsets.ModelViewSet):
    """ViewSet for Location Point (GPS data) management"""
    
    queryset = LocationPoint.objects.select_related('asset')
    serializer_class = LocationPointSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['asset']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__gte=start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__lte=end_dt)
            except ValueError:
                pass
        
        # Filter by location bounds (bounding box)
        north = self.request.query_params.get('north')
        south = self.request.query_params.get('south')
        east = self.request.query_params.get('east')
        west = self.request.query_params.get('west')
        
        if all([north, south, east, west]):
            try:
                queryset = queryset.filter(
                    latitude__lte=float(north),
                    latitude__gte=float(south),
                    longitude__lte=float(east),
                    longitude__gte=float(west)
                )
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def latest_positions(self, request):
        """Get latest position for each asset"""
        latest_points = []
        
        # Get unique assets that have location data
        asset_ids = self.get_queryset().values_list('asset_id', flat=True).distinct()
        
        for asset_id in asset_ids:
            latest_point = self.get_queryset().filter(asset_id=asset_id).first()
            if latest_point:
                latest_points.append(latest_point)
        
        serializer = LocationPointSerializer(latest_points, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create location points"""
        serializer = LocationPointSerializer(data=request.data, many=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationZoneViewSet(viewsets.ModelViewSet):
    """ViewSet for Location Zone (Geofence) management"""
    
    queryset = LocationZone.objects.all()
    serializer_class = LocationZoneSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['zone_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'zone_type', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def active_zones(self, request):
        """Get all active geofences"""
        active_zones = self.get_queryset().filter(is_active=True)
        serializer = LocationZoneSerializer(active_zones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def zone_events(self, request, pk=None):
        """Get recent events for this zone"""
        zone = self.get_object()
        days_back = int(request.query_params.get('days_back', 7))
        start_date = timezone.now() - timedelta(days=days_back)
        
        events = ZoneEvent.objects.filter(
            zone=zone,
            timestamp__gte=start_date
        ).select_related('asset').order_by('-timestamp')
        
        serializer = ZoneEventSerializer(events, many=True)
        return Response(serializer.data)


class ZoneEventViewSet(viewsets.ModelViewSet):
    """ViewSet for Zone Event management"""
    
    queryset = ZoneEvent.objects.select_related('asset', 'zone', 'location_point')
    serializer_class = ZoneEventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['asset', 'zone', 'event_type']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__gte=start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__lte=end_dt)
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def recent_alerts(self, request):
        """Get recent zone entry/exit alerts"""
        hours_back = int(request.query_params.get('hours_back', 24))
        start_time = timezone.now() - timedelta(hours=hours_back)
        
        recent_events = self.get_queryset().filter(
            timestamp__gte=start_time
        ).order_by('-timestamp')[:50]
        
        serializer = ZoneEventSerializer(recent_events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get zone event statistics"""
        queryset = self.get_queryset()
        
        # Date range for stats
        days_back = int(request.query_params.get('days_back', 30))
        start_date = timezone.now() - timedelta(days=days_back)
        recent_events = queryset.filter(timestamp__gte=start_date)
        
        stats = {
            'total_events': queryset.count(),
            'recent_events': recent_events.count(),
            'by_event_type': list(recent_events.values('event_type').annotate(count=Count('event_type'))),
            'by_zone': list(
                recent_events.select_related('zone')
                .values('zone__name')
                .annotate(count=Count('zone__name'))[:10]
            ),
            'by_asset': list(
                recent_events.select_related('asset')
                .values('asset__asset_number')
                .annotate(count=Count('asset__asset_number'))[:10]
            ),
            'events_by_hour': self.get_events_by_hour(recent_events),
        }
        
        return Response(stats)
    
    def get_events_by_hour(self, queryset):
        """Get event count by hour of day"""
        events_by_hour = {}
        for hour in range(24):
            events_by_hour[f"{hour:02d}:00"] = 0
        
        for event in queryset:
            hour_key = f"{event.timestamp.hour:02d}:00"
            events_by_hour[hour_key] += 1
        
        return events_by_hour


class RouteTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for Route Template management"""
    
    queryset = RouteTemplate.objects.all()
    serializer_class = RouteTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description', 'start_location_name', 'end_location_name']
    ordering_fields = ['name', 'estimated_duration_minutes', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def active_routes(self, request):
        """Get all active route templates"""
        active_routes = self.get_queryset().filter(is_active=True)
        serializer = RouteTemplateSerializer(active_routes, many=True)
        return Response(serializer.data)


class TripViewSet(viewsets.ModelViewSet):
    """ViewSet for Trip management with comprehensive tracking features"""
    
    queryset = Trip.objects.select_related('asset', 'driver__user', 'route')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset', 'driver', 'route', 'status']
    search_fields = ['asset__asset_number', 'driver__user__first_name', 
                    'driver__user__last_name', 'start_location_name', 'end_location_name']
    ordering_fields = ['start_time', 'end_time', 'total_distance_km', 'created_at']
    ordering = ['-start_time']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return TripListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TripCreateUpdateSerializer
        return TripDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__date__lte=end_date)
        
        # Filter by distance range
        min_distance = self.request.query_params.get('min_distance')
        max_distance = self.request.query_params.get('max_distance')
        
        if min_distance:
            queryset = queryset.filter(total_distance_km__gte=float(min_distance))
        if max_distance:
            queryset = queryset.filter(total_distance_km__lte=float(max_distance))
        
        # Filter active trips
        if self.request.query_params.get('active_only'):
            queryset = queryset.filter(status='in_progress')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get trip statistics and metrics"""
        queryset = self.get_queryset()
        
        # Date range for recent stats
        days_back = int(request.query_params.get('days_back', 30))
        start_date = date.today() - timedelta(days=days_back)
        recent_trips = queryset.filter(start_time__date__gte=start_date)
        
        # Calculate aggregate statistics
        stats = queryset.aggregate(
            total_trips=Count('trip_id'),
            total_distance=Sum('total_distance_km'),
            avg_distance=Avg('total_distance_km'),
            max_distance=Max('total_distance_km'),
            total_fuel=Sum('fuel_consumed_liters'),
            avg_fuel=Avg('fuel_consumed_liters')
        )
        
        # Recent statistics
        recent_stats = recent_trips.aggregate(
            recent_trips=Count('trip_id'),
            recent_distance=Sum('total_distance_km'),
            recent_fuel=Sum('fuel_consumed_liters')
        )
        
        # Status breakdown
        status_counts = {}
        for status_choice in Trip.STATUS_CHOICES:
            status_counts[status_choice[0]] = queryset.filter(status=status_choice[0]).count()
        
        return Response({
            **stats,
            **recent_stats,
            'status_counts': status_counts,
            'by_asset': list(
                queryset.select_related('asset')
                .values('asset__asset_number')
                .annotate(trip_count=Count('trip_id'), total_km=Sum('total_distance_km'))[:10]
            ),
            'by_driver': list(
                queryset.select_related('driver__user')
                .values('driver__user__first_name', 'driver__user__last_name')
                .annotate(trip_count=Count('trip_id'), total_km=Sum('total_distance_km'))[:10]
            ),
        })
    
    @action(detail=False, methods=['get'])
    def active_trips(self, request):
        """Get currently active trips"""
        active_trips = self.get_queryset().filter(status='in_progress')
        serializer = TripListSerializer(active_trips, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def live_tracking(self, request):
        """Get live tracking data for all assets"""
        # This would normally query real-time location data
        # For now, return mock data structure
        tracking_data = []
        
        # Get latest location for each asset with active trips
        active_trips = self.get_queryset().filter(status='in_progress')
        
        for trip in active_trips:
            # Get latest location point for this asset
            latest_location = LocationPoint.objects.filter(
                asset=trip.asset
            ).order_by('-timestamp').first()
            
            if latest_location:
                tracking_data.append({
                    'asset_id': str(trip.asset.asset_id),
                    'asset_number': trip.asset.asset_number,
                    'make_model': f"{trip.asset.make} {trip.asset.model}",
                    'driver_name': f"{trip.driver.user.first_name} {trip.driver.user.last_name}" if trip.driver else None,
                    'current_latitude': latest_location.latitude,
                    'current_longitude': latest_location.longitude,
                    'current_speed': latest_location.speed,
                    'current_heading': latest_location.heading,
                    'last_update': latest_location.timestamp,
                    'status': trip.status,
                    'current_trip_id': str(trip.trip_id),
                    'in_zone': None  # Would check current zones
                })
        
        return Response(tracking_data)
    
    @action(detail=True, methods=['patch'])
    def start_trip(self, request, pk=None):
        """Start a trip"""
        trip = self.get_object()
        
        if trip.status != 'planned':
            return Response(
                {'error': 'Trip can only be started from planned status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trip.status = 'in_progress'
        trip.start_time = timezone.now()
        
        # Set start location if provided
        if 'start_latitude' in request.data:
            trip.start_latitude = request.data['start_latitude']
        if 'start_longitude' in request.data:
            trip.start_longitude = request.data['start_longitude']
        if 'start_odometer' in request.data:
            trip.start_odometer = request.data['start_odometer']
        
        trip.save()
        
        serializer = TripDetailSerializer(trip)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def end_trip(self, request, pk=None):
        """End a trip"""
        trip = self.get_object()
        
        if trip.status != 'in_progress':
            return Response(
                {'error': 'Trip can only be ended from in_progress status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trip.status = 'completed'
        trip.end_time = timezone.now()
        
        # Set end location if provided
        if 'end_latitude' in request.data:
            trip.end_latitude = request.data['end_latitude']
        if 'end_longitude' in request.data:
            trip.end_longitude = request.data['end_longitude']
        if 'end_odometer' in request.data:
            trip.end_odometer = request.data['end_odometer']
        if 'total_distance_km' in request.data:
            trip.total_distance_km = request.data['total_distance_km']
        if 'fuel_consumed_liters' in request.data:
            trip.fuel_consumed_liters = request.data['fuel_consumed_liters']
        
        trip.save()
        
        serializer = TripDetailSerializer(trip)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def route_replay(self, request, pk=None):
        """Get route replay data for a completed trip"""
        trip = self.get_object()
        
        if not trip.start_time or not trip.end_time:
            return Response(
                {'error': 'Trip must have start and end times'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all location points for this trip
        location_points = LocationPoint.objects.filter(
            asset=trip.asset,
            timestamp__gte=trip.start_time,
            timestamp__lte=trip.end_time
        ).order_by('timestamp')
        
        # Get zone events during the trip
        zone_events = ZoneEvent.objects.filter(
            asset=trip.asset,
            timestamp__gte=trip.start_time,
            timestamp__lte=trip.end_time
        ).order_by('timestamp')
        
        return Response({
            'trip': TripDetailSerializer(trip).data,
            'location_points': LocationPointSerializer(location_points, many=True).data,
            'zone_events': ZoneEventSerializer(zone_events, many=True).data,
        })
