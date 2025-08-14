from rest_framework import serializers
from datetime import datetime, timedelta
from .models import LocationPoint, LocationZone, ZoneEvent, RouteTemplate, Trip


class LocationPointSerializer(serializers.ModelSerializer):
    """Serializer for Location Points (GPS data)"""
    
    class Meta:
        model = LocationPoint
        fields = ['location_id', 'asset', 'latitude', 'longitude', 'altitude_meters',
                 'accuracy_meters', 'speed_kmh', 'heading_degrees', 'timestamp', 'source_type']
        read_only_fields = ['location_id']
    
    def validate_latitude(self, value):
        """Validate latitude is within valid range"""
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees")
        return value
    
    def validate_longitude(self, value):
        """Validate longitude is within valid range"""
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees")
        return value
    
    def validate_speed_kmh(self, value):
        """Validate speed is non-negative"""
        if value and value < 0:
            raise serializers.ValidationError("Speed cannot be negative")
        return value


class LocationZoneSerializer(serializers.ModelSerializer):
    """Serializer for Location Zones (Geofences)"""
    
    class Meta:
        model = LocationZone
        fields = ['zone_id', 'name', 'description', 'zone_type', 'center_latitude',
                 'center_longitude', 'radius_meters', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['zone_id', 'created_at', 'updated_at']
    
    def validate_center_latitude(self, value):
        """Validate latitude is within valid range"""
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees")
        return value
    
    def validate_center_longitude(self, value):
        """Validate longitude is within valid range"""
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees")
        return value
    
    def validate_radius_meters(self, value):
        """Validate radius is positive"""
        if value <= 0:
            raise serializers.ValidationError("Radius must be greater than 0")
        return value


class ZoneEventSerializer(serializers.ModelSerializer):
    """Serializer for Zone Events (Enter/Exit events)"""
    
    asset_details = serializers.SerializerMethodField()
    zone_details = serializers.SerializerMethodField()
    
    class Meta:
        model = ZoneEvent
        fields = ['event_id', 'asset', 'asset_details', 'zone', 'zone_details',
                 'event_type', 'timestamp', 'location_point', 'created_at']
        read_only_fields = ['event_id', 'created_at', 'asset_details', 'zone_details']
    
    def get_asset_details(self, obj):
        return {
            'asset_id': str(obj.asset.asset_id),
            'asset_number': obj.asset.asset_number,
            'make_model': f"{obj.asset.make} {obj.asset.model}"
        }
    
    def get_zone_details(self, obj):
        return {
            'zone_id': str(obj.zone.zone_id),
            'name': obj.zone.name,
            'zone_type': obj.zone.zone_type
        }


class RouteTemplateSerializer(serializers.ModelSerializer):
    """Serializer for Route Templates"""
    
    waypoint_count = serializers.SerializerMethodField()
    total_distance_km = serializers.SerializerMethodField()
    
    class Meta:
        model = RouteTemplate
        fields = ['route_id', 'name', 'description', 'start_location_name',
                 'end_location_name', 'waypoints', 'estimated_duration_minutes',
                 'is_active', 'waypoint_count', 'total_distance_km',
                 'created_at', 'updated_at']
        read_only_fields = ['route_id', 'created_at', 'updated_at', 
                          'waypoint_count', 'total_distance_km']
    
    def get_waypoint_count(self, obj):
        return len(obj.waypoints) if obj.waypoints else 0
    
    def get_total_distance_km(self, obj):
        # Simple distance calculation for demo
        if not obj.waypoints or len(obj.waypoints) < 2:
            return 0
        
        total_distance = 0
        for i in range(1, len(obj.waypoints)):
            # This would normally use the Haversine formula
            # For now, return a placeholder
            total_distance += 10  # km per segment
        
        return total_distance
    
    def validate_waypoints(self, value):
        """Validate waypoints structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Waypoints must be a list")
        
        for i, waypoint in enumerate(value):
            if not isinstance(waypoint, dict):
                raise serializers.ValidationError(f"Waypoint {i} must be an object")
            
            if 'latitude' not in waypoint or 'longitude' not in waypoint:
                raise serializers.ValidationError(f"Waypoint {i} must have latitude and longitude")
            
            try:
                lat = float(waypoint['latitude'])
                lng = float(waypoint['longitude'])
                
                if lat < -90 or lat > 90:
                    raise serializers.ValidationError(f"Waypoint {i} latitude out of range")
                if lng < -180 or lng > 180:
                    raise serializers.ValidationError(f"Waypoint {i} longitude out of range")
                    
            except (ValueError, TypeError):
                raise serializers.ValidationError(f"Waypoint {i} coordinates must be numbers")
        
        return value


class TripListSerializer(serializers.ModelSerializer):
    """Simplified Trip serializer for list views"""
    
    asset_details = serializers.SerializerMethodField()
    driver_details = serializers.SerializerMethodField()
    route_details = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Trip
        fields = ['trip_id', 'asset', 'asset_details', 'driver', 'driver_details',
                 'route', 'route_details', 'start_time', 'end_time', 'status',
                 'total_distance_km', 'duration_display', 'created_at']
        read_only_fields = ['trip_id', 'created_at', 'duration_display']
    
    def get_asset_details(self, obj):
        return {
            'asset_id': str(obj.asset.asset_id),
            'asset_number': obj.asset.asset_number,
            'make_model': f"{obj.asset.make} {obj.asset.model}"
        }
    
    def get_driver_details(self, obj):
        if obj.driver:
            return {
                'driver_id': str(obj.driver.driver_id),
                'name': f"{obj.driver.user.first_name} {obj.driver.user.last_name}"
            }
        return None
    
    def get_route_details(self, obj):
        if obj.route:
            return {
                'route_id': str(obj.route.route_id),
                'name': obj.route.name,
                'start_location': obj.route.start_location_name,
                'end_location': obj.route.end_location_name
            }
        return None
    
    def get_duration_display(self, obj):
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            hours = duration.total_seconds() // 3600
            minutes = (duration.total_seconds() % 3600) // 60
            return f"{int(hours)}h {int(minutes)}m"
        return None


class TripDetailSerializer(serializers.ModelSerializer):
    """Detailed Trip serializer for detail views"""
    
    asset_details = serializers.SerializerMethodField()
    driver_details = serializers.SerializerMethodField()
    route_details = serializers.SerializerMethodField()
    location_points = LocationPointSerializer(many=True, read_only=True, source='get_location_points')
    zone_events = ZoneEventSerializer(many=True, read_only=True, source='get_zone_events')
    
    duration_minutes = serializers.SerializerMethodField()
    average_speed_kmh = serializers.SerializerMethodField()
    max_speed_kmh = serializers.SerializerMethodField()
    stops_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Trip
        fields = ['trip_id', 'asset', 'asset_details', 'driver', 'driver_details',
                 'route', 'route_details', 'start_time', 'end_time', 'status',
                 'start_location_name', 'end_location_name', 'start_latitude',
                 'start_longitude', 'end_latitude', 'end_longitude',
                 'total_distance_km', 'average_speed_kmh', 'max_speed_kmh',
                 'start_odometer', 'end_odometer', 'fuel_consumed_liters',
                 'duration_minutes', 'stops_count', 'notes',
                 'location_points', 'zone_events', 'created_at', 'updated_at']
        read_only_fields = ['trip_id', 'created_at', 'updated_at', 'duration_minutes',
                          'average_speed_kmh', 'max_speed_kmh', 'stops_count']
    
    def get_asset_details(self, obj):
        return {
            'asset_id': str(obj.asset.asset_id),
            'asset_number': obj.asset.asset_number,
            'make_model': f"{obj.asset.make} {obj.asset.model}",
            'license_plate': obj.asset.license_plate
        }
    
    def get_driver_details(self, obj):
        if obj.driver:
            return {
                'driver_id': str(obj.driver.driver_id),
                'name': f"{obj.driver.user.first_name} {obj.driver.user.last_name}",
                'license_number': obj.driver.license_number
            }
        return None
    
    def get_route_details(self, obj):
        if obj.route:
            return RouteTemplateSerializer(obj.route).data
        return None
    
    def get_duration_minutes(self, obj):
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            return int(duration.total_seconds() / 60)
        return None
    
    def get_average_speed_kmh(self, obj):
        if obj.total_distance_km and obj.start_time and obj.end_time:
            duration_hours = (obj.end_time - obj.start_time).total_seconds() / 3600
            if duration_hours > 0:
                return round(obj.total_distance_km / duration_hours, 1)
        return None
    
    def get_max_speed_kmh(self, obj):
        # This would query the related location points for max speed
        # For now, return a placeholder
        return None
    
    def get_stops_count(self, obj):
        # This would analyze location points to count stops
        # For now, return a placeholder
        return 0


class TripCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating trips"""
    
    class Meta:
        model = Trip
        fields = ['asset', 'driver', 'route', 'start_time', 'end_time', 'status',
                 'start_location_name', 'end_location_name', 'start_latitude',
                 'start_longitude', 'end_latitude', 'end_longitude',
                 'total_distance_km', 'start_odometer', 'end_odometer',
                 'fuel_consumed_liters', 'notes']
    
    def validate(self, data):
        """Cross-field validation"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        start_odometer = data.get('start_odometer')
        end_odometer = data.get('end_odometer')
        
        # Validate time range
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time")
        
        # Validate odometer readings
        if start_odometer is not None and end_odometer is not None:
            if end_odometer < start_odometer:
                raise serializers.ValidationError("End odometer reading must be greater than start reading")
        
        # Validate coordinates if provided
        for field_pair in [('start_latitude', 'start_longitude'), ('end_latitude', 'end_longitude')]:
            lat_field, lng_field = field_pair
            lat = data.get(lat_field)
            lng = data.get(lng_field)
            
            if lat is not None:
                if lat < -90 or lat > 90:
                    raise serializers.ValidationError(f"{lat_field} must be between -90 and 90 degrees")
            
            if lng is not None:
                if lng < -180 or lng > 180:
                    raise serializers.ValidationError(f"{lng_field} must be between -180 and 180 degrees")
        
        return data
    
    def validate_total_distance_km(self, value):
        """Validate distance is non-negative"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Total distance cannot be negative")
        return value
    
    def validate_fuel_consumed_liters(self, value):
        """Validate fuel consumption is non-negative"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Fuel consumption cannot be negative")
        return value


class LiveTrackingSerializer(serializers.Serializer):
    """Serializer for live tracking data"""
    
    asset_id = serializers.UUIDField()
    asset_number = serializers.CharField(max_length=50)
    make_model = serializers.CharField(max_length=100)
    driver_name = serializers.CharField(max_length=100, allow_null=True)
    current_latitude = serializers.FloatField()
    current_longitude = serializers.FloatField()
    current_speed = serializers.FloatField(allow_null=True)
    current_heading = serializers.FloatField(allow_null=True)
    last_update = serializers.DateTimeField()
    status = serializers.CharField(max_length=20)
    current_trip_id = serializers.UUIDField(allow_null=True)
    in_zone = serializers.CharField(max_length=100, allow_null=True)


class GeoFenceAlertSerializer(serializers.Serializer):
    """Serializer for geofence alert data"""
    
    alert_id = serializers.UUIDField()
    asset_id = serializers.UUIDField()
    asset_number = serializers.CharField(max_length=50)
    zone_id = serializers.UUIDField()
    zone_name = serializers.CharField(max_length=100)
    event_type = serializers.ChoiceField(choices=['enter', 'exit'])
    timestamp = serializers.DateTimeField()
    location = serializers.DictField()
    is_acknowledged = serializers.BooleanField(default=False)