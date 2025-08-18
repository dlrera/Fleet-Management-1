from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from datetime import date, datetime
import uuid
import os
import tempfile
from PIL import Image
import io

from .models import Asset, AssetDocument


class AssetModelTestCase(TestCase):
    """Test cases for Asset model"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_asset_data = {
            'vehicle_type': 'truck',
            'make': 'Ford',
            'model': 'F-150',
            'year': 2022,
            'vin': '1FTFW1ET5DFC10312',
            'license_plate': 'ABC123',
            'department': 'Operations',
            'purchase_date': date(2022, 1, 15),
            'purchase_cost': Decimal('35000.00'),
            'current_odometer': 15000,
            'status': 'active',
            'notes': 'Fleet vehicle for operations department'
        }
    
    def test_asset_creation_with_all_fields(self):
        """Test creating an asset with all fields"""
        asset = Asset.objects.create(**self.valid_asset_data)
        
        self.assertIsInstance(asset.id, uuid.UUID)
        self.assertEqual(asset.vehicle_type, 'truck')
        self.assertEqual(asset.make, 'Ford')
        self.assertEqual(asset.model, 'F-150')
        self.assertEqual(asset.year, 2022)
        self.assertEqual(asset.vin, '1FTFW1ET5DFC10312')
        self.assertEqual(asset.license_plate, 'ABC123')
        self.assertEqual(asset.department, 'Operations')
        self.assertEqual(asset.purchase_date, date(2022, 1, 15))
        self.assertEqual(asset.purchase_cost, Decimal('35000.00'))
        self.assertEqual(asset.current_odometer, 15000)
        self.assertEqual(asset.status, 'active')
        self.assertEqual(asset.notes, 'Fleet vehicle for operations department')
        self.assertIsNotNone(asset.created_at)
        self.assertIsNotNone(asset.updated_at)
    
    def test_asset_creation_minimal_fields(self):
        """Test creating an asset with only required fields"""
        minimal_data = {
            'vehicle_type': 'bus',
            'make': 'Mercedes',
            'model': 'Sprinter',
            'year': 2021
        }
        asset = Asset.objects.create(**minimal_data)
        
        self.assertEqual(asset.vehicle_type, 'bus')
        self.assertEqual(asset.make, 'Mercedes')
        self.assertEqual(asset.model, 'Sprinter')
        self.assertEqual(asset.year, 2021)
        self.assertEqual(asset.current_odometer, 0)  # default value
        self.assertEqual(asset.status, 'active')  # default value
        self.assertIsNotNone(asset.asset_id)  # auto-generated
    
    def test_asset_id_auto_generation(self):
        """Test that asset_id is auto-generated based on vehicle type"""
        # Create first truck
        asset1 = Asset.objects.create(
            vehicle_type='truck',
            make='Ford',
            model='F-150',
            year=2022
        )
        self.assertEqual(asset1.asset_id, 'TRU-0001')
        
        # Create second truck
        asset2 = Asset.objects.create(
            vehicle_type='truck',
            make='Chevrolet',
            model='Silverado',
            year=2023
        )
        self.assertEqual(asset2.asset_id, 'TRU-0002')
        
        # Create first bus
        asset3 = Asset.objects.create(
            vehicle_type='bus',
            make='Mercedes',
            model='Sprinter',
            year=2021
        )
        self.assertEqual(asset3.asset_id, 'BUS-0001')
    
    def test_custom_asset_id(self):
        """Test creating asset with custom asset_id"""
        asset = Asset.objects.create(
            asset_id='CUSTOM-001',
            vehicle_type='van',
            make='Ford',
            model='Transit',
            year=2022
        )
        self.assertEqual(asset.asset_id, 'CUSTOM-001')
    
    def test_asset_id_uniqueness(self):
        """Test that asset_id must be unique"""
        Asset.objects.create(
            asset_id='UNIQUE-001',
            vehicle_type='car',
            make='Toyota',
            model='Camry',
            year=2022
        )
        
        with self.assertRaises(IntegrityError):
            Asset.objects.create(
                asset_id='UNIQUE-001',
                vehicle_type='car',
                make='Honda',
                model='Accord',
                year=2022
            )
    
    def test_vin_uniqueness(self):
        """Test that VIN must be unique"""
        vin = '1FTFW1ET5DFC10312'
        Asset.objects.create(
            vehicle_type='truck',
            make='Ford',
            model='F-150',
            year=2022,
            vin=vin
        )
        
        with self.assertRaises(IntegrityError):
            Asset.objects.create(
                vehicle_type='truck',
                make='Ford',
                model='F-250',
                year=2023,
                vin=vin
            )
    
    def test_vin_can_be_blank(self):
        """Test that VIN can be blank or null"""
        asset1 = Asset.objects.create(
            vehicle_type='equipment',
            make='Caterpillar',
            model='Excavator',
            year=2020,
            vin=None
        )
        asset2 = Asset.objects.create(
            vehicle_type='equipment',
            make='John Deere',
            model='Loader',
            year=2021,
            vin=''
        )
        
        self.assertIsNone(asset1.vin)
        self.assertEqual(asset2.vin, '')
    
    def test_year_validation(self):
        """Test year field validation"""
        # Test minimum year validation
        with self.assertRaises(ValidationError):
            asset = Asset(
                vehicle_type='car',
                make='Ford',
                model='Model T',
                year=1899  # Below minimum
            )
            asset.full_clean()
    
    def test_vehicle_type_choices(self):
        """Test vehicle type choices validation"""
        valid_types = ['bus', 'truck', 'tractor', 'trailer', 'van', 'car', 'equipment', 'other']
        
        for i, vehicle_type in enumerate(valid_types):
            asset = Asset.objects.create(
                asset_id=f'TEST-{vehicle_type.upper()}-{i:03d}',  # Ensure unique asset_id
                vehicle_type=vehicle_type,
                make='Test',
                model=f'Model{i}',
                year=2022
            )
            self.assertEqual(asset.vehicle_type, vehicle_type)
    
    def test_status_choices(self):
        """Test status choices validation"""
        valid_statuses = ['active', 'maintenance', 'retired', 'out_of_service']
        
        for i, status in enumerate(valid_statuses):
            asset = Asset.objects.create(
                asset_id=f'STATUS-{status.upper()}-{i:03d}',  # Ensure unique asset_id
                vehicle_type='car',
                make='Test',
                model=f'Model{i}',
                year=2022,
                status=status
            )
            self.assertEqual(asset.status, status)
    
    def test_str_method(self):
        """Test the __str__ method"""
        asset = Asset.objects.create(**self.valid_asset_data)
        expected_str = f"{asset.asset_id} - 2022 Ford F-150"
        self.assertEqual(str(asset), expected_str)
    
    def test_meta_ordering(self):
        """Test default ordering by asset_id"""
        Asset.objects.create(asset_id='Z-001', vehicle_type='car', make='BMW', model='X3', year=2022)
        Asset.objects.create(asset_id='A-001', vehicle_type='car', make='Audi', model='A4', year=2022)
        Asset.objects.create(asset_id='M-001', vehicle_type='car', make='Mercedes', model='C-Class', year=2022)
        
        assets = list(Asset.objects.all())
        asset_ids = [asset.asset_id for asset in assets]
        self.assertEqual(asset_ids, ['A-001', 'M-001', 'Z-001'])


class AssetDocumentModelTestCase(TestCase):
    """Test cases for AssetDocument model"""
    
    def setUp(self):
        """Set up test data"""
        self.asset = Asset.objects.create(
            vehicle_type='truck',
            make='Ford',
            model='F-150',
            year=2022
        )
        
        # Create a test file
        self.test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
    
    def test_document_creation(self):
        """Test creating an asset document"""
        document = AssetDocument.objects.create(
            asset=self.asset,
            document_type='registration',
            title='Vehicle Registration',
            file=self.test_file,
            description='Primary vehicle registration document'
        )
        
        self.assertEqual(document.asset, self.asset)
        self.assertEqual(document.document_type, 'registration')
        self.assertEqual(document.title, 'Vehicle Registration')
        self.assertEqual(document.description, 'Primary vehicle registration document')
        self.assertIsNotNone(document.uploaded_at)
        self.assertTrue(document.file.name.startswith('assets/documents/'))
    
    def test_document_type_choices(self):
        """Test document type choices"""
        valid_types = ['registration', 'insurance', 'manual', 'maintenance', 'inspection', 'photo', 'other']
        
        for doc_type in valid_types:
            document = AssetDocument.objects.create(
                asset=self.asset,
                document_type=doc_type,
                title=f'Test {doc_type}',
                file=SimpleUploadedFile(f"test_{doc_type}.pdf", b"content", content_type="application/pdf")
            )
            self.assertEqual(document.document_type, doc_type)
    
    def test_document_cascade_delete(self):
        """Test that documents are deleted when asset is deleted"""
        document = AssetDocument.objects.create(
            asset=self.asset,
            document_type='photo',
            title='Vehicle Photo',
            file=self.test_file
        )
        
        document_id = document.id
        self.assertTrue(AssetDocument.objects.filter(id=document_id).exists())
        
        # Delete the asset
        self.asset.delete()
        
        # Document should be deleted too
        self.assertFalse(AssetDocument.objects.filter(id=document_id).exists())
    
    def test_document_str_method(self):
        """Test the __str__ method"""
        document = AssetDocument.objects.create(
            asset=self.asset,
            document_type='insurance',
            title='Insurance Policy',
            file=self.test_file
        )
        
        expected_str = f"{self.asset.asset_id} - Insurance Policy"
        self.assertEqual(str(document), expected_str)
    
    def test_document_ordering(self):
        """Test documents are ordered by upload date (newest first)"""
        import time
        
        doc1 = AssetDocument.objects.create(
            asset=self.asset,
            document_type='registration',
            title='Old Document',
            file=SimpleUploadedFile("old.pdf", b"content", content_type="application/pdf")
        )
        
        # Small delay to ensure different timestamps
        time.sleep(0.01)
        
        doc2 = AssetDocument.objects.create(
            asset=self.asset,
            document_type='insurance',
            title='New Document',
            file=SimpleUploadedFile("new.pdf", b"content", content_type="application/pdf")
        )
        
        documents = list(AssetDocument.objects.all())
        self.assertEqual(documents[0], doc2)  # Newest first
        self.assertEqual(documents[1], doc1)
    
    def test_related_name(self):
        """Test accessing documents through asset"""
        doc1 = AssetDocument.objects.create(
            asset=self.asset,
            document_type='registration',
            title='Registration',
            file=SimpleUploadedFile("reg.pdf", b"content", content_type="application/pdf")
        )
        
        doc2 = AssetDocument.objects.create(
            asset=self.asset,
            document_type='insurance',
            title='Insurance',
            file=SimpleUploadedFile("ins.pdf", b"content", content_type="application/pdf")
        )
        
        asset_documents = self.asset.documents.all()
        self.assertEqual(asset_documents.count(), 2)
        self.assertIn(doc1, asset_documents)
        self.assertIn(doc2, asset_documents)


class AssetImageTestCase(TestCase):
    """Test cases for Asset image functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.asset = Asset.objects.create(
            vehicle_type='truck',
            make='Ford',
            model='F-150',
            year=2022
        )
    
    def create_test_image(self, filename='test_image.jpg', format='JPEG', size=(1200, 900), color='red'):
        """Create a test image file"""
        image = Image.new('RGB', size, color)
        image_io = io.BytesIO()
        image.save(image_io, format=format)
        image_io.seek(0)
        
        return SimpleUploadedFile(
            filename,
            image_io.read(),
            content_type=f'image/{format.lower()}'
        )
    
    def test_asset_image_upload(self):
        """Test uploading an image to an asset"""
        test_image = self.create_test_image()
        
        self.asset.image = test_image
        self.asset.save()
        
        self.assertTrue(self.asset.image)
        self.assertTrue(self.asset.image.name.startswith('assets/images/'))
        self.assertIn('_main', self.asset.image.name)
        self.assertTrue(self.asset.image.name.endswith('.jpg'))
    
    def test_asset_thumbnail_generation(self):
        """Test that thumbnail is automatically generated"""
        test_image = self.create_test_image(size=(1600, 1200))
        
        self.asset.image = test_image
        self.asset.save()
        
        # Thumbnail should be generated automatically
        self.assertTrue(self.asset.thumbnail)
        self.assertTrue(self.asset.thumbnail.name.startswith('assets/images/thumbnails/'))
        self.assertIn('_thumb', self.asset.thumbnail.name)
        self.assertTrue(self.asset.thumbnail.name.endswith('.jpg'))
    
    def test_image_resizing(self):
        """Test that large images are resized to max 800x600"""
        # Create a large image
        test_image = self.create_test_image(size=(2000, 1500))
        
        self.asset.image = test_image
        self.asset.save()
        
        # Open the saved image and check dimensions
        with Image.open(self.asset.image.path) as img:
            width, height = img.size
            # Should be resized to fit within 800x600 while maintaining aspect ratio
            self.assertLessEqual(width, 800)
            self.assertLessEqual(height, 600)
            # Aspect ratio should be maintained (2000:1500 = 4:3)
            self.assertAlmostEqual(width / height, 4/3, places=1)
    
    def test_thumbnail_size(self):
        """Test that thumbnail is exactly 150x150"""
        test_image = self.create_test_image(size=(1600, 800))  # Wide image
        
        self.asset.image = test_image
        self.asset.save()
        
        # Check thumbnail dimensions
        with Image.open(self.asset.thumbnail.path) as thumb:
            width, height = thumb.size
            self.assertEqual(width, 150)
            self.assertEqual(height, 150)
    
    def test_image_format_conversion(self):
        """Test that images are converted to JPEG"""
        # Create a PNG image
        test_image = self.create_test_image(filename='test.png', format='PNG')
        
        self.asset.image = test_image
        self.asset.save()
        
        # Both main image and thumbnail should be JPEG
        with Image.open(self.asset.image.path) as img:
            self.assertEqual(img.format, 'JPEG')
        
        with Image.open(self.asset.thumbnail.path) as thumb:
            self.assertEqual(thumb.format, 'JPEG')
    
    def test_image_cleanup_on_delete(self):
        """Test that images are cleaned up when asset is deleted"""
        test_image = self.create_test_image()
        
        self.asset.image = test_image
        self.asset.save()
        
        # Store file paths
        image_path = self.asset.image.path
        thumbnail_path = self.asset.thumbnail.path
        
        # Files should exist
        self.assertTrue(os.path.exists(image_path))
        self.assertTrue(os.path.exists(thumbnail_path))
        
        # Delete the asset
        self.asset.delete()
        
        # Files should be cleaned up
        self.assertFalse(os.path.exists(image_path))
        self.assertFalse(os.path.exists(thumbnail_path))
    
    def test_image_replacement(self):
        """Test replacing an existing image"""
        # Upload first image
        first_image = self.create_test_image(color='red')
        self.asset.image = first_image
        self.asset.save()
        
        first_image_name = self.asset.image.name
        first_thumbnail_name = self.asset.thumbnail.name
        
        # Replace with second image
        second_image = self.create_test_image(color='blue')
        self.asset.image = second_image
        self.asset.save()
        
        # New image names should be different
        self.assertNotEqual(self.asset.image.name, first_image_name)
        self.assertNotEqual(self.asset.thumbnail.name, first_thumbnail_name)
        
        # New files should exist
        self.assertTrue(os.path.exists(self.asset.image.path))
        self.assertTrue(os.path.exists(self.asset.thumbnail.path))
    
    def test_no_image_upload(self):
        """Test asset without image"""
        # Asset should work fine without image
        self.assertFalse(self.asset.image)
        self.assertFalse(self.asset.thumbnail)
    
    def test_small_image_not_upscaled(self):
        """Test that small images are not upscaled"""
        # Create a small image
        test_image = self.create_test_image(size=(400, 300))
        
        self.asset.image = test_image
        self.asset.save()
        
        # Image should keep original size since it's already smaller than max
        with Image.open(self.asset.image.path) as img:
            width, height = img.size
            self.assertEqual(width, 400)
            self.assertEqual(height, 300)
    
    def test_square_image_handling(self):
        """Test handling of square images"""
        test_image = self.create_test_image(size=(1000, 1000))
        
        self.asset.image = test_image
        self.asset.save()
        
        # Main image should be resized to 600x600 (to fit within 800x600)
        with Image.open(self.asset.image.path) as img:
            width, height = img.size
            self.assertEqual(width, 600)
            self.assertEqual(height, 600)
        
        # Thumbnail should be 150x150
        with Image.open(self.asset.thumbnail.path) as thumb:
            width, height = thumb.size
            self.assertEqual(width, 150)
            self.assertEqual(height, 150)
    
    def test_very_wide_image_handling(self):
        """Test handling of very wide images"""
        test_image = self.create_test_image(size=(2400, 600))  # 4:1 aspect ratio
        
        self.asset.image = test_image
        self.asset.save()
        
        # Main image should be resized to 800x200 (maintaining aspect ratio)
        with Image.open(self.asset.image.path) as img:
            width, height = img.size
            self.assertEqual(width, 800)
            self.assertEqual(height, 200)
    
    def test_very_tall_image_handling(self):
        """Test handling of very tall images"""
        test_image = self.create_test_image(size=(600, 2400))  # 1:4 aspect ratio
        
        self.asset.image = test_image
        self.asset.save()
        
        # Main image should be resized to 150x600 (maintaining aspect ratio)
        with Image.open(self.asset.image.path) as img:
            width, height = img.size
            self.assertEqual(width, 150)
            self.assertEqual(height, 600)