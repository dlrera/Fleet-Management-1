from rest_framework import serializers
from datetime import date, timedelta
from .models import (
    MaintenanceType, MaintenanceSchedule, MaintenanceRecord,
    MaintenancePart, MaintenancePartUsage
)


class MaintenanceTypeSerializer(serializers.ModelSerializer):
    """Serializer for Maintenance Types"""
    
    class Meta:
        model = MaintenanceType
        fields = ['id', 'name', 'category', 'description', 'estimated_duration_hours',
                 'estimated_cost', 'requires_technician', 'requires_parts', 
                 'safety_critical', 'instructions', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MaintenancePartSerializer(serializers.ModelSerializer):
    """Serializer for Maintenance Parts"""
    
    is_low_stock = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenancePart
        fields = ['id', 'part_number', 'part_name', 'description', 'manufacturer',
                 'unit_cost', 'stock_quantity', 'minimum_stock', 'is_low_stock', 
                 'total_value', 'compatible_assets', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_low_stock', 'total_value']
    
    def get_is_low_stock(self, obj):
        return obj.is_low_stock
    
    def get_total_value(self, obj):
        return obj.unit_cost * obj.stock_quantity


class MaintenancePartUsageSerializer(serializers.ModelSerializer):
    """Serializer for Maintenance Part Usage"""
    
    part_name = serializers.CharField(source='part.part_name', read_only=True)
    part_number = serializers.CharField(source='part.part_number', read_only=True)
    total_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenancePartUsage
        fields = ['id', 'part', 'part_name', 'part_number', 'quantity_used',
                 'unit_cost_at_time', 'total_cost', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at', 'total_cost', 'part_name', 'part_number']
    
    def get_total_cost(self, obj):
        return obj.total_cost


class MaintenanceScheduleListSerializer(serializers.ModelSerializer):
    """Simplified Maintenance Schedule serializer for list views"""
    
    asset_number = serializers.CharField(source='asset.asset_number', read_only=True)
    maintenance_type_name = serializers.CharField(source='maintenance_type.name', read_only=True)
    technician_name = serializers.SerializerMethodField()
    next_due_date = serializers.SerializerMethodField()
    is_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceSchedule
        fields = ['schedule_id', 'asset', 'asset_number', 'maintenance_type', 
                 'maintenance_type_name', 'interval_type', 'interval_value', 'time_unit',
                 'assigned_technician', 'technician_name', 'is_active',
                 'next_due_date', 'is_due', 'is_overdue', 'days_until_due', 'created_at']
        read_only_fields = ['schedule_id', 'created_at', 'next_due_date', 'is_due', 
                          'is_overdue', 'days_until_due']
    
    def get_technician_name(self, obj):
        if obj.assigned_technician:
            return f"{obj.assigned_technician.first_name} {obj.assigned_technician.last_name}"
        return None
    
    def get_next_due_date(self, obj):
        return obj.next_due_date
    
    def get_is_due(self, obj):
        return obj.is_due
    
    def get_is_overdue(self, obj):
        return obj.is_overdue
    
    def get_days_until_due(self, obj):
        return obj.days_until_due


class MaintenanceScheduleDetailSerializer(serializers.ModelSerializer):
    """Detailed Maintenance Schedule serializer for detail views"""
    
    asset_details = serializers.SerializerMethodField()
    maintenance_type_details = MaintenanceTypeSerializer(source='maintenance_type', read_only=True)
    technician_details = serializers.SerializerMethodField()
    next_due_date = serializers.SerializerMethodField()
    is_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    recent_records = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceSchedule
        fields = ['schedule_id', 'asset', 'asset_details', 'maintenance_type',
                 'maintenance_type_details', 'interval_type', 'interval_value', 'time_unit',
                 'last_service_date', 'last_service_mileage', 'last_service_hours',
                 'assigned_technician', 'technician_details', 'vendor', 'is_active', 'notes',
                 'next_due_date', 'is_due', 'is_overdue', 'days_until_due', 'recent_records',
                 'created_at', 'updated_at']
        read_only_fields = ['schedule_id', 'created_at', 'updated_at', 'next_due_date', 
                          'is_due', 'is_overdue', 'days_until_due', 'recent_records']
    
    def get_asset_details(self, obj):
        return {
            'asset_id': str(obj.asset.asset_id),
            'asset_number': obj.asset.asset_number,
            'make_model': f"{obj.asset.make} {obj.asset.model}",
            'current_odometer': obj.asset.current_odometer_reading
        }
    
    def get_technician_details(self, obj):
        if obj.assigned_technician:
            return {
                'id': obj.assigned_technician.id,
                'name': f"{obj.assigned_technician.first_name} {obj.assigned_technician.last_name}",
                'email': obj.assigned_technician.email
            }
        return None
    
    def get_next_due_date(self, obj):
        return obj.next_due_date
    
    def get_is_due(self, obj):
        return obj.is_due
    
    def get_is_overdue(self, obj):
        return obj.is_overdue
    
    def get_days_until_due(self, obj):
        return obj.days_until_due
    
    def get_recent_records(self, obj):
        recent = obj.maintenancerecord_set.filter(
            service_date__gte=date.today() - timedelta(days=365)
        ).order_by('-service_date')[:5]
        return [{'record_id': str(r.record_id), 'service_date': r.service_date, 
                'status': r.status, 'total_cost': r.total_cost} for r in recent]


class MaintenanceScheduleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating maintenance schedules"""
    
    class Meta:
        model = MaintenanceSchedule
        fields = ['asset', 'maintenance_type', 'interval_type', 'interval_value', 'time_unit',
                 'last_service_date', 'last_service_mileage', 'last_service_hours',
                 'assigned_technician', 'vendor', 'is_active', 'notes']
    
    def validate(self, data):
        """Validate interval configuration based on type"""
        interval_type = data.get('interval_type')
        time_unit = data.get('time_unit')
        
        if interval_type == 'time' and not time_unit:
            raise serializers.ValidationError("time_unit is required when interval_type is 'time'")
        
        if interval_type != 'time' and time_unit:
            raise serializers.ValidationError("time_unit should only be set when interval_type is 'time'")
        
        return data


class MaintenanceRecordListSerializer(serializers.ModelSerializer):
    """Simplified Maintenance Record serializer for list views"""
    
    asset_number = serializers.CharField(source='asset.asset_number', read_only=True)
    maintenance_type_name = serializers.CharField(source='maintenance_type.name', read_only=True)
    performed_by_name = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceRecord
        fields = ['record_id', 'asset', 'asset_number', 'maintenance_type',
                 'maintenance_type_name', 'service_date', 'completion_date', 'status',
                 'performed_by', 'performed_by_name', 'total_cost', 'quality_rating', 'created_at']
        read_only_fields = ['record_id', 'created_at', 'total_cost']
    
    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return f"{obj.performed_by.first_name} {obj.performed_by.last_name}"
        return obj.vendor or "Unknown"
    
    def get_total_cost(self, obj):
        return obj.total_cost


class MaintenanceRecordDetailSerializer(serializers.ModelSerializer):
    """Detailed Maintenance Record serializer for detail views"""
    
    asset_details = serializers.SerializerMethodField()
    maintenance_type_details = MaintenanceTypeSerializer(source='maintenance_type', read_only=True)
    performed_by_details = serializers.SerializerMethodField()
    parts_used = MaintenancePartUsageSerializer(many=True, read_only=True)
    work_order_details = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceRecord
        fields = ['record_id', 'asset', 'asset_details', 'maintenance_type',
                 'maintenance_type_details', 'schedule', 'service_date', 'completion_date',
                 'service_mileage', 'service_hours', 'performed_by', 'performed_by_details',
                 'vendor', 'technician_notes', 'labor_cost', 'parts_cost', 'external_cost',
                 'total_cost', 'status', 'quality_rating', 'issues_found', 'recommendations',
                 'invoice_number', 'work_order', 'work_order_details', 'parts_used',
                 'created_at', 'updated_at']
        read_only_fields = ['record_id', 'created_at', 'updated_at', 'total_cost']
    
    def get_asset_details(self, obj):
        return {
            'asset_id': str(obj.asset.asset_id),
            'asset_number': obj.asset.asset_number,
            'make_model': f"{obj.asset.make} {obj.asset.model}"
        }
    
    def get_performed_by_details(self, obj):
        if obj.performed_by:
            return {
                'id': obj.performed_by.id,
                'name': f"{obj.performed_by.first_name} {obj.performed_by.last_name}",
                'email': obj.performed_by.email
            }
        return None
    
    def get_work_order_details(self, obj):
        if obj.work_order:
            return {
                'work_order_id': str(obj.work_order.work_order_id),
                'work_order_number': obj.work_order.work_order_number,
                'status': obj.work_order.status
            }
        return None
    
    def get_total_cost(self, obj):
        return obj.total_cost


class MaintenanceRecordCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating maintenance records"""
    
    parts_to_use = serializers.ListField(
        child=serializers.DictField(), 
        write_only=True, 
        required=False,
        help_text="List of parts to use: [{'part_id': 1, 'quantity': 2, 'unit_cost': 10.50}]"
    )
    
    class Meta:
        model = MaintenanceRecord
        fields = ['asset', 'maintenance_type', 'schedule', 'service_date', 'completion_date',
                 'service_mileage', 'service_hours', 'performed_by', 'vendor', 'technician_notes',
                 'labor_cost', 'parts_cost', 'external_cost', 'status', 'quality_rating',
                 'issues_found', 'recommendations', 'invoice_number', 'work_order', 'parts_to_use']
    
    def create(self, validated_data):
        parts_to_use = validated_data.pop('parts_to_use', [])
        record = MaintenanceRecord.objects.create(**validated_data)
        
        # Create part usage records
        for part_data in parts_to_use:
            MaintenancePartUsage.objects.create(
                maintenance_record=record,
                part_id=part_data['part_id'],
                quantity_used=part_data['quantity'],
                unit_cost_at_time=part_data.get('unit_cost', 0),
                notes=part_data.get('notes', '')
            )
        
        return record
    
    def update(self, instance, validated_data):
        parts_to_use = validated_data.pop('parts_to_use', None)
        
        # Update record fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update parts if provided
        if parts_to_use is not None:
            # Remove existing part usage records
            instance.parts_used.all().delete()
            
            # Create new part usage records
            for part_data in parts_to_use:
                MaintenancePartUsage.objects.create(
                    maintenance_record=instance,
                    part_id=part_data['part_id'],
                    quantity_used=part_data['quantity'],
                    unit_cost_at_time=part_data.get('unit_cost', 0),
                    notes=part_data.get('notes', '')
                )
        
        return instance
    
    def validate_service_date(self, value):
        """Validate service date is not in the future"""
        if value > date.today():
            raise serializers.ValidationError("Service date cannot be in the future")
        return value
    
    def validate(self, data):
        """Validate completion date is after service date"""
        service_date = data.get('service_date')
        completion_date = data.get('completion_date')
        
        if completion_date and service_date and completion_date < service_date:
            raise serializers.ValidationError("Completion date cannot be before service date")
        
        return data