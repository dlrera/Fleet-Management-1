from rest_framework import serializers
from .models import Asset, AssetDocument


class AssetDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetDocument
        fields = ['id', 'document_type', 'title', 'file', 'description', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class AssetSerializer(serializers.ModelSerializer):
    documents = AssetDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'asset_id', 'vehicle_type', 'make', 'model', 'year',
            'vin', 'license_plate', 'department', 'purchase_date',
            'purchase_cost', 'current_odometer', 'status', 'notes',
            'created_at', 'updated_at', 'documents'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
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
            'created_at', 'documents_count'
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
            'purchase_cost', 'current_odometer', 'status', 'notes'
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