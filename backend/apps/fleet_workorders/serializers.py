from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import date
from .models import (
    WorkOrder, WorkOrderPhoto, WorkOrderDocument, WorkOrderComment,
    WorkOrderStatusHistory, WorkOrderChecklist, WorkOrderChecklistItem
)


class UserSerializer(serializers.ModelSerializer):
    """Basic User serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id', 'username']


class WorkOrderPhotoSerializer(serializers.ModelSerializer):
    """Serializer for Work Order Photos"""
    
    uploaded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkOrderPhoto
        fields = ['id', 'photo', 'photo_type', 'title', 'description', 
                 'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by_name']
    
    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}"
        return None


class WorkOrderDocumentSerializer(serializers.ModelSerializer):
    """Serializer for Work Order Documents"""
    
    uploaded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkOrderDocument
        fields = ['id', 'document', 'document_type', 'title', 'description',
                 'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by_name']
    
    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}"
        return None


class WorkOrderCommentSerializer(serializers.ModelSerializer):
    """Serializer for Work Order Comments"""
    
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkOrderComment
        fields = ['id', 'comment', 'created_by', 'created_by_name', 
                 'created_at', 'is_internal']
        read_only_fields = ['id', 'created_at', 'created_by_name']
    
    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"


class WorkOrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for Work Order Status History"""
    
    changed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkOrderStatusHistory
        fields = ['id', 'old_status', 'new_status', 'changed_by', 'changed_by_name',
                 'changed_at', 'reason']
        read_only_fields = ['id', 'changed_at', 'changed_by_name']
    
    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return f"{obj.changed_by.first_name} {obj.changed_by.last_name}"
        return None


class WorkOrderChecklistItemSerializer(serializers.ModelSerializer):
    """Serializer for Work Order Checklist Items"""
    
    completed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkOrderChecklistItem
        fields = ['id', 'description', 'is_completed', 'completed_by',
                 'completed_by_name', 'completed_at', 'order', 'notes']
        read_only_fields = ['id', 'completed_by_name', 'completed_at']
    
    def get_completed_by_name(self, obj):
        if obj.completed_by:
            return f"{obj.completed_by.first_name} {obj.completed_by.last_name}"
        return None


class WorkOrderChecklistSerializer(serializers.ModelSerializer):
    """Serializer for Work Order Checklists"""
    
    items = WorkOrderChecklistItemSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkOrderChecklist
        fields = ['id', 'title', 'description', 'is_required', 'order',
                 'created_by', 'created_by_name', 'created_at', 'items',
                 'completion_percentage']
        read_only_fields = ['id', 'created_at', 'created_by_name', 'completion_percentage']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None
    
    def get_completion_percentage(self, obj):
        total_items = obj.items.count()
        if total_items == 0:
            return 100
        completed_items = obj.items.filter(is_completed=True).count()
        return int((completed_items / total_items) * 100)


class WorkOrderListSerializer(serializers.ModelSerializer):
    """Simplified Work Order serializer for list views"""
    
    asset_details = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkOrder
        fields = ['work_order_id', 'work_order_number', 'title', 'work_type',
                 'priority', 'status', 'asset', 'asset_details', 'created_by',
                 'created_by_name', 'assigned_to', 'assigned_to_name',
                 'requested_completion_date', 'progress_percentage', 'total_cost',
                 'is_overdue', 'days_until_due', 'created_at']
        read_only_fields = ['work_order_id', 'work_order_number', 'created_at', 
                          'total_cost', 'is_overdue', 'days_until_due']
    
    def get_asset_details(self, obj):
        return {
            'asset_id': str(obj.asset.asset_id),
            'asset_number': obj.asset.asset_number,
            'make_model': f"{obj.asset.make} {obj.asset.model}"
        }
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return obj.vendor or "Unassigned"
    
    def get_total_cost(self, obj):
        return obj.total_cost
    
    def get_is_overdue(self, obj):
        return obj.is_overdue
    
    def get_days_until_due(self, obj):
        return obj.days_until_due


