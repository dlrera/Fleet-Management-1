from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import FuelTransaction, FuelSite, FuelCard, FuelAlert, UnitsPolicy
from assets.serializers import AssetListSerializer
from decimal import Decimal
from datetime import datetime, timedelta


class FuelSiteSerializer(serializers.ModelSerializer):
    """Serializer for fuel sites"""
    
    class Meta:
        model = FuelSite
        fields = [
            'id', 'name', 'site_type', 'address', 'latitude', 'longitude',
            'time_zone', 'products_supported', 'controller_type', 'external_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FuelTransactionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for fuel transaction lists"""
    asset_details = AssetListSerializer(source='asset', read_only=True)
    fuel_site_name = serializers.CharField(source='fuel_site.name', read_only=True)
    product_type_display = serializers.CharField(source='get_product_type_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    entry_source_display = serializers.CharField(source='get_entry_source_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    # Computed fields
    is_anomaly = serializers.SerializerMethodField()
    days_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = FuelTransaction
        fields = [
            'id', 'asset', 'asset_details', 'timestamp', 'entry_source', 'entry_source_display',
            'product_type', 'product_type_display', 'volume', 'unit', 'unit_display',
            'unit_price', 'total_cost', 'odometer', 'vendor', 'fuel_site_name',
            'mpg', 'cost_per_mile', 'distance_delta', 'is_anomaly', 'days_ago',
            'created_by_username', 'created_at'
        ]
    
    def get_is_anomaly(self, obj):
        """Check if this transaction has any anomaly flags"""
        return len(obj.is_anomaly_candidate) > 0
    
    def get_days_ago(self, obj):
        """Calculate how many days ago this transaction occurred"""
        delta = datetime.now().date() - obj.timestamp.date()
        return delta.days


class FuelTransactionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for fuel transactions"""
    asset_details = AssetListSerializer(source='asset', read_only=True)
    fuel_site_details = FuelSiteSerializer(source='fuel_site', read_only=True)
    created_by_details = serializers.SerializerMethodField()
    
    # Display fields
    product_type_display = serializers.CharField(source='get_product_type_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    entry_source_display = serializers.CharField(source='get_entry_source_display', read_only=True)
    
    # Computed fields
    normalized_volume_gallons = serializers.ReadOnlyField()
    is_anomaly_candidate = serializers.ReadOnlyField()
    efficiency_rating = serializers.SerializerMethodField()
    cost_analysis = serializers.SerializerMethodField()
    
    class Meta:
        model = FuelTransaction
        fields = [
            'id', 'asset', 'asset_details', 'timestamp', 'entry_source', 'entry_source_display',
            'product_type', 'product_type_display', 'volume', 'unit', 'unit_display',
            'unit_price', 'total_cost', 'odometer', 'engine_hours',
            'location_latitude', 'location_longitude', 'location_label',
            'payment_ref', 'vendor', 'fuel_site', 'fuel_site_details', 'notes',
            'distance_delta', 'mpg', 'cost_per_mile', 'fuel_per_hour',
            'normalized_volume_gallons', 'is_anomaly_candidate', 'efficiency_rating',
            'cost_analysis', 'created_by', 'created_by_details', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'distance_delta', 'mpg', 'cost_per_mile', 'fuel_per_hour',
            'created_at', 'updated_at'
        ]
    
    def get_created_by_details(self, obj):
        """Get creator user details"""
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'username': obj.created_by.username,
                'first_name': obj.created_by.first_name,
                'last_name': obj.created_by.last_name
            }
        return None
    
    def get_efficiency_rating(self, obj):
        """Calculate efficiency rating compared to asset class average"""
        if not obj.mpg:
            return None
            
        # Simple rating based on MPG thresholds
        # This could be enhanced with asset class baselines
        if obj.mpg >= 30:
            return 'excellent'
        elif obj.mpg >= 20:
            return 'good'
        elif obj.mpg >= 15:
            return 'average'
        elif obj.mpg >= 10:
            return 'below_average'
        else:
            return 'poor'
    
    def get_cost_analysis(self, obj):
        """Analyze cost metrics for this transaction"""
        analysis = {
            'total_cost_formatted': f"${obj.total_cost:.2f}" if obj.total_cost else None,
            'unit_price_formatted': f"${obj.unit_price:.3f}" if obj.unit_price else None,
            'cost_per_mile_formatted': f"${obj.cost_per_mile:.3f}" if obj.cost_per_mile else None,
        }
        
        # Add cost comparison (could be enhanced with historical averages)
        if obj.unit_price:
            if obj.unit_price > 5.00:
                analysis['price_rating'] = 'high'
            elif obj.unit_price > 3.50:
                analysis['price_rating'] = 'average'
            else:
                analysis['price_rating'] = 'low'
        
        return analysis


class FuelTransactionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating fuel transactions"""
    
    class Meta:
        model = FuelTransaction
        fields = [
            'id', 'asset', 'timestamp', 'entry_source', 'product_type',
            'volume', 'unit', 'unit_price', 'total_cost', 'odometer', 'engine_hours',
            'location_latitude', 'location_longitude', 'location_label',
            'payment_ref', 'vendor', 'fuel_site', 'notes'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate fuel transaction data"""
        # Require either unit_price or total_cost
        if not data.get('unit_price') and not data.get('total_cost'):
            raise serializers.ValidationError({
                'pricing': 'Either unit_price or total_cost must be provided.'
            })
        
        # Validate volume is positive
        if data.get('volume') and data['volume'] <= 0:
            raise serializers.ValidationError({
                'volume': 'Volume must be greater than zero.'
            })
        
        # Validate odometer is reasonable if provided
        if data.get('odometer'):
            if data['odometer'] < 0:
                raise serializers.ValidationError({
                    'odometer': 'Odometer reading cannot be negative.'
                })
            
            # Check for reasonable odometer reading (< 1 million miles)
            if data['odometer'] > 1000000:
                raise serializers.ValidationError({
                    'odometer': 'Odometer reading seems unreasonably high.'
                })
        
        # Validate timestamp is not too far in the future
        if data.get('timestamp'):
            future_limit = timezone.now() + timedelta(days=1)
            if data['timestamp'] > future_limit:
                raise serializers.ValidationError({
                    'timestamp': 'Transaction timestamp cannot be more than 1 day in the future.'
                })
        
        return data
    
    def create(self, validated_data):
        """Create fuel transaction with current user"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class FuelCardSerializer(serializers.ModelSerializer):
    """Serializer for fuel cards"""
    assigned_asset_details = AssetListSerializer(source='assigned_asset', read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = FuelCard
        fields = [
            'id', 'provider', 'provider_display', 'card_last4', 'assigned_asset',
            'assigned_asset_details', 'pin_policy', 'status', 'status_display',
            'external_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FuelAlertSerializer(serializers.ModelSerializer):
    """Serializer for fuel alerts"""
    asset_details = AssetListSerializer(source='asset', read_only=True)
    transaction_details = FuelTransactionListSerializer(source='transaction', read_only=True)
    resolved_by_details = serializers.SerializerMethodField()
    
    # Display fields
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Computed fields
    days_open = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = FuelAlert
        fields = [
            'id', 'alert_type', 'alert_type_display', 'severity', 'severity_display',
            'status', 'status_display', 'asset', 'asset_details', 'transaction',
            'transaction_details', 'title', 'description', 'threshold_value',
            'actual_value', 'resolved_by', 'resolved_by_details', 'resolved_at',
            'resolution_notes', 'days_open', 'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_resolved_by_details(self, obj):
        """Get resolver user details"""
        if obj.resolved_by:
            return {
                'id': obj.resolved_by.id,
                'username': obj.resolved_by.username,
                'first_name': obj.resolved_by.first_name,
                'last_name': obj.resolved_by.last_name
            }
        return None
    
    def get_days_open(self, obj):
        """Calculate how many days this alert has been open"""
        if obj.status == 'resolved':
            end_date = obj.resolved_at.date() if obj.resolved_at else obj.updated_at.date()
        else:
            end_date = datetime.now().date()
        
        delta = end_date - obj.created_at.date()
        return delta.days
    
    def get_is_overdue(self, obj):
        """Check if alert is overdue based on severity"""
        if obj.status == 'resolved':
            return False
        
        days_open = self.get_days_open(obj)
        
        # Define SLA days based on severity
        sla_days = {
            'critical': 1,
            'high': 3,
            'medium': 7,
            'low': 14
        }
        
        return days_open > sla_days.get(obj.severity, 7)


class UnitsPolicySerializer(serializers.ModelSerializer):
    """Serializer for units policy"""
    
    # Display fields
    distance_unit_display = serializers.CharField(source='get_distance_unit_display', read_only=True)
    volume_unit_display = serializers.CharField(source='get_volume_unit_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    
    class Meta:
        model = UnitsPolicy
        fields = [
            'id', 'distance_unit', 'distance_unit_display', 'volume_unit', 'volume_unit_display',
            'currency', 'currency_display', 'low_mpg_threshold_percent', 'high_price_percentile',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FuelStatsSerializer(serializers.Serializer):
    """Serializer for fuel statistics"""
    
    # Summary statistics
    total_transactions = serializers.IntegerField()
    total_volume = serializers.DecimalField(max_digits=12, decimal_places=3)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_mpg = serializers.DecimalField(max_digits=6, decimal_places=2)
    average_cost_per_mile = serializers.DecimalField(max_digits=8, decimal_places=4)
    
    # Breakdown by product type
    product_breakdown = serializers.DictField()
    
    # Trend data
    monthly_trends = serializers.ListField()
    
    # Alert counts
    open_alerts = serializers.IntegerField()
    critical_alerts = serializers.IntegerField()
    
    # Top performers
    most_efficient_assets = serializers.ListField()
    least_efficient_assets = serializers.ListField()


class FuelImportPreviewSerializer(serializers.Serializer):
    """Serializer for CSV import preview"""
    
    total_rows = serializers.IntegerField()
    valid_rows = serializers.IntegerField()
    invalid_rows = serializers.IntegerField()
    duplicates = serializers.IntegerField()
    
    # Sample data
    sample_valid = serializers.ListField()
    sample_invalid = serializers.ListField()
    
    # Validation errors
    errors = serializers.DictField()
    warnings = serializers.DictField()
    
    # Column mapping
    column_mapping = serializers.DictField()
    required_columns = serializers.ListField()
    optional_columns = serializers.ListField()