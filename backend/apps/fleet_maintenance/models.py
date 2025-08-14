import uuid
from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from decimal import Decimal


class MaintenanceType(models.Model):
    """Defines different types of maintenance activities"""
    
    CATEGORY_CHOICES = [
        ('preventive', 'Preventive Maintenance'),
        ('inspection', 'Inspection'),
        ('safety', 'Safety Check'),
        ('compliance', 'Compliance Requirement'),
        ('seasonal', 'Seasonal Maintenance'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, default='')
    estimated_duration_hours = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    requires_technician = models.BooleanField(default=True)
    requires_parts = models.BooleanField(default=False)
    safety_critical = models.BooleanField(default=False)
    instructions = models.TextField(blank=True, default='', help_text="Step-by-step maintenance instructions")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class MaintenanceSchedule(models.Model):
    """Defines maintenance schedules for assets"""
    
    INTERVAL_TYPES = [
        ('time', 'Time-based (days/months)'),
        ('mileage', 'Mileage-based'),
        ('hours', 'Engine Hours-based'),
        ('manual', 'Manual Schedule'),
    ]

    TIME_UNITS = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years'),
    ]

    schedule_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey('fleet_assets.Asset', on_delete=models.CASCADE, related_name='maintenance_schedules')
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.CASCADE)
    
    # Interval Configuration
    interval_type = models.CharField(max_length=10, choices=INTERVAL_TYPES)
    interval_value = models.PositiveIntegerField(help_text="Interval amount (e.g., 30 for 30 days)")
    time_unit = models.CharField(max_length=10, choices=TIME_UNITS, blank=True, null=True)
    
    # Last Service Information
    last_service_date = models.DateField(blank=True, null=True)
    last_service_mileage = models.PositiveIntegerField(blank=True, null=True)
    last_service_hours = models.PositiveIntegerField(blank=True, null=True)
    
    # Assignment
    assigned_technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_maintenance')
    vendor = models.CharField(max_length=200, blank=True, default='', help_text="External vendor if not done in-house")
    
    # Status
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['asset', 'maintenance_type']
        ordering = ['asset', 'maintenance_type__name']

    def __str__(self):
        return f"{self.asset.asset_number} - {self.maintenance_type.name}"

    def calculate_next_due_date(self):
        """Calculate the next due date based on interval type"""
        if not self.is_active:
            return None
            
        if self.interval_type == 'time':
            if self.last_service_date:
                base_date = self.last_service_date
            else:
                base_date = date.today()
                
            if self.time_unit == 'days':
                return base_date + timedelta(days=self.interval_value)
            elif self.time_unit == 'weeks':
                return base_date + timedelta(weeks=self.interval_value)
            elif self.time_unit == 'months':
                # Approximate months as 30 days
                return base_date + timedelta(days=self.interval_value * 30)
            elif self.time_unit == 'years':
                return base_date + timedelta(days=self.interval_value * 365)
                
        elif self.interval_type in ['mileage', 'hours']:
            # For mileage/hours-based, we need current readings
            current_reading = (self.asset.current_odometer_reading 
                             if self.interval_type == 'mileage' 
                             else getattr(self.asset, 'current_hours', 0))
            
            last_reading = (self.last_service_mileage 
                          if self.interval_type == 'mileage' 
                          else self.last_service_hours or 0)
            
            if current_reading >= (last_reading + self.interval_value):
                return date.today()  # Due now
            else:
                # Estimate based on average usage
                return None  # Cannot calculate without usage data
                
        return None

    @property
    def next_due_date(self):
        """Get the calculated next due date"""
        return self.calculate_next_due_date()

    @property
    def is_due(self):
        """Check if maintenance is currently due"""
        due_date = self.next_due_date
        if due_date:
            return date.today() >= due_date
        return False

    @property
    def is_overdue(self):
        """Check if maintenance is overdue"""
        due_date = self.next_due_date
        if due_date:
            return date.today() > due_date
        return False

    @property
    def days_until_due(self):
        """Calculate days until next due date"""
        due_date = self.next_due_date
        if due_date:
            return (due_date - date.today()).days
        return None


