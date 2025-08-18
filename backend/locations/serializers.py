from rest_framework import serializers
from django.utils import timezone
from assets.models import Asset
from .models import LocationUpdate, LocationZone, AssetLocationSummary


class LocationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for LocationUpdate model
    """
    asset_id = serializers.CharField(write_only=True, help_text="Asset ID to associate with this location")
    asset_details = serializers.SerializerMethodField(read_only=True)
    coordinates = serializers.ReadOnlyField()
    
    class Meta:
        model = LocationUpdate
        fields = [
            'id', 'asset', 'asset_id', 'asset_details',
            'latitude', 'longitude', 'coordinates',
            'timestamp', 'source', 'accuracy', 'speed', 'heading',
            'address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'asset', 'coordinates', 'created_at', 'updated_at']
    
    def get_asset_details(self, obj):
        """Return basic asset information"""
        return {
            'id': str(obj.asset.id),
            'asset_id': obj.asset.asset_id,
            'make': obj.asset.make,
            'model': obj.asset.model,
            'vehicle_type': obj.asset.vehicle_type,
            'status': obj.asset.status
        }
    
    def validate_asset_id(self, value):
        """Validate that the asset exists"""
        try:
            Asset.objects.get(asset_id=value)
            return value
        except Asset.DoesNotExist:
            raise serializers.ValidationError(f"Asset with ID '{value}' does not exist.")
    
    def validate_timestamp(self, value):
        """Validate timestamp is not in the future"""
        if value > timezone.now():
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # Ensure latitude and longitude are provided together
        if ('latitude' in data) != ('longitude' in data):
            raise serializers.ValidationError("Both latitude and longitude must be provided.")
        
        # Validate speed and heading constraints
        if data.get('speed') is not None and data.get('speed') < 0:
            raise serializers.ValidationError("Speed cannot be negative.")
        
        if data.get('heading') is not None:
            heading = data.get('heading')
            if heading < 0 or heading > 360:
                raise serializers.ValidationError("Heading must be between 0 and 360 degrees.")
        
        return data
    
    def create(self, validated_data):
        """Create location update and update asset summary"""
        asset_id = validated_data.pop('asset_id')
        asset = Asset.objects.get(asset_id=asset_id)
        validated_data['asset'] = asset
        
        # Create the location update
        location_update = super().create(validated_data)
        
        # Update the asset location summary
        AssetLocationSummary.update_for_asset(location_update)
        
        return location_update


class LocationZoneSerializer(serializers.ModelSerializer):
    """
    Serializer for LocationZone model
    """
    center_coordinates = serializers.ReadOnlyField()
    
    class Meta:
        model = LocationZone
        fields = [
            'id', 'name', 'description', 'zone_type',
            'center_lat', 'center_lng', 'center_coordinates',
            'radius', 'is_active', 'color',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'center_coordinates', 'created_at', 'updated_at']
    
    def validate_color(self, value):
        """Validate hex color format"""
        import re
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise serializers.ValidationError("Color must be a valid hex color code (e.g., #1976d2).")
        return value
    
    def validate_radius(self, value):
        """Validate radius is reasonable"""
        if value < 1:
            raise serializers.ValidationError("Radius must be at least 1 meter.")
        if value > 50000:  # 50km
            raise serializers.ValidationError("Radius cannot exceed 50,000 meters (50km).")
        return value


class AssetLocationSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for AssetLocationSummary model - read-only for map display
    """
    asset_details = serializers.SerializerMethodField()
    zone_details = serializers.SerializerMethodField()
    coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetLocationSummary
        fields = [
            'asset', 'asset_details', 'latitude', 'longitude', 'coordinates',
            'timestamp', 'source', 'address', 'current_zone', 'zone_details',
            'updated_at'
        ]
        read_only_fields = ['asset', 'asset_details', 'latitude', 'longitude', 'coordinates', 'timestamp', 'source', 'address', 'current_zone', 'zone_details', 'updated_at']
    
    def get_asset_details(self, obj):
        """Return comprehensive asset information for map display"""
        return {
            'id': str(obj.asset.id),
            'asset_id': obj.asset.asset_id,
            'make': obj.asset.make,
            'model': obj.asset.model,
            'year': obj.asset.year,
            'vehicle_type': obj.asset.vehicle_type,
            'status': obj.asset.status,
            'department': obj.asset.department,
            'thumbnail': obj.asset.thumbnail.url if obj.asset.thumbnail else None
        }
    
    def get_zone_details(self, obj):
        """Return zone information if asset is in a zone"""
        if obj.current_zone:
            return {
                'id': str(obj.current_zone.id),
                'name': obj.current_zone.name,
                'zone_type': obj.current_zone.zone_type,
                'color': obj.current_zone.color
            }
        return None
    
    def get_coordinates(self, obj):
        """Return coordinates as tuple"""
        return [float(obj.latitude), float(obj.longitude)]


class BulkLocationUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk location updates (e.g., from telematics systems)
    """
    locations = LocationUpdateSerializer(many=True)
    
    def validate_locations(self, value):
        """Validate that we don't have too many locations in one batch"""
        if len(value) > 1000:
            raise serializers.ValidationError("Maximum 1000 location updates per batch.")
        return value
    
    def create(self, validated_data):
        """Create multiple location updates efficiently"""
        locations_data = validated_data['locations']
        created_locations = []
        
        for location_data in locations_data:
            serializer = LocationUpdateSerializer(data=location_data)
            if serializer.is_valid():
                location = serializer.save()
                created_locations.append(location)
            else:
                # Log error but continue with other locations
                pass
        
        return {'created_count': len(created_locations), 'locations': created_locations}


class LocationHistorySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for location history views
    """
    class Meta:
        model = LocationUpdate
        fields = [
            'id', 'latitude', 'longitude', 'timestamp', 
            'source', 'speed', 'heading', 'address'
        ]
        read_only_fields = ['id', 'latitude', 'longitude', 'timestamp', 'source', 'speed', 'heading', 'address']


class ManualLocationEntrySerializer(serializers.Serializer):
    """
    Simplified serializer for manual location entry
    """
    asset_id = serializers.CharField()
    latitude = serializers.DecimalField(max_digits=10, decimal_places=8)
    longitude = serializers.DecimalField(max_digits=11, decimal_places=8)
    address = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_asset_id(self, value):
        """Validate asset exists and is active"""
        try:
            asset = Asset.objects.get(asset_id=value)
            if asset.status == 'retired':
                raise serializers.ValidationError("Cannot add location for retired asset.")
            return value
        except Asset.DoesNotExist:
            raise serializers.ValidationError(f"Asset with ID '{value}' does not exist.")
    
    def create(self, validated_data):
        """Create location update with manual source"""
        asset = Asset.objects.get(asset_id=validated_data['asset_id'])
        
        location_data = {
            'asset': asset,
            'latitude': validated_data['latitude'],
            'longitude': validated_data['longitude'],
            'timestamp': timezone.now(),
            'source': 'manual',
            'address': validated_data.get('address', '')
        }
        
        location_update = LocationUpdate.objects.create(**location_data)
        AssetLocationSummary.update_for_asset(location_update)
        
        return location_update