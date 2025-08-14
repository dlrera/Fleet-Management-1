import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timedelta


class WorkOrder(models.Model):
    """Work orders for maintenance and repair tasks"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
        ('critical', 'Critical'),
        ('emergency', 'Emergency'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('closed', 'Closed'),
    ]

    TYPE_CHOICES = [
        ('preventive', 'Preventive Maintenance'),
        ('corrective', 'Corrective Maintenance'),
        ('repair', 'Repair'),
        ('inspection', 'Inspection'),
        ('emergency', 'Emergency Repair'),
        ('modification', 'Modification'),
        ('other', 'Other'),
    ]

    # Core Information
    work_order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order_number = models.CharField(max_length=50, unique=True, help_text="Human-readable work order number")
    
    # Asset and Problem Information
    asset = models.ForeignKey('fleet_assets.Asset', on_delete=models.CASCADE, related_name='work_orders')
    title = models.CharField(max_length=200, help_text="Brief description of the work")
    description = models.TextField(help_text="Detailed description of the issue or task")
    work_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Priority and Scheduling
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    requested_completion_date = models.DateField(blank=True, null=True)
    scheduled_start_date = models.DateField(blank=True, null=True)
    scheduled_end_date = models.DateField(blank=True, null=True)
    
    # Personnel Assignment
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_work_orders')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_work_orders')
    department = models.ForeignKey('fleet_assets.Department', on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.CharField(max_length=200, blank=True, default='', help_text="External vendor if outsourced")
    
    # Status and Progress
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text="Work completion percentage"
    )
    
    # Cost Tracking
    estimated_labor_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    actual_labor_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    external_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional Information
    location = models.CharField(max_length=200, blank=True, default='', help_text="Work location")
    safety_requirements = models.TextField(blank=True, default='', help_text="Special safety requirements")
    tools_required = models.TextField(blank=True, default='', help_text="Special tools or equipment needed")
    notes = models.TextField(blank=True, default='')
    
    # Related Records
    maintenance_record = models.OneToOneField(
        'fleet_maintenance.MaintenanceRecord', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='linked_work_order'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['asset', 'status']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f"{self.work_order_number} - {self.title}"

    @property
    def total_cost(self):
        """Calculate total work order cost"""
        return self.labor_cost + self.parts_cost + self.external_cost

    @property
    def is_overdue(self):
        """Check if work order is overdue"""
        if self.requested_completion_date and self.status not in ['completed', 'cancelled', 'closed']:
            return date.today() > self.requested_completion_date
        return False

    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.requested_completion_date:
            return (self.requested_completion_date - date.today()).days
        return None

    @property
    def duration_days(self):
        """Calculate actual duration in days"""
        if self.started_at and self.completed_at:
            return (self.completed_at.date() - self.started_at.date()).days
        return None

    def save(self, *args, **kwargs):
        """Auto-generate work order number if not provided"""
        if not self.work_order_number:
            # Generate work order number based on date and sequence
            today = date.today()
            prefix = f"WO{today.strftime('%Y%m%d')}"
            
            # Get the last work order number for today
            last_wo = WorkOrder.objects.filter(
                work_order_number__startswith=prefix
            ).order_by('-work_order_number').first()
            
            if last_wo:
                # Extract sequence number and increment
                try:
                    seq = int(last_wo.work_order_number[-3:]) + 1
                except:
                    seq = 1
            else:
                seq = 1
                
            self.work_order_number = f"{prefix}{seq:03d}"
        
        super().save(*args, **kwargs)


class WorkOrderPhoto(models.Model):
    """Photos attached to work orders"""
    
    PHOTO_TYPES = [
        ('before', 'Before Work'),
        ('during', 'During Work'),
        ('after', 'After Work'),
        ('damage', 'Damage Documentation'),
        ('parts', 'Parts/Components'),
        ('other', 'Other'),
    ]

    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='work_order_photos/')
    photo_type = models.CharField(max_length=10, choices=PHOTO_TYPES, default='other')
    title = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.work_order.work_order_number} - {self.title or 'Photo'}"


class WorkOrderDocument(models.Model):
    """Documents attached to work orders"""
    
    DOCUMENT_TYPES = [
        ('manual', 'Manual/Instructions'),
        ('schematic', 'Schematic/Diagram'),
        ('invoice', 'Invoice/Receipt'),
        ('report', 'Report'),
        ('certificate', 'Certificate'),
        ('estimate', 'Cost Estimate'),
        ('other', 'Other'),
    ]

    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='work_order_documents/')
    document_type = models.CharField(max_length=15, choices=DOCUMENT_TYPES, default='other')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.work_order.work_order_number} - {self.title}"


class WorkOrderComment(models.Model):
    """Comments/updates on work orders"""
    
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(default=True, help_text="Internal comment not visible to external users")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.work_order.work_order_number} - Comment by {self.created_by.username}"


class WorkOrderStatusHistory(models.Model):
    """Track status changes for work orders"""
    
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=15, choices=WorkOrder.STATUS_CHOICES, blank=True, null=True)
    new_status = models.CharField(max_length=15, choices=WorkOrder.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, default='', help_text="Reason for status change")

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.work_order.work_order_number}: {self.old_status} → {self.new_status}"


class WorkOrderChecklist(models.Model):
    """Checklists for work orders"""
    
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='checklists')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.work_order.work_order_number} - {self.title}"


class WorkOrderChecklistItem(models.Model):
    """Individual items in a checklist"""
    
    checklist = models.ForeignKey(WorkOrderChecklist, on_delete=models.CASCADE, related_name='items')
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['order', 'description']

    def __str__(self):
        return f"{self.checklist.title} - Item {self.order}"

    def save(self, *args, **kwargs):
        """Set completion timestamp when item is marked complete"""
        if self.is_completed and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        elif not self.is_completed:
            self.completed_at = None
            self.completed_by = None
        
        super().save(*args, **kwargs)
