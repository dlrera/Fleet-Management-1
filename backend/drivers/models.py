from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from PIL import Image
import uuid
import os
from datetime import date, timedelta


def driver_photo_upload_path(instance, filename):
    """Generate upload path for driver photos"""
    filename = f"{instance.driver_id}_photo.jpg"
    return os.path.join('drivers', 'photos', filename)


class Driver(models.Model):
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave'),
    ]
    
    LICENSE_TYPE_CHOICES = [
        ('class_a', 'Class A CDL'),
        ('class_b', 'Class B CDL'),
        ('class_c', 'Class C CDL'),
        ('chauffeur', 'Chauffeur License'),
        ('regular', 'Regular License'),
        ('motorcycle', 'Motorcycle License'),
    ]
    
    # Unique identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver_id = models.CharField(max_length=50, unique=True, help_text="Unique driver identifier")
    
    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    date_of_birth = models.DateField()
    
    # Employment information
    hire_date = models.DateField()
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    employee_number = models.CharField(max_length=50, blank=True, null=True)
    
    # License information
    license_number = models.CharField(max_length=50, unique=True)
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPE_CHOICES)
    license_expiration = models.DateField()
    license_state = models.CharField(max_length=2, help_text="Two-letter state code")
    
    # Address information
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, help_text="Two-letter state code")
    zip_code = models.CharField(max_length=10)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    emergency_contact_relationship = models.CharField(max_length=100)
    
    # Profile photo
    profile_photo = models.ImageField(
        upload_to=driver_photo_upload_path,
        blank=True,
        null=True,
        help_text="Driver profile photo (recommended: 300x300px, max 2MB)"
    )
    
    # Additional information
    notes = models.TextField(blank=True, null=True, help_text="Additional notes or comments")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['driver_id']
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'
    
    def __str__(self):
        return f"{self.driver_id} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def license_expires_soon(self):
        """Check if license expires within 30 days"""
        return self.license_expiration <= date.today() + timedelta(days=30)
    
    @property
    def license_is_expired(self):
        """Check if license is expired"""
        return self.license_expiration < date.today()
    
    @property
    def age(self):
        """Calculate driver age"""
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    def save(self, *args, **kwargs):
        # Auto-generate driver_id if not provided
        if not self.driver_id:
            # Generate driver ID based on last name and current count
            name_prefix = self.last_name[:3].upper()
            count = Driver.objects.count() + 1
            self.driver_id = f"DRV-{name_prefix}-{count:04d}"
        
        # Process profile photo if provided
        if self.profile_photo:
            self._process_photo()
        
        super().save(*args, **kwargs)
    
    def _process_photo(self):
        """Process and resize the uploaded photo"""
        if not self.profile_photo:
            return
            
        # Open the image
        image = Image.open(self.profile_photo)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Resize to max 300x300 while maintaining aspect ratio
        max_size = (300, 300)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save the resized image
        from django.core.files.base import ContentFile
        from io import BytesIO
        
        photo_io = BytesIO()
        image.save(photo_io, format='JPEG', quality=85, optimize=True)
        photo_content = ContentFile(photo_io.getvalue())
        
        # Generate filename
        filename = f"{self.driver_id}_photo.jpg"
        
        # Save photo
        self.profile_photo.save(filename, photo_content, save=False)
    
    def delete(self, *args, **kwargs):
        """Delete associated photo when driver is deleted"""
        if self.profile_photo:
            self.profile_photo.delete(save=False)
        super().delete(*args, **kwargs)