class WorkOrderDetailSerializer(serializers.ModelSerializer):
    """Detailed Work Order serializer for detail views"""
    
    asset_details = serializers.SerializerMethodField()
    created_by_details = serializers.SerializerMethodField()
    assigned_to_details = serializers.SerializerMethodField()
    department_details = serializers.SerializerMethodField()
    maintenance_record_details = serializers.SerializerMethodField()
    
    photos = WorkOrderPhotoSerializer(many=True, read_only=True)
    documents = WorkOrderDocumentSerializer(many=True, read_only=True)
    comments = WorkOrderCommentSerializer(many=True, read_only=True)
    status_history = WorkOrderStatusHistorySerializer(many=True, read_only=True)
    checklists = WorkOrderChecklistSerializer(many=True, read_only=True)
    
    total_cost = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkOrder
        fields = ['work_order_id', 'work_order_number', 'asset', 'asset_details',
                 'title', 'description', 'work_type', 'priority', 'requested_completion_date',
                 'scheduled_start_date', 'scheduled_end_date', 'created_by',
                 'created_by_details', 'assigned_to', 'assigned_to_details',
                 'department', 'department_details', 'vendor', 'status',
                 'progress_percentage', 'estimated_labor_hours', 'actual_labor_hours',
                 'labor_cost', 'parts_cost', 'external_cost', 'total_cost',
                 'created_at', 'assigned_at', 'started_at', 'completed_at',
                 'closed_at', 'updated_at', 'location', 'safety_requirements',
                 'tools_required', 'notes', 'maintenance_record',
                 'maintenance_record_details', 'is_overdue', 'days_until_due',
                 'duration_days', 'photos', 'documents', 'comments',
                 'status_history', 'checklists']
        read_only_fields = ['work_order_id', 'work_order_number', 'created_at',
                          'updated_at', 'total_cost', 'is_overdue', 'days_until_due',
                          'duration_days']
    
    def get_asset_details(self, obj):
        return {
            'asset_id': str(obj.asset.asset_id),
            'asset_number': obj.asset.asset_number,
            'make_model': f"{obj.asset.make} {obj.asset.model}",
            'license_plate': obj.asset.license_plate,
            'current_odometer': obj.asset.current_odometer_reading
        }
    
    def get_created_by_details(self, obj):
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'name': f"{obj.created_by.first_name} {obj.created_by.last_name}",
                'email': obj.created_by.email
            }
        return None
    
    def get_assigned_to_details(self, obj):
        if obj.assigned_to:
            return {
                'id': obj.assigned_to.id,
                'name': f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}",
                'email': obj.assigned_to.email
            }
        return None
    
    def get_department_details(self, obj):
        if obj.department:
            return {
                'department_id': str(obj.department.department_id),
                'name': obj.department.name,
                'manager': obj.department.manager
            }
        return None
    
    def get_maintenance_record_details(self, obj):
        if obj.maintenance_record:
            return {
                'record_id': str(obj.maintenance_record.record_id),
                'service_date': obj.maintenance_record.service_date,
                'status': obj.maintenance_record.status
            }
        return None
    
    def get_total_cost(self, obj):
        return obj.total_cost
    
    def get_is_overdue(self, obj):
        return obj.is_overdue
    
    def get_days_until_due(self, obj):
        return obj.days_until_due
    
    def get_duration_days(self, obj):
        return obj.duration_days


class WorkOrderCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating work orders"""
    
    class Meta:
        model = WorkOrder
        fields = ['asset', 'title', 'description', 'work_type', 'priority',
                 'requested_completion_date', 'scheduled_start_date', 'scheduled_end_date',
                 'assigned_to', 'department', 'vendor', 'status', 'progress_percentage',
                 'estimated_labor_hours', 'actual_labor_hours', 'labor_cost',
                 'parts_cost', 'external_cost', 'location', 'safety_requirements',
                 'tools_required', 'notes', 'maintenance_record']
    
    def validate_requested_completion_date(self, value):
        """Validate requested completion date is not in the past"""
        if value and value < date.today():
            raise serializers.ValidationError("Requested completion date cannot be in the past")
        return value
    
    def validate_scheduled_dates(self, data):
        """Validate scheduled dates are logical"""
        start_date = data.get('scheduled_start_date')
        end_date = data.get('scheduled_end_date')
        
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError("Scheduled end date cannot be before start date")
        
        return data
    
    def validate_progress_percentage(self, value):
        """Validate progress percentage is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Progress percentage must be between 0 and 100")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        self.validate_scheduled_dates(data)
        
        # Validate status and progress alignment
        status = data.get('status')
        progress = data.get('progress_percentage', 0)
        
        if status == 'completed' and progress < 100:
            raise serializers.ValidationError("Work order marked as completed must have 100% progress")
        
        if status == 'open' and progress > 0:
            raise serializers.ValidationError("Open work orders should not have progress > 0")
        
        return data


class WorkOrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating work order status"""
    
    new_status = serializers.ChoiceField(choices=WorkOrder.STATUS_CHOICES)
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False, 
        allow_null=True
    )
    
    def validate_new_status(self, value):
        """Validate status transition is allowed"""
        work_order = self.context.get('work_order')
        if not work_order:
            return value
        
        current_status = work_order.status
        
        # Define allowed transitions
        allowed_transitions = {
            'open': ['assigned', 'cancelled'],
            'assigned': ['in_progress', 'on_hold', 'cancelled'],
            'in_progress': ['completed', 'on_hold', 'cancelled'],
            'on_hold': ['in_progress', 'cancelled'],
            'completed': ['closed', 'in_progress'],  # Allow reopening if needed
            'cancelled': [],  # Cannot transition from cancelled
            'closed': []  # Cannot transition from closed
        }
        
        if value not in allowed_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot transition from '{current_status}' to '{value}'"
            )
        
        return value