from django.db import models
from django.core.validators import MinValueValidator
import uuid


class Asset(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('bus', 'Bus'),
        ('truck', 'Truck'),
        ('tractor', 'Tractor'),
        ('trailer', 'Trailer'),
        ('van', 'Van'),
        ('car', 'Car'),
        ('equipment', 'Equipment'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
        ('out_of_service', 'Out of Service'),
    ]
    
    # Unique identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_id = models.CharField(max_length=50, unique=True, help_text="Unique asset identifier")
    
    # Vehicle information
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField(validators=[MinValueValidator(1900)])
    vin = models.CharField(max_length=17, unique=True, blank=True, null=True, help_text="Vehicle Identification Number")
    license_plate = models.CharField(max_length=20, blank=True, null=True)
    
    # Assignment and ownership
    department = models.CharField(max_length=100, blank=True, null=True, help_text="Department or owner assignment")
    
    # Financial information
    purchase_date = models.DateField(blank=True, null=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Operational information
    current_odometer = models.PositiveIntegerField(default=0, help_text="Current odometer/hour reading")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Additional information
    notes = models.TextField(blank=True, null=True, help_text="Additional notes or comments")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['asset_id']
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'
    
    def __str__(self):
        return f"{self.asset_id} - {self.year} {self.make} {self.model}"
    
    def save(self, *args, **kwargs):
        # Auto-generate asset_id if not provided
        if not self.asset_id:
            # Generate asset ID based on vehicle type and current count
            type_prefix = self.vehicle_type.upper()[:3]
            count = Asset.objects.filter(vehicle_type=self.vehicle_type).count() + 1
            self.asset_id = f"{type_prefix}-{count:04d}"
        super().save(*args, **kwargs)


class AssetDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('registration', 'Registration'),
        ('insurance', 'Insurance'),
        ('manual', 'Manual'),
        ('maintenance', 'Maintenance Record'),
        ('inspection', 'Inspection Report'),
        ('photo', 'Photo'),
        ('other', 'Other'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='assets/documents/%Y/%m/%d/')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.asset.asset_id} - {self.title}"