from rest_framework import serializers
from .models import (
    CapitalPlan, CapitalPlanItem, CapitalPlanScenario, CapitalPlanApproval,
    AssetLifecycle, CapitalProject, ProjectAssetLink
)
from django.contrib.auth import get_user_model

User = get_user_model()


class CapitalPlanItemSerializer(serializers.ModelSerializer):
    """Serializer for capital plan items."""
    
    fleet_asset_details = serializers.SerializerMethodField(read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    
    class Meta:
        model = CapitalPlanItem
        fields = [
            'id', 'item_type', 'item_type_display', 'priority', 'priority_display',
            'fleet_asset_id', 'fleet_asset_details', 'description', 'quantity',
            'asset_type', 'make', 'model', 'year', 'specifications',
            'unit_cost', 'total_cost', 'justification', 'expected_service_life',
            'is_approved', 'approval_notes', 'target_quarter',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_cost', 'created_at', 'updated_at']
    
    def get_fleet_asset_details(self, obj):
        """Get fleet asset details if referenced."""
        if obj.fleet_asset_id:
            try:
                from assets.models import Asset
                asset = Asset.objects.get(id=obj.fleet_asset_id)
                return {
                    'id': asset.id,
                    'asset_id': asset.asset_id,
                    'make': asset.make,
                    'model': asset.model,
                    'year': asset.year,
                    'status': asset.status
                }
            except:
                return None
        return None


class CapitalPlanScenarioSerializer(serializers.ModelSerializer):
    """Serializer for capital plan scenarios."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    adjusted_budget = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CapitalPlanScenario
        fields = [
            'id', 'name', 'description', 'budget_adjustment', 'adjusted_budget',
            'item_modifications', 'total_cost', 'items_included', 'items_deferred',
            'is_primary', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_adjusted_budget(self, obj):
        """Calculate adjusted budget for scenario."""
        return obj.plan.total_budget + obj.budget_adjustment


class CapitalPlanApprovalSerializer(serializers.ModelSerializer):
    """Serializer for capital plan approvals."""
    
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = CapitalPlanApproval
        fields = [
            'id', 'level', 'level_display', 'approver', 'approver_name',
            'action', 'action_display', 'comments', 'conditions', 'approved_at'
        ]
        read_only_fields = ['approved_at']


class CapitalPlanSerializer(serializers.ModelSerializer):
    """Serializer for capital plans."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    remaining_budget = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    budget_utilization = serializers.FloatField(read_only=True)
    
    items = CapitalPlanItemSerializer(many=True, read_only=True)
    scenarios = CapitalPlanScenarioSerializer(many=True, read_only=True)
    approvals = CapitalPlanApprovalSerializer(many=True, read_only=True)
    
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    scenarios_count = serializers.IntegerField(source='scenarios.count', read_only=True)
    
    class Meta:
        model = CapitalPlan
        fields = [
            'id', 'name', 'description', 'fiscal_year', 'total_budget',
            'allocated_budget', 'remaining_budget', 'budget_utilization',
            'status', 'status_display', 'created_by', 'created_by_name',
            'approved_by', 'approved_by_name', 'created_at', 'updated_at',
            'approved_at', 'notes', 'tags', 'items', 'scenarios', 'approvals',
            'items_count', 'scenarios_count'
        ]
        read_only_fields = ['allocated_budget', 'created_at', 'updated_at']


class CapitalPlanListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for capital plan lists."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    budget_utilization = serializers.FloatField(read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = CapitalPlan
        fields = [
            'id', 'name', 'fiscal_year', 'total_budget', 'allocated_budget',
            'budget_utilization', 'status', 'status_display', 'created_by_name',
            'created_at', 'items_count'
        ]


class AssetLifecycleSerializer(serializers.ModelSerializer):
    """Serializer for asset lifecycle tracking."""
    
    age_years = serializers.FloatField(read_only=True)
    remaining_useful_life = serializers.FloatField(read_only=True)
    estimated_replacement_date = serializers.DateField(read_only=True)
    lifecycle_percentage = serializers.FloatField(read_only=True)
    maintenance_cost_ratio = serializers.FloatField(read_only=True)
    condition_display = serializers.CharField(source='get_current_condition_display', read_only=True)
    category_display = serializers.CharField(source='get_asset_category_display', read_only=True)
    
    class Meta:
        model = AssetLifecycle
        fields = [
            'id', 'asset_name', 'asset_type', 'asset_category', 'category_display',
            'asset_code', 'location', 'department', 'installation_date',
            'expected_useful_life', 'age_years', 'remaining_useful_life',
            'estimated_replacement_date', 'lifecycle_percentage',
            'original_cost', 'replacement_cost', 'salvage_value',
            'current_condition', 'condition_display', 'last_condition_assessment',
            'condition_notes', 'total_maintenance_cost', 'maintenance_cost_ratio',
            'last_maintenance_date', 'maintenance_frequency',
            'fleet_asset_id', 'manufacturer', 'model_number', 'serial_number',
            'warranty_expiry', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 
                           'age_years', 'remaining_useful_life', 'estimated_replacement_date',
                           'lifecycle_percentage', 'maintenance_cost_ratio']


class AssetLifecycleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for asset lifecycle lists."""
    
    age_years = serializers.FloatField(read_only=True)
    lifecycle_percentage = serializers.FloatField(read_only=True)
    condition_display = serializers.CharField(source='get_current_condition_display', read_only=True)
    category_display = serializers.CharField(source='get_asset_category_display', read_only=True)
    
    class Meta:
        model = AssetLifecycle
        fields = [
            'id', 'asset_name', 'asset_code', 'asset_category', 'category_display',
            'location', 'current_condition', 'condition_display',
            'age_years', 'lifecycle_percentage', 'replacement_cost'
        ]


class ProjectAssetLinkSerializer(serializers.ModelSerializer):
    """Serializer for project-asset links."""
    
    asset_name = serializers.CharField(source='asset_lifecycle.asset_name', read_only=True)
    asset_code = serializers.CharField(source='asset_lifecycle.asset_code', read_only=True)
    relationship_display = serializers.CharField(source='get_relationship_type_display', read_only=True)
    
    class Meta:
        model = ProjectAssetLink
        fields = [
            'id', 'asset_lifecycle', 'asset_name', 'asset_code',
            'relationship_type', 'relationship_display', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class CapitalProjectSerializer(serializers.ModelSerializer):
    """Serializer for capital projects."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    budget_variance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    budget_variance_percentage = serializers.FloatField(read_only=True)
    asset_links = ProjectAssetLinkSerializer(many=True, read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = CapitalProject
        fields = [
            'id', 'project_code', 'title', 'description', 'category', 'category_display',
            'priority', 'priority_display', 'status', 'status_display',
            'scheduled_year', 'scheduled_quarter', 'estimated_cost', 'approved_budget',
            'actual_cost', 'budget_variance', 'budget_variance_percentage',
            'business_case', 'benefits', 'risks', 'capital_plan',
            'project_manager', 'department', 'stakeholders',
            'start_date', 'end_date', 'completion_date',
            'approval_date', 'approved_by', 'approved_by_name',
            'asset_links', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by',
                           'approved_budget', 'actual_cost', 'budget_variance',
                           'budget_variance_percentage', 'approval_date', 
                           'approved_by', 'completion_date']
    
    def validate_estimated_cost(self, value):
        """Validate estimated cost is within reasonable range."""
        from decimal import Decimal
        if value < 0:
            raise serializers.ValidationError("Estimated cost cannot be negative")
        if value > Decimal('999999999.99'):
            raise serializers.ValidationError("Estimated cost exceeds maximum allowed value")
        return value
    
    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance and self.instance.status == 'approved' and value != 'approved':
            if not self.context['request'].user.has_perm('capital_planning.approve_plan'):
                raise serializers.ValidationError("Cannot change status of approved project without permission")
        return value


class CapitalProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for capital project lists."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = CapitalProject
        fields = [
            'id', 'project_code', 'title', 'category', 'category_display',
            'priority', 'priority_display', 'status', 'status_display',
            'scheduled_year', 'estimated_cost', 'department'
        ]


class AssetConditionUpdateSerializer(serializers.Serializer):
    """Serializer for updating asset condition."""
    
    condition = serializers.ChoiceField(choices=AssetLifecycle.CONDITION_CHOICES)
    assessment_date = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate_notes(self, value):
        """Sanitize notes to prevent XSS."""
        import bleach
        if value:
            # Remove any HTML tags
            clean_value = bleach.clean(value, tags=[], strip=True)
            if clean_value != value:
                raise serializers.ValidationError("Notes cannot contain HTML")
        return value