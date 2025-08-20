from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class CapitalPlan(models.Model):
    """
    Represents a capital planning cycle for fleet asset procurement/replacement.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    fiscal_year = models.IntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2050)]
    )
    
    # Budget information
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    allocated_budget = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Audit fields
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_capital_plans'
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_capital_plans'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['-fiscal_year', '-created_at']
        permissions = [
            ('view_plan', 'Can view capital plans'),
            ('edit_plan', 'Can edit capital plans'),
            ('approve_plan', 'Can approve capital plans'),
            ('delete_plan', 'Can delete capital plans'),
        ]
    
    def __str__(self):
        return f"{self.name} (FY{self.fiscal_year})"
    
    @property
    def remaining_budget(self):
        return self.total_budget - self.allocated_budget
    
    @property
    def budget_utilization(self):
        if self.total_budget > 0:
            return (self.allocated_budget / self.total_budget) * 100
        return 0


class CapitalPlanItem(models.Model):
    """
    Individual line items in a capital plan (vehicles, equipment to purchase/replace).
    """
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    ITEM_TYPE_CHOICES = [
        ('replacement', 'Asset Replacement'),
        ('new_purchase', 'New Purchase'),
        ('upgrade', 'Asset Upgrade'),
        ('lease', 'Lease'),
    ]
    
    plan = models.ForeignKey(CapitalPlan, on_delete=models.CASCADE, related_name='items')
    
    # Item details
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Asset reference (stored as scalar to avoid cross-app FK)
    fleet_asset_id = models.IntegerField(null=True, blank=True, 
        help_text="Reference to fleet asset being replaced")
    
    # Description
    description = models.CharField(max_length=500)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Vehicle/Equipment specifications
    asset_type = models.CharField(max_length=100)  # e.g., "Heavy Truck", "Sedan"
    make = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(null=True, blank=True)
    specifications = models.JSONField(default=dict, blank=True)
    
    # Cost information
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Justification
    justification = models.TextField(blank=True)
    expected_service_life = models.IntegerField(
        null=True, blank=True,
        help_text="Expected service life in years"
    )
    
    # Status
    is_approved = models.BooleanField(default=False)
    approval_notes = models.TextField(blank=True)
    
    # Timing
    target_quarter = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="Target quarter for acquisition (1-4)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', '-total_cost']
    
    def __str__(self):
        return f"{self.description} - ${self.total_cost:,.0f}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total cost
        self.total_cost = self.unit_cost * self.quantity
        super().save(*args, **kwargs)


class CapitalPlanScenario(models.Model):
    """
    Alternative scenarios for capital planning (what-if analysis).
    """
    plan = models.ForeignKey(CapitalPlan, on_delete=models.CASCADE, related_name='scenarios')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Budget adjustments
    budget_adjustment = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Positive or negative adjustment to base budget"
    )
    
    # Item modifications stored as JSON
    item_modifications = models.JSONField(
        default=dict,
        help_text="Modifications to plan items (quantities, priorities, etc.)"
    )
    
    # Analysis results
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    items_included = models.IntegerField(default=0)
    items_deferred = models.IntegerField(default=0)
    
    is_primary = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_primary', 'name']
    
    def __str__(self):
        return f"{self.plan.name} - {self.name}"


class CapitalPlanApproval(models.Model):
    """
    Approval workflow for capital plans.
    """
    APPROVAL_LEVELS = [
        ('department', 'Department Head'),
        ('finance', 'Finance Review'),
        ('executive', 'Executive Approval'),
        ('board', 'Board Approval'),
    ]
    
    ACTION_CHOICES = [
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('request_changes', 'Changes Requested'),
    ]
    
    plan = models.ForeignKey(CapitalPlan, on_delete=models.CASCADE, related_name='approvals')
    level = models.CharField(max_length=20, choices=APPROVAL_LEVELS)
    
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    comments = models.TextField(blank=True)
    conditions = models.TextField(blank=True, help_text="Any conditions for approval")
    
    approved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['plan', 'approved_at']
        unique_together = ['plan', 'level']
    
    def __str__(self):
        return f"{self.plan.name} - {self.get_level_display()} - {self.get_action_display()}"


class AssetLifecycle(models.Model):
    """
    Lifecycle tracking for physical assets (Feature 1: Asset Inventory & Lifecycle Tracking)
    """
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('critical', 'Critical'),
    ]
    
    ASSET_CATEGORY_CHOICES = [
        ('building', 'Building'),
        ('vehicle', 'Vehicle'),
        ('equipment', 'Equipment'),
        ('infrastructure', 'Infrastructure'),
        ('technology', 'Technology'),
        ('other', 'Other'),
    ]
    
    # Asset identification
    asset_name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=100)
    asset_category = models.CharField(max_length=50, choices=ASSET_CATEGORY_CHOICES)
    asset_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    # Location
    location = models.CharField(max_length=200)
    department = models.CharField(max_length=100, blank=True)
    
    # Lifecycle dates
    installation_date = models.DateField(help_text="Date asset was installed/commissioned")
    expected_useful_life = models.IntegerField(
        help_text="Expected useful life in years",
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    
    # Financial information
    original_cost = models.DecimalField(max_digits=12, decimal_places=2)
    replacement_cost = models.DecimalField(max_digits=12, decimal_places=2)
    salvage_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Condition tracking
    current_condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    last_condition_assessment = models.DateField(null=True, blank=True)
    condition_notes = models.TextField(blank=True)
    
    # Maintenance tracking
    total_maintenance_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Total lifetime maintenance cost"
    )
    last_maintenance_date = models.DateField(null=True, blank=True)
    maintenance_frequency = models.CharField(
        max_length=50, blank=True,
        help_text="e.g., Monthly, Quarterly, Annually"
    )
    
    # Reference to fleet asset if applicable
    fleet_asset_id = models.IntegerField(null=True, blank=True)
    
    # Metadata
    manufacturer = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    
    # Audit fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_asset_lifecycles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['asset_name']
        indexes = [
            models.Index(fields=['asset_category']),
            models.Index(fields=['current_condition']),
            models.Index(fields=['installation_date']),
        ]
    
    def __str__(self):
        return f"{self.asset_name} ({self.asset_code or 'No Code'})"
    
    @property
    def age_years(self):
        """Calculate current age of asset in years"""
        from datetime import date
        if self.installation_date:
            delta = date.today() - self.installation_date
            return delta.days / 365.25
        return 0
    
    @property
    def remaining_useful_life(self):
        """Calculate remaining useful life in years"""
        return max(0, self.expected_useful_life - self.age_years)
    
    @property
    def estimated_replacement_date(self):
        """Calculate estimated replacement date based on useful life"""
        from datetime import timedelta
        if self.installation_date:
            days = self.expected_useful_life * 365.25
            return self.installation_date + timedelta(days=days)
        return None
    
    @property
    def lifecycle_percentage(self):
        """Calculate percentage of lifecycle consumed"""
        if self.expected_useful_life > 0:
            return min(100, (self.age_years / self.expected_useful_life) * 100)
        return 0
    
    @property
    def maintenance_cost_ratio(self):
        """Calculate ratio of maintenance cost to replacement cost"""
        if self.replacement_cost > 0:
            return (self.total_maintenance_cost / self.replacement_cost) * 100
        return 0


class CapitalProject(models.Model):
    """
    Capital projects for asset replacement, renovation, etc. (Feature 2: Capital Project Planning)
    """
    PROJECT_STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('deferred', 'Deferred'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('critical', 'Critical - Immediate'),
        ('high', 'High - Within 1 Year'),
        ('medium', 'Medium - 1-3 Years'),
        ('low', 'Low - 3+ Years'),
    ]
    
    PROJECT_CATEGORY_CHOICES = [
        ('replacement', 'Asset Replacement'),
        ('renovation', 'Renovation/Upgrade'),
        ('new_construction', 'New Construction'),
        ('infrastructure', 'Infrastructure'),
        ('technology', 'Technology'),
        ('fleet', 'Fleet'),
        ('equipment', 'Equipment'),
        ('other', 'Other'),
    ]
    
    # Project identification
    project_code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Categorization
    category = models.CharField(max_length=50, choices=PROJECT_CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='proposed')
    
    # Planning
    scheduled_year = models.IntegerField(validators=[MinValueValidator(2020), MaxValueValidator(2050)])
    scheduled_quarter = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    
    # Financial
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    approved_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Justification
    business_case = models.TextField(help_text="Business justification for the project")
    benefits = models.TextField(help_text="Expected benefits and outcomes")
    risks = models.TextField(blank=True, help_text="Project risks and mitigation strategies")
    
    # Links to capital plan
    capital_plan = models.ForeignKey(
        CapitalPlan, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='capital_projects'
    )
    
    # Project management
    project_manager = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100)
    stakeholders = models.TextField(blank=True, help_text="Key stakeholders (comma-separated)")
    
    # Timeline
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    
    # Approval tracking
    approval_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_capital_projects'
    )
    
    # Audit fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_capital_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'scheduled_year', 'title']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['scheduled_year']),
        ]
    
    def __str__(self):
        return f"{self.project_code} - {self.title}"
    
    @property
    def budget_variance(self):
        """Calculate budget variance"""
        if self.status == 'completed':
            return self.approved_budget - self.actual_cost
        return self.approved_budget - self.estimated_cost
    
    @property
    def budget_variance_percentage(self):
        """Calculate budget variance as percentage"""
        if self.approved_budget > 0:
            return (self.budget_variance / self.approved_budget) * 100
        return 0


class ProjectAssetLink(models.Model):
    """
    Links capital projects to affected assets
    """
    project = models.ForeignKey(CapitalProject, on_delete=models.CASCADE, related_name='asset_links')
    asset_lifecycle = models.ForeignKey(AssetLifecycle, on_delete=models.CASCADE, related_name='project_links')
    
    RELATIONSHIP_CHOICES = [
        ('replace', 'Replace'),
        ('upgrade', 'Upgrade'),
        ('maintain', 'Maintain'),
        ('decommission', 'Decommission'),
    ]
    
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'asset_lifecycle']
    
    def __str__(self):
        return f"{self.project.title} - {self.asset_lifecycle.asset_name} ({self.get_relationship_type_display()})"
