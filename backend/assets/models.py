from django.db import models
from django.core.validators import MinValueValidator
from PIL import Image
import uuid
import os


def asset_image_upload_path(instance, filename):
    """Generate upload path for asset images"""
    filename = f"{instance.asset_id}_main.jpg"
    return os.path.join('assets', 'images', filename)


def asset_thumbnail_upload_path(instance, filename):
    """Generate upload path for asset thumbnails"""
    filename = f"{instance.asset_id}_thumb.jpg"
    return os.path.join('assets', 'images', 'thumbnails', filename)


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
    
    # Images
    image = models.ImageField(
        upload_to=asset_image_upload_path, 
        blank=True, 
        null=True,
        help_text="Main asset image (recommended: 800x600px, max 5MB)"
    )
    thumbnail = models.ImageField(
        upload_to=asset_thumbnail_upload_path, 
        blank=True, 
        null=True,
        help_text="Auto-generated thumbnail (150x150px)"
    )
    
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
        
        # Process image if provided
        if self.image:
            self._process_image()
        
        super().save(*args, **kwargs)
    
    def _process_image(self):
        """Process and resize the uploaded image, create thumbnail"""
        if not self.image:
            return
            
        # Open the image
        image = Image.open(self.image)
        
        # Convert to RGB if necessary (handles RGBA, P mode images)
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Resize main image to max 800x600 while maintaining aspect ratio
        max_size = (800, 600)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save the resized main image
        from django.core.files.base import ContentFile
        from io import BytesIO
        
        # Save main image
        main_io = BytesIO()
        image.save(main_io, format='JPEG', quality=85, optimize=True)
        main_content = ContentFile(main_io.getvalue())
        
        # Generate filename for main image
        original_name = self.image.name
        name_without_ext = os.path.splitext(os.path.basename(original_name))[0]
        main_filename = f"{self.asset_id}_main.jpg"
        
        # Save main image
        self.image.save(main_filename, main_content, save=False)
        
        # Create thumbnail (150x150)
        thumbnail_image = image.copy()
        thumbnail_size = (150, 150)
        
        # For thumbnails, we'll crop to square to ensure consistent appearance
        width, height = thumbnail_image.size
        
        # Calculate crop box for center square
        if width > height:
            left = (width - height) / 2
            right = (width + height) / 2
            top = 0
            bottom = height
        else:
            left = 0
            right = width
            top = (height - width) / 2
            bottom = (height + width) / 2
        
        # Crop to square
        thumbnail_image = thumbnail_image.crop((left, top, right, bottom))
        
        # Resize to thumbnail size
        thumbnail_image = thumbnail_image.resize(thumbnail_size, Image.Resampling.LANCZOS)
        
        # Save thumbnail
        thumb_io = BytesIO()
        thumbnail_image.save(thumb_io, format='JPEG', quality=85, optimize=True)
        thumb_content = ContentFile(thumb_io.getvalue())
        
        # Generate filename for thumbnail
        thumb_filename = f"{self.asset_id}_thumb.jpg"
        
        # Save thumbnail
        if not self.thumbnail:
            from django.core.files.storage import default_storage
            thumb_path = asset_thumbnail_upload_path(self, thumb_filename)
            self.thumbnail.save(thumb_filename, thumb_content, save=False)
        else:
            self.thumbnail.save(thumb_filename, thumb_content, save=False)
    
    def delete(self, *args, **kwargs):
        """Delete associated image files when asset is deleted"""
        if self.image:
            self.image.delete(save=False)
        if self.thumbnail:
            self.thumbnail.delete(save=False)
        super().delete(*args, **kwargs)


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