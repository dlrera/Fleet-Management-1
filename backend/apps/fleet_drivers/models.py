import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import date, timedelta


class Driver(models.Model):
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
    ]

    LICENSE_CLASS_CHOICES = [
        ('regular', 'Regular License'),
        ('cdl_a', 'CDL Class A'),
        ('cdl_b', 'CDL Class B'),
        ('cdl_c', 'CDL Class C'),
        ('motorcycle', 'Motorcycle License'),
        ('chauffeur', 'Chauffeur License'),
    ]

    # Core Information
    driver_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    # Personal Information
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')],
        blank=True,
        help_text="Phone number format: +1234567890"
    )
    address = models.TextField(blank=True, default='')
    date_of_birth = models.DateField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, default='')
    emergency_contact_phone = models.CharField(max_length=15, blank=True, default='')
    
    # License Information
    license_number = models.CharField(max_length=50, unique=True)
    license_class = models.CharField(max_length=20, choices=LICENSE_CLASS_CHOICES)
    license_state = models.CharField(max_length=2, help_text="State abbreviation (e.g., CA, NY)")
    license_issue_date = models.DateField()
    license_expiry_date = models.DateField()
    
    # Employment Information
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    hire_date = models.DateField()
    termination_date = models.DateField(blank=True, null=True)
    department = models.ForeignKey('fleet_assets.Department', on_delete=models.CASCADE, related_name='drivers')
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_drivers')
    
    # Medical Information
    medical_exam_date = models.DateField(blank=True, null=True)
    medical_exam_expiry = models.DateField(blank=True, null=True)
    has_medical_restrictions = models.BooleanField(default=False)
    medical_restrictions = models.TextField(blank=True, default='')
    
    # Performance and Safety
    safety_rating = models.PositiveIntegerField(
        default=5,
        help_text="Safety rating from 1 (poor) to 10 (excellent)"
    )
    total_miles_driven = models.PositiveIntegerField(default=0)
    total_incidents = models.PositiveIntegerField(default=0)
    last_training_date = models.DateField(blank=True, null=True)
    
    # Additional Information
    notes = models.TextField(blank=True, default='')
    profile_photo = models.ImageField(upload_to='driver_photos/', blank=True, null=True)
    
    # Assigned Vehicles (Many-to-Many relationship)
    assigned_vehicles = models.ManyToManyField('fleet_assets.Asset', blank=True, related_name='assigned_drivers')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['employment_status', 'license_expiry_date']),
            models.Index(fields=['department', 'employment_status']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id or self.license_number})"

    @property
    def full_name(self):
        """Get driver's full name"""
        return self.user.get_full_name()

    @property
    def is_active(self):
        """Check if driver is active"""
        return self.employment_status == 'active'

    @property
    def license_expires_soon(self, days=30):
        """Check if license expires within specified days"""
        if self.license_expiry_date:
            days_until_expiry = (self.license_expiry_date - date.today()).days
            return 0 <= days_until_expiry <= days
        return False

    @property
    def is_license_expired(self):
        """Check if license has expired"""
        return date.today() > self.license_expiry_date

    @property
    def medical_expires_soon(self, days=30):
        """Check if medical exam expires within specified days"""
        if self.medical_exam_expiry:
            days_until_expiry = (self.medical_exam_expiry - date.today()).days
            return 0 <= days_until_expiry <= days
        return False

    @property
    def is_medical_expired(self):
        """Check if medical exam has expired"""
        if self.medical_exam_expiry:
            return date.today() > self.medical_exam_expiry
        return False

    @property
    def age(self):
        """Calculate driver's age"""
        if self.date_of_birth:
            return (date.today() - self.date_of_birth).days // 365
        return None

    @property
    def years_of_service(self):
        """Calculate years of service"""
        return (date.today() - self.hire_date).days // 365


class DriverCertification(models.Model):
    CERTIFICATION_TYPES = [
        ('cdl_passenger', 'CDL Passenger Endorsement'),
        ('cdl_school_bus', 'CDL School Bus Endorsement'),
        ('cdl_hazmat', 'CDL Hazmat Endorsement'),
        ('defensive_driving', 'Defensive Driving'),
        ('first_aid', 'First Aid Certification'),
        ('forklift', 'Forklift Operation'),
        ('crane', 'Crane Operation'),
        ('dot_medical', 'DOT Medical Certificate'),
        ('safety_training', 'Safety Training'),
        ('other', 'Other Certification'),
    ]

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='certifications')
    certification_type = models.CharField(max_length=30, choices=CERTIFICATION_TYPES)
    certification_name = models.CharField(max_length=200)
    certification_number = models.CharField(max_length=100, blank=True, default='')
    issuing_authority = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    is_required = models.BooleanField(default=False, help_text="Required for driver's role")
    document = models.FileField(upload_to='driver_certifications/', blank=True, null=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expiry_date']
        unique_together = ['driver', 'certification_type', 'certification_number']

    def __str__(self):
        return f"{self.driver.full_name} - {self.certification_name}"

    @property
    def is_expired(self):
        """Check if certification has expired"""
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False

    @property
    def expires_soon(self, days=30):
        """Check if certification expires within specified days"""
        if self.expiry_date:
            days_until_expiry = (self.expiry_date - date.today()).days
            return 0 <= days_until_expiry <= days
        return False


class DriverIncident(models.Model):
    INCIDENT_TYPES = [
        ('accident', 'Vehicle Accident'),
        ('traffic_violation', 'Traffic Violation'),
        ('safety_violation', 'Safety Violation'),
        ('policy_violation', 'Policy Violation'),
        ('customer_complaint', 'Customer Complaint'),
        ('commendation', 'Commendation'),
        ('other', 'Other'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='incidents')
    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    incident_date = models.DateField()
    description = models.TextField()
    location = models.CharField(max_length=500, blank=True, default='')
    vehicle = models.ForeignKey('fleet_assets.Asset', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Actions and Resolution
    action_taken = models.TextField(blank=True, default='')
    resolved = models.BooleanField(default=False)
    resolution_date = models.DateField(blank=True, null=True)
    
    # Cost Impact
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    insurance_claim_number = models.CharField(max_length=100, blank=True, default='')
    
    # Documentation
    police_report_number = models.CharField(max_length=100, blank=True, default='')
    documents = models.FileField(upload_to='incident_documents/', blank=True, null=True)
    
    # Metadata
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-incident_date', '-created_at']

    def __str__(self):
        return f"{self.driver.full_name} - {self.get_incident_type_display()} ({self.incident_date})"


class DriverTraining(models.Model):
    TRAINING_TYPES = [
        ('safety', 'Safety Training'),
        ('defensive_driving', 'Defensive Driving'),
        ('vehicle_operation', 'Vehicle Operation'),
        ('customer_service', 'Customer Service'),
        ('compliance', 'Compliance Training'),
        ('emergency_procedures', 'Emergency Procedures'),
        ('other', 'Other Training'),
    ]

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='training_records')
    training_type = models.CharField(max_length=30, choices=TRAINING_TYPES)
    training_name = models.CharField(max_length=200)
    instructor = models.CharField(max_length=100, blank=True, default='')
    training_date = models.DateField()
    completion_date = models.DateField(blank=True, null=True)
    hours_completed = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_required = models.BooleanField(default=False)
    passed = models.BooleanField(default=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Training score (percentage)")
    certificate = models.FileField(upload_to='training_certificates/', blank=True, null=True)
    notes = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-training_date']

    def __str__(self):
        return f"{self.driver.full_name} - {self.training_name} ({self.training_date})"