class MaintenanceRecord(models.Model):
    """Records of completed maintenance activities"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('deferred', 'Deferred'),
    ]

    record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey('fleet_assets.Asset', on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.CASCADE)
    schedule = models.ForeignKey(MaintenanceSchedule, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Service Details
    service_date = models.DateField()
    completion_date = models.DateField(blank=True, null=True)
    service_mileage = models.PositiveIntegerField(blank=True, null=True)
    service_hours = models.PositiveIntegerField(blank=True, null=True)
    
    # Personnel
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='performed_maintenance')
    vendor = models.CharField(max_length=200, blank=True, default='')
    technician_notes = models.TextField(blank=True, default='')
    
    # Cost Tracking
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    external_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Vendor/external costs")
    
    # Status and Quality
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    quality_rating = models.PositiveIntegerField(blank=True, null=True, help_text="Quality rating 1-10")
    issues_found = models.TextField(blank=True, default='', help_text="Issues discovered during maintenance")
    recommendations = models.TextField(blank=True, default='', help_text="Recommendations for future maintenance")
    
    # Documentation
    invoice_number = models.CharField(max_length=100, blank=True, default='')
    work_order = models.ForeignKey('fleet_workorders.WorkOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_records')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-service_date', '-created_at']

    def __str__(self):
        return f"{self.asset.asset_number} - {self.maintenance_type.name} ({self.service_date})"

    @property
    def total_cost(self):
        """Calculate total maintenance cost"""
        return self.labor_cost + self.parts_cost + self.external_cost

    def save(self, *args, **kwargs):
        """Update schedule last service info when maintenance is completed"""
        super().save(*args, **kwargs)
        
        if self.status == 'completed' and self.schedule:
            self.schedule.last_service_date = self.completion_date or self.service_date
            if self.service_mileage:
                self.schedule.last_service_mileage = self.service_mileage
            if self.service_hours:
                self.schedule.last_service_hours = self.service_hours
            self.schedule.save()


class MaintenancePart(models.Model):
    """Parts used in maintenance activities"""
    
    part_number = models.CharField(max_length=100)
    part_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    manufacturer = models.CharField(max_length=100, blank=True, default='')
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=0, help_text="Minimum stock level for reorder alerts")
    
    # Compatibility
    compatible_assets = models.ManyToManyField('fleet_assets.Asset', blank=True, related_name='compatible_parts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['part_number', 'manufacturer']
        ordering = ['part_number']

    def __str__(self):
        return f"{self.part_number} - {self.part_name}"

    @property
    def is_low_stock(self):
        """Check if part is below minimum stock level"""
        return self.stock_quantity <= self.minimum_stock


class MaintenancePartUsage(models.Model):
    """Track parts used in specific maintenance records"""
    
    maintenance_record = models.ForeignKey(MaintenanceRecord, on_delete=models.CASCADE, related_name='parts_used')
    part = models.ForeignKey(MaintenancePart, on_delete=models.CASCADE)
    quantity_used = models.PositiveIntegerField()
    unit_cost_at_time = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost per unit at time of use")
    notes = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['maintenance_record', 'part']

    def __str__(self):
        return f"{self.maintenance_record} - {self.part.part_number} (x{self.quantity_used})"

    @property
    def total_cost(self):
        """Calculate total cost for this part usage"""
        return Decimal(self.quantity_used) * self.unit_cost_at_time

    def save(self, *args, **kwargs):
        """Update part stock when usage is recorded"""
        if self.pk is None:  # New record
            self.part.stock_quantity = max(0, self.part.stock_quantity - self.quantity_used)
            self.part.save()
        super().save(*args, **kwargs)
