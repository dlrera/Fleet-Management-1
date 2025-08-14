import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta
import math


class LocationPoint(models.Model):
    """GPS location points for fleet assets"""
    
    SOURCE_TYPES = [
        ('gps_device', 'GPS Device'),
        ('mobile_app', 'Mobile App'),
        ('manual_entry', 'Manual Entry'),
        ('telematics', 'Telematics System'),
        ('driver_checkin', 'Driver Check-in'),
    ]

    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey('fleet_assets.Asset', on_delete=models.CASCADE, related_name='location_points')
    
    # GPS Coordinates
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Latitude in decimal degrees"
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Longitude in decimal degrees"
    )
    
    # Location Metadata
    timestamp = models.DateTimeField(help_text="Time when location was recorded")
    source_type = models.CharField(max_length=15, choices=SOURCE_TYPES)
    accuracy_meters = models.FloatField(blank=True, null=True, help_text="GPS accuracy in meters")
    
    # Motion Data
    speed_kmh = models.FloatField(blank=True, null=True, help_text="Speed in km/h")
    heading_degrees = models.FloatField(
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0), MaxValueValidator(360)],
        help_text="Direction of travel in degrees (0-360)"
    )
    altitude_meters = models.FloatField(blank=True, null=True, help_text="Altitude in meters")
    
    # Additional Context
    address = models.CharField(max_length=500, blank=True, default='', help_text="Reverse geocoded address")
    odometer_reading = models.PositiveIntegerField(blank=True, null=True, help_text="Vehicle odometer at this point")
    engine_hours = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    fuel_level_percent = models.FloatField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Driver Information
    driver = models.ForeignKey('fleet_drivers.Driver', on_delete=models.SET_NULL, null=True, blank=True)
    
    # System Fields
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['asset', '-timestamp']),
            models.Index(fields=['timestamp', 'source_type']),
            models.Index(fields=['asset', 'source_type', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.asset.asset_number} - {self.latitude}, {self.longitude} ({self.timestamp})"

    @property
    def coordinates(self):
        """Return coordinates as tuple"""
        return (float(self.latitude), float(self.longitude))

    def distance_to(self, other_location):
        """Calculate distance to another location in kilometers using Haversine formula"""
        if not other_location:
            return None
            
        lat1, lon1 = self.coordinates
        lat2, lon2 = other_location.coordinates
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        return c * r


class LocationZone(models.Model):
    """Defined geographical zones/geofences"""
    
    ZONE_TYPES = [
        ('depot', 'Depot/Base'),
        ('service_area', 'Service Area'),
        ('restricted', 'Restricted Zone'),
        ('customer_site', 'Customer Site'),
        ('maintenance_facility', 'Maintenance Facility'),
        ('fuel_station', 'Fuel Station'),
        ('parking', 'Parking Area'),
        ('other', 'Other'),
    ]

    zone_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPES)
    description = models.TextField(blank=True, default='')
    
    # Center point
    center_latitude = models.DecimalField(max_digits=10, decimal_places=7)
    center_longitude = models.DecimalField(max_digits=10, decimal_places=7)
    radius_meters = models.FloatField(help_text="Zone radius in meters")
    
    # Zone Properties
    is_active = models.BooleanField(default=True)
    color = models.CharField(max_length=7, default='#0000FF', help_text="Hex color for map display")
    
    # Alerts
    alert_on_enter = models.BooleanField(default=False)
    alert_on_exit = models.BooleanField(default=False)
    alert_on_speeding = models.BooleanField(default=False)
    speed_limit_kmh = models.FloatField(blank=True, null=True)
    
    # Access Control
    allowed_vehicles = models.ManyToManyField('fleet_assets.Asset', blank=True, related_name='allowed_zones')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_zone_type_display()})"

    def contains_point(self, latitude, longitude):
        """Check if a point is within this zone"""
        # Calculate distance from center
        center_lat, center_lon = float(self.center_latitude), float(self.center_longitude)
        
        # Simple distance calculation (approximate for small distances)
        lat_diff = math.radians(latitude - center_lat)
        lon_diff = math.radians(longitude - center_lon)
        
        a = (math.sin(lat_diff/2)**2 + 
             math.cos(math.radians(center_lat)) * math.cos(math.radians(latitude)) * 
             math.sin(lon_diff/2)**2)
        
        distance_km = 2 * math.asin(math.sqrt(a)) * 6371  # Earth radius
        distance_m = distance_km * 1000
        
        return distance_m <= self.radius_meters


class ZoneEvent(models.Model):
    """Events triggered by vehicles entering/exiting zones"""
    
    EVENT_TYPES = [
        ('enter', 'Zone Entry'),
        ('exit', 'Zone Exit'),
        ('speeding', 'Speed Violation'),
        ('dwelling', 'Extended Dwelling'),
        ('unauthorized', 'Unauthorized Access'),
    ]

    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey('fleet_assets.Asset', on_delete=models.CASCADE, related_name='zone_events')
    zone = models.ForeignKey(LocationZone, on_delete=models.CASCADE, related_name='events')
    location_point = models.ForeignKey(LocationPoint, on_delete=models.CASCADE)
    
    event_type = models.CharField(max_length=15, choices=EVENT_TYPES)
    event_time = models.DateTimeField()
    
    # Event Details
    speed_at_event = models.FloatField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True, help_text="Duration for dwelling events")
    
    # Alert Status
    alert_sent = models.BooleanField(default=False)
    alert_sent_at = models.DateTimeField(blank=True, null=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-event_time']
        indexes = [
            models.Index(fields=['asset', '-event_time']),
            models.Index(fields=['zone', '-event_time']),
            models.Index(fields=['event_type', 'alert_sent']),
        ]

    def __str__(self):
        return f"{self.asset.asset_number} - {self.get_event_type_display()} at {self.zone.name}"


class RouteTemplate(models.Model):
    """Pre-defined routes for vehicles"""
    
    route_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    
    # Route Properties
    estimated_duration_minutes = models.PositiveIntegerField(help_text="Estimated travel time")
    estimated_distance_km = models.FloatField(help_text="Estimated distance")
    
    # Route Points (stored as JSON)
    waypoints = models.JSONField(
        help_text="Array of {lat, lng, name} waypoint objects",
        default=list
    )
    
    # Assignment
    assigned_vehicles = models.ManyToManyField('fleet_assets.Asset', blank=True, related_name='route_templates')
    default_driver = models.ForeignKey('fleet_drivers.Driver', on_delete=models.SET_NULL, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Trip(models.Model):
    """Individual trips/journeys by vehicles"""
    
    TRIP_STATUS = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    trip_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey('fleet_assets.Asset', on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey('fleet_drivers.Driver', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Trip Details
    trip_name = models.CharField(max_length=200, blank=True, default='')
    route_template = models.ForeignKey(RouteTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timing
    planned_start_time = models.DateTimeField()
    planned_end_time = models.DateTimeField(blank=True, null=True)
    actual_start_time = models.DateTimeField(blank=True, null=True)
    actual_end_time = models.DateTimeField(blank=True, null=True)
    
    # Locations
    start_location = models.ForeignKey(
        LocationPoint, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='trips_started'
    )
    end_location = models.ForeignKey(
        LocationPoint, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='trips_ended'
    )
    
    # Trip Metrics
    total_distance_km = models.FloatField(default=0)
    total_duration_minutes = models.PositiveIntegerField(default=0)
    average_speed_kmh = models.FloatField(blank=True, null=True)
    max_speed_kmh = models.FloatField(blank=True, null=True)
    
    # Readings
    start_odometer = models.PositiveIntegerField(blank=True, null=True)
    end_odometer = models.PositiveIntegerField(blank=True, null=True)
    fuel_consumed_liters = models.FloatField(blank=True, null=True)
    
    # Status and Notes
    status = models.CharField(max_length=15, choices=TRIP_STATUS, default='planned')
    purpose = models.CharField(max_length=200, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-planned_start_time']
        indexes = [
            models.Index(fields=['asset', '-planned_start_time']),
            models.Index(fields=['driver', '-planned_start_time']),
            models.Index(fields=['status', 'planned_start_time']),
        ]

    def __str__(self):
        return f"{self.asset.asset_number} - {self.trip_name or 'Trip'} ({self.planned_start_time.date()})"

    @property
    def is_active(self):
        """Check if trip is currently active"""
        return self.status == 'in_progress'

    def calculate_trip_metrics(self):
        """Calculate trip metrics from location points"""
        if not self.actual_start_time or not self.actual_end_time:
            return
            
        # Get all location points during the trip
        trip_points = LocationPoint.objects.filter(
            asset=self.asset,
            timestamp__gte=self.actual_start_time,
            timestamp__lte=self.actual_end_time
        ).order_by('timestamp')
        
        if trip_points.count() < 2:
            return
            
        # Calculate total distance
        total_distance = 0
        max_speed = 0
        speeds = []
        
        for i in range(1, len(trip_points)):
            current = trip_points[i]
            previous = trip_points[i-1]
            
            # Distance calculation
            distance = previous.distance_to(current)
            if distance:
                total_distance += distance
                
            # Speed tracking
            if current.speed_kmh:
                speeds.append(current.speed_kmh)
                max_speed = max(max_speed, current.speed_kmh)
        
        # Update trip metrics
        self.total_distance_km = total_distance
        self.max_speed_kmh = max_speed
        if speeds:
            self.average_speed_kmh = sum(speeds) / len(speeds)
            
        # Duration
        duration = self.actual_end_time - self.actual_start_time
        self.total_duration_minutes = int(duration.total_seconds() / 60)
        
        self.save()