class DriverCertification(models.Model):
    CERTIFICATION_TYPE_CHOICES = [
        ('cdl_passenger', 'CDL Passenger Endorsement'),
        ('cdl_school_bus', 'CDL School Bus Endorsement'),
        ('cdl_hazmat', 'CDL Hazmat Endorsement'),
        ('cdl_air_brakes', 'CDL Air Brakes'),
        ('defensive_driving', 'Defensive Driving'),
        ('first_aid', 'First Aid'),
        ('cpr', 'CPR'),
        ('drug_alcohol_awareness', 'Drug & Alcohol Awareness'),
        ('safety_training', 'Safety Training'),
        ('dot_medical', 'DOT Medical Certificate'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='certifications')
    certification_type = models.CharField(max_length=30, choices=CERTIFICATION_TYPE_CHOICES)
    certification_number = models.CharField(max_length=100, blank=True, null=True)
    certification_name = models.CharField(max_length=200, help_text="Custom certification name if 'other'")
    
    issued_date = models.DateField()
    expiration_date = models.DateField(blank=True, null=True)
    issuing_authority = models.CharField(max_length=200)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)
    
    # Document attachment
    certificate_document = models.FileField(
        upload_to='drivers/certifications/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Upload certificate document (PDF, JPG, PNG)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expiration_date']
        unique_together = ['driver', 'certification_type', 'certification_number']
    
    def __str__(self):
        return f"{self.driver.driver_id} - {self.get_certification_type_display()}"
    
    @property
    def expires_soon(self):
        """Check if certification expires within 30 days"""
        if not self.expiration_date:
            return False
        return self.expiration_date <= date.today() + timedelta(days=30)
    
    @property
    def is_expired(self):
        """Check if certification is expired"""
        if not self.expiration_date:
            return False
        return self.expiration_date < date.today()


class DriverAssetAssignment(models.Model):
    ASSIGNMENT_TYPE_CHOICES = [
        ('primary', 'Primary Driver'),
        ('secondary', 'Secondary Driver'),
        ('temporary', 'Temporary Assignment'),
        ('backup', 'Backup Driver'),
        ('shared', 'Shared Assignment'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='asset_assignments')
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='driver_assignments')
    
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPE_CHOICES, default='primary')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    assigned_date = models.DateTimeField()
    unassigned_date = models.DateTimeField(blank=True, null=True)
    
    assigned_by = models.CharField(max_length=200, help_text="Person who made the assignment")
    notes = models.TextField(blank=True, null=True)
    
    # Priority for assignment type (1 = highest priority)
    priority = models.PositiveIntegerField(default=1, help_text="Assignment priority (1 = highest)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', '-assigned_date']
        # Allow multiple drivers per asset, but unique combination of driver-asset-assignment_type for active assignments
        unique_together = []
        
    def __str__(self):
        return f"{self.driver.driver_id} → {self.asset.asset_id} ({self.assignment_type})"
    
    @property
    def is_current(self):
        """Check if this is a current active assignment"""
        return self.status == 'active' and self.unassigned_date is None
    
    @property
    def duration_days(self):
        """Calculate assignment duration in days"""
        end_date = self.unassigned_date or timezone.now()
        return (end_date.date() - self.assigned_date.date()).days
    
    def clean(self):
        """Custom validation for assignment rules"""
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        # Allow multiple drivers per asset with different assignment types
        # Only validate that we don't have duplicate active assignments for same driver-asset-type combination
        if self.status == 'active' and not self.unassigned_date:
            existing = DriverAssetAssignment.objects.filter(
                driver=self.driver,
                asset=self.asset,
                assignment_type=self.assignment_type,
                status='active',
                unassigned_date__isnull=True
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError(
                    f"Driver {self.driver.driver_id} already has an active {self.assignment_type} assignment to asset {self.asset.asset_id}"
                )
    
    def save(self, *args, **kwargs):
        # Remove full_clean() to avoid validation conflicts with DRF serializers
        # Validation is handled by the serializers instead
        super().save(*args, **kwargs)


class DriverViolation(models.Model):
    VIOLATION_TYPE_CHOICES = [
        ('traffic', 'Traffic Violation'),
        ('moving', 'Moving Violation'),
        ('parking', 'Parking Violation'),
        ('equipment', 'Equipment Violation'),
        ('safety', 'Safety Violation'),
        ('drug_alcohol', 'Drug/Alcohol Violation'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('minor', 'Minor'),
        ('major', 'Major'),
        ('serious', 'Serious'),
        ('critical', 'Critical'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='violations')
    
    violation_type = models.CharField(max_length=20, choices=VIOLATION_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField()
    
    violation_date = models.DateField()
    citation_number = models.CharField(max_length=100, blank=True, null=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Asset involved (if applicable)
    asset = models.ForeignKey('assets.Asset', on_delete=models.SET_NULL, blank=True, null=True)
    
    # Resolution
    resolved = models.BooleanField(default=False)
    resolution_date = models.DateField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-violation_date']
    
    def __str__(self):
        return f"{self.driver.driver_id} - {self.get_violation_type_display()} ({self.violation_date})"
