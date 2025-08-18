from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from assets.models import Asset
import uuid


class LocationUpdate(models.Model):
    """
    Model to track asset location updates from various sources
    """
    SOURCE_CHOICES = [
        ('manual', 'Manual Entry'),
        ('gps_device', 'GPS Device'),
        ('mobile_app', 'Mobile App'),
        ('telematics', 'Telematics System'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='location_updates')
    
    # Coordinate fields with precision for GPS accuracy
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=8,
        validators=[
            MinValueValidator(-90.0),
            MaxValueValidator(90.0)
        ],
        help_text="Latitude coordinate (-90.0 to 90.0)"
    )
    longitude = models.DecimalField(
        max_digits=11, 
        decimal_places=8,
        validators=[
            MinValueValidator(-180.0),
            MaxValueValidator(180.0)
        ],
        help_text="Longitude coordinate (-180.0 to 180.0)"
    )
    
    # Timestamp and source
    timestamp = models.DateTimeField(help_text="When the location was recorded")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual')
    
    # Optional GPS metadata
    accuracy = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0)],
        help_text="GPS accuracy in meters"
    )
    speed = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0)],
        help_text="Speed in km/h"
    )
    heading = models.FloatField(
        null=True, 
        blank=True,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(360.0)
        ],
        help_text="Direction in degrees (0-360)"
    )
    
    # Address information (can be populated via reverse geocoding)
    address = models.TextField(blank=True, help_text="Human-readable address")
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Location Update'
        verbose_name_plural = 'Location Updates'
        indexes = [
            models.Index(fields=['asset', '-timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        return f"{self.asset.asset_id} at {self.latitude}, {self.longitude} ({self.timestamp})"
    
    @property
    def coordinates(self):
        """Return coordinates as tuple for easy use"""
        return (float(self.latitude), float(self.longitude))
    
    def save(self, *args, **kwargs):
        # Ensure latitude/longitude are within valid ranges
        if self.latitude < -90 or self.latitude > 90:
            raise ValueError("Latitude must be between -90 and 90")
        if self.longitude < -180 or self.longitude > 180:
            raise ValueError("Longitude must be between -180 and 180")
        
        super().save(*args, **kwargs)


class LocationZone(models.Model):
    """
    Model for defining geographical zones for geofencing and location classification
    """
    ZONE_TYPE_CHOICES = [
        ('depot', 'Depot'),
        ('service_area', 'Service Area'),
        ('customer_site', 'Customer Site'),
        ('restricted', 'Restricted Zone'),
        ('maintenance', 'Maintenance Facility'),
        ('other', 'Other'),
    ]
    
    # Basic information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="Zone name")
    description = models.TextField(blank=True, help_text="Zone description")
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES, default='other')
    
    # Geographic definition (circular zones for MVP)
    center_lat = models.DecimalField(
        max_digits=10, 
        decimal_places=8,
        validators=[
            MinValueValidator(-90.0),
            MaxValueValidator(90.0)
        ],
        help_text="Zone center latitude"
    )
    center_lng = models.DecimalField(
        max_digits=11, 
        decimal_places=8,
        validators=[
            MinValueValidator(-180.0),
            MaxValueValidator(180.0)
        ],
        help_text="Zone center longitude"
    )
    radius = models.FloatField(
        validators=[
            MinValueValidator(100.0),
            MaxValueValidator(50000.0)
        ],
        help_text="Zone radius in meters (100m - 50km)"
    )
    
    # Status and metadata
    is_active = models.BooleanField(default=True)
    color = models.CharField(max_length=7, default='#1976d2', help_text="Hex color code for map display")
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Location Zone'
        verbose_name_plural = 'Location Zones'
        indexes = [
            models.Index(fields=['zone_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_zone_type_display()})"
    
    @property
    def center_coordinates(self):
        """Return center coordinates as tuple"""
        return (float(self.center_lat), float(self.center_lng))
    
    def contains_point(self, latitude, longitude):
        """
        Check if a point (lat, lng) falls within this zone
        Uses simple circular distance calculation
        """
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lat1, lon1 = radians(float(self.center_lat)), radians(float(self.center_lng))
        lat2, lon2 = radians(latitude), radians(longitude)
        
        # Haversine formula for distance calculation
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        distance_km = 2 * asin(sqrt(a)) * 6371  # Earth radius in km
        distance_m = distance_km * 1000  # Convert to meters
        
        return distance_m <= self.radius


class AssetLocationSummary(models.Model):
    """
    Optimized model to store latest location for each asset for quick retrieval
    Updated whenever a new location update is received
    """
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='current_location')
    latest_update = models.ForeignKey(LocationUpdate, on_delete=models.CASCADE)
    
    # Denormalized fields for quick access
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    timestamp = models.DateTimeField()
    source = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    
    # Zone information (if applicable)
    current_zone = models.ForeignKey(LocationZone, on_delete=models.SET_NULL, null=True, blank=True)
    
    # System fields
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Asset Location Summary'
        verbose_name_plural = 'Asset Location Summaries'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        return f"{self.asset.asset_id} - Current Location"
    
    @classmethod
    def update_for_asset(cls, location_update):
        """
        Update or create summary for an asset based on new location update
        """
        # Check if asset is in any zone
        zones = LocationZone.objects.filter(is_active=True)
        current_zone = None
        for zone in zones:
            if zone.contains_point(float(location_update.latitude), float(location_update.longitude)):
                current_zone = zone
                break
        
        summary, created = cls.objects.get_or_create(
            asset=location_update.asset,
            defaults={
                'latest_update': location_update,
                'latitude': location_update.latitude,
                'longitude': location_update.longitude,
                'timestamp': location_update.timestamp,
                'source': location_update.source,
                'address': location_update.address,
                'current_zone': current_zone,
            }
        )
        
        if not created and location_update.timestamp > summary.timestamp:
            # Update with newer location
            summary.latest_update = location_update
            summary.latitude = location_update.latitude
            summary.longitude = location_update.longitude
            summary.timestamp = location_update.timestamp
            summary.source = location_update.source
            summary.address = location_update.address
            summary.current_zone = current_zone
            
            summary.save()
        
        return summary
