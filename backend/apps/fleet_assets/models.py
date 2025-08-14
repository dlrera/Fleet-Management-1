import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Asset(models.Model):
    VEHICLE_TYPES = [
        ('bus', 'Bus'),
        ('truck', 'Truck'),
        ('tractor', 'Tractor'),
        ('trailer', 'Trailer'),
        ('van', 'Van'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('pickup', 'Pickup Truck'),
        ('motorcycle', 'Motorcycle'),
        ('equipment', 'Equipment'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('repair', 'In Repair'),
        ('retired', 'Retired'),
        ('sold', 'Sold'),
        ('stolen', 'Stolen/Lost'),
    ]

    # Core Identification
    asset_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_number = models.CharField(max_length=50, unique=True, help_text="Internal asset number")
    
    # Vehicle Information
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(date.today().year + 1)
        ]
    )
    vin_number = models.CharField(max_length=17, unique=True, blank=True, null=True, 
                                 help_text="Vehicle Identification Number")
    license_plate = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    # Ownership and Assignment
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='assets')
    
    # Financial Information
    purchase_date = models.DateField(blank=True, null=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Operational Information
    current_odometer_reading = models.PositiveIntegerField(
        default=0, 
        help_text="Current mileage/hours"
    )
    fuel_type = models.CharField(max_length=30, blank=True, default='')
    fuel_capacity = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    # Status and Condition
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    condition_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        blank=True, null=True,
        help_text="Condition rating from 1 (poor) to 10 (excellent)"
    )
    
    # Additional Information
    notes = models.TextField(blank=True, default='')
    warranty_expiry = models.DateField(blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True, default='')
    insurance_expiry = models.DateField(blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assets_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['asset_number']
        indexes = [
            models.Index(fields=['vehicle_type', 'status']),
            models.Index(fields=['department', 'status']),
            models.Index(fields=['make', 'model']),
        ]

    def __str__(self):
        return f"{self.asset_number} - {self.make} {self.model} ({self.year})"

    @property
    def age_years(self):
        """Calculate age of asset in years"""
        return date.today().year - self.year

    @property
    def is_active(self):
        """Check if asset is in active status"""
        return self.status == 'active'

    @property
    def needs_maintenance(self):
        """Check if asset has overdue maintenance (will be calculated with maintenance records)"""
        # This will be implemented when maintenance models are created
        return False


class AssetDocument(models.Model):
    DOCUMENT_TYPES = [
        ('registration', 'Registration'),
        ('insurance', 'Insurance'),
        ('manual', 'Manual/Documentation'),
        ('inspection', 'Inspection Certificate'),
        ('warranty', 'Warranty Information'),
        ('receipt', 'Purchase Receipt'),
        ('photo', 'Photo'),
        ('other', 'Other'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='asset_documents/')
    description = models.TextField(blank=True, default='')
    expiry_date = models.DateField(blank=True, null=True, help_text="For documents with expiry dates")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.asset.asset_number} - {self.title}"

    @property
    def is_expired(self):
        """Check if document has expired"""
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False

    @property
    def expires_soon(self, days=30):
        """Check if document expires within specified days"""
        if self.expiry_date:
            days_until_expiry = (self.expiry_date - date.today()).days
            return 0 <= days_until_expiry <= days
        return False


class AssetImage(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='asset_images/')
    title = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')
    is_primary = models.BooleanField(default=False, help_text="Primary image for asset")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-uploaded_at']

    def __str__(self):
        return f"{self.asset.asset_number} - {self.title or 'Image'}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per asset
        if self.is_primary:
            AssetImage.objects.filter(asset=self.asset, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
