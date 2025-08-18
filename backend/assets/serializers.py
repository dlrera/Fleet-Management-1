from rest_framework import serializers
from .models import Asset, AssetDocument
from drivers.models import DriverAssetAssignment


class AssetDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetDocument
        fields = ['id', 'document_type', 'title', 'file', 'description', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class DriverAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for driver assignments on assets"""    
    driver = serializers.SerializerMethodField()
    assignment_type_display = serializers.CharField(source='get_assignment_type_display', read_only=True)
    
    class Meta:
        model = DriverAssetAssignment
        fields = [
            'id', 'driver', 'assignment_type', 'assignment_type_display', 
            'status', 'assigned_date', 'unassigned_date', 'assigned_by', 
            'notes', 'priority'
        ]
    
    def get_driver(self, obj):
        return {
            'id': obj.driver.id,
            'driver_id': obj.driver.driver_id,
            'full_name': obj.driver.full_name,
            'first_name': obj.driver.first_name,
            'last_name': obj.driver.last_name,
            'email': obj.driver.email,
            'department': obj.driver.department,
            'employment_status': obj.driver.employment_status,
            'profile_photo': obj.driver.profile_photo.url if obj.driver.profile_photo else None
        }


class AssetSerializer(serializers.ModelSerializer):
    documents = AssetDocumentSerializer(many=True, read_only=True)
    driver_assignments = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = [
            'id', 'asset_id', 'vehicle_type', 'make', 'model', 'year',
            'vin', 'license_plate', 'department', 'purchase_date',
            'purchase_cost', 'current_odometer', 'status', 'notes',
            'image', 'thumbnail', 'created_at', 'updated_at', 'documents',
            'driver_assignments'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_driver_assignments(self, obj):
        # Get active driver assignments for this asset
        assignments = obj.driver_assignments.filter(
            status='active',
            unassigned_date__isnull=True
        ).select_related('driver').order_by('priority', '-assigned_date')
        
        return DriverAssignmentSerializer(assignments, many=True).data
    
    def validate_year(self, value):
        from datetime import datetime
        current_year = datetime.now().year
        if value > current_year + 1:
            raise serializers.ValidationError("Year cannot be in the future.")
        return value
    
    def validate_vin(self, value):
        if value and len(value) != 17:
            raise serializers.ValidationError("VIN must be exactly 17 characters.")
        return value


class AssetListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    documents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = [
            'id', 'asset_id', 'vehicle_type', 'make', 'model', 'year',
            'license_plate', 'department', 'current_odometer', 'status',
            'thumbnail', 'created_at', 'documents_count'
        ]
    
    def get_documents_count(self, obj):
        return obj.documents.count()


class AssetCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for create/update operations without nested documents"""
    
    asset_id = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'asset_id', 'vehicle_type', 'make', 'model', 'year',
            'vin', 'license_plate', 'department', 'purchase_date',
            'purchase_cost', 'current_odometer', 'status', 'notes', 'image'
        ]
        read_only_fields = ['id']
    
    def validate_year(self, value):
        from datetime import datetime
        current_year = datetime.now().year
        if value > current_year + 1:
            raise serializers.ValidationError("Year cannot be in the future.")
        return value
    
    def validate_vin(self, value):
        if value and len(value) != 17:
            raise serializers.ValidationError("VIN must be exactly 17 characters.")
        return value