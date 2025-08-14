from rest_framework import serializers
from .models import Department, Asset, AssetDocument, AssetImage


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    
    asset_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'manager', 'created_at', 'updated_at', 'asset_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'asset_count']
    
    def get_asset_count(self, obj):
        return obj.assets.filter(status='active').count()


class AssetImageSerializer(serializers.ModelSerializer):
    """Serializer for Asset Images"""
    
    class Meta:
        model = AssetImage
        fields = ['id', 'image', 'title', 'description', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class AssetDocumentSerializer(serializers.ModelSerializer):
    """Serializer for Asset Documents"""
    
    class Meta:
        model = AssetDocument
        fields = ['id', 'file', 'document_type', 'title', 'description', 'expiry_date', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class AssetListSerializer(serializers.ModelSerializer):
    """Simplified Asset serializer for list views"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    age_years = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = ['asset_id', 'asset_number', 'make', 'model', 'year', 'vehicle_type', 
                 'license_plate', 'status', 'department_name', 'current_odometer_reading',
                 'age_years', 'created_at']
        read_only_fields = ['asset_id', 'created_at', 'age_years']
    
    def get_age_years(self, obj):
        return obj.age_years


class AssetDetailSerializer(serializers.ModelSerializer):
    """Detailed Asset serializer for detail views"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    documents = AssetDocumentSerializer(many=True, read_only=True)
    images = AssetImageSerializer(many=True, read_only=True)
    age_years = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = ['asset_id', 'asset_number', 'vehicle_type', 'make', 'model', 'year',
                 'vin_number', 'license_plate', 'fuel_type', 'fuel_capacity',
                 'purchase_date', 'purchase_cost', 'current_value',
                 'current_odometer_reading', 'warranty_expiry', 'insurance_policy_number',
                 'insurance_expiry', 'status', 'condition_rating', 'department', 'department_name',
                 'notes', 'created_by', 'created_at', 'updated_at',
                 'documents', 'images', 'age_years']
        read_only_fields = ['asset_id', 'created_at', 'updated_at', 'age_years']
    
    def get_age_years(self, obj):
        return obj.age_years


class AssetCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating assets"""
    
    class Meta:
        model = Asset
        fields = ['asset_number', 'vehicle_type', 'make', 'model', 'year',
                 'vin_number', 'license_plate', 'fuel_type', 'fuel_capacity',
                 'purchase_date', 'purchase_cost', 'current_value',
                 'current_odometer_reading', 'warranty_expiry', 'insurance_policy_number',
                 'insurance_expiry', 'status', 'condition_rating', 'department', 'notes']
    
    def validate_vin_number(self, value):
        """Validate VIN number format and uniqueness"""
        if value and len(value) != 17:
            raise serializers.ValidationError("VIN number must be 17 characters long")
        return value
    
    def validate_asset_number(self, value):
        """Validate asset number uniqueness"""
        instance = getattr(self, 'instance', None)
        if Asset.objects.filter(asset_number=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Asset number must be unique")
        return value