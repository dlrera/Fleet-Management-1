from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from decimal import Decimal
from datetime import date

from .models import Asset, AssetDocument
from .serializers import (
    AssetSerializer, 
    AssetListSerializer, 
    AssetCreateUpdateSerializer,
    AssetDocumentSerializer
)


class AssetSerializerTestCase(TestCase):
    """Test cases for Asset serializers"""
    
    def setUp(self):
        """Set up test data"""
        self.asset_data = {
            'asset_id': 'TEST-001',
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
            'notes': 'Test vehicle'
        }
        
        self.asset = Asset.objects.create(**self.asset_data)
    
    def test_asset_serializer_serialization(self):
        """Test AssetSerializer serialization"""
        serializer = AssetSerializer(self.asset)
        data = serializer.data
        
        self.assertEqual(data['asset_id'], 'TEST-001')
        self.assertEqual(data['vehicle_type'], 'truck')
        self.assertEqual(data['make'], 'Ford')
        self.assertEqual(data['model'], 'F-150')
        self.assertEqual(data['year'], 2022)
        self.assertEqual(data['vin'], '1FTFW1ET5DFC10312')
        self.assertEqual(data['license_plate'], 'ABC123')
        self.assertEqual(data['department'], 'Operations')
        self.assertEqual(data['purchase_date'], '2022-01-15')
        self.assertEqual(data['purchase_cost'], '35000.00')
        self.assertEqual(data['current_odometer'], 15000)
        self.assertEqual(data['status'], 'active')
        self.assertEqual(data['notes'], 'Test vehicle')
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        self.assertIn('documents', data)
    
    def test_asset_list_serializer(self):
        """Test AssetListSerializer includes documents count"""
        # Add a document to the asset
        AssetDocument.objects.create(
            asset=self.asset,
            document_type='registration',
            title='Registration',
            file=SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        )
        
        serializer = AssetListSerializer(self.asset)
        data = serializer.data
        
        self.assertEqual(data['documents_count'], 1)
        self.assertNotIn('documents', data)  # Full documents not included in list view
        self.assertNotIn('notes', data)  # Notes not included in list view
    
    def test_asset_create_update_serializer_validation(self):
        """Test AssetCreateUpdateSerializer validation"""
        # Test valid data
        valid_data = {
            'vehicle_type': 'bus',
            'make': 'Mercedes',
            'model': 'Sprinter',
            'year': 2023,
            'vin': '2GTBV8DX3G1234567'
        }
        
        serializer = AssetCreateUpdateSerializer(data=valid_data)
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
        self.assertTrue(serializer.is_valid())
        
        # Test invalid year (future)
        invalid_data = valid_data.copy()
        invalid_data['year'] = 2030
        
        serializer = AssetCreateUpdateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('year', serializer.errors)
    
    def test_vin_validation(self):
        """Test VIN validation in serializer"""
        # Test invalid VIN length
        invalid_data = {
            'vehicle_type': 'car',
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2022,
            'vin': 'TOOSHORT'  # Less than 17 characters
        }
        
        serializer = AssetCreateUpdateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('vin', serializer.errors)
        
        # Test valid VIN
        valid_data = invalid_data.copy()
        valid_data['vin'] = '1HGBH41JXMN109186'  # Exactly 17 characters
        
        serializer = AssetCreateUpdateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_year_validation(self):
        """Test year validation in serializer"""
        from datetime import datetime
        current_year = datetime.now().year
        
        # Test future year (invalid)
        future_data = {
            'vehicle_type': 'car',
            'make': 'Tesla',
            'model': 'Model 3',
            'year': current_year + 2
        }
        
        serializer = AssetCreateUpdateSerializer(data=future_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('year', serializer.errors)
        
        # Test current year + 1 (valid for next model year)
        valid_data = future_data.copy()
        valid_data['year'] = current_year + 1
        
        serializer = AssetCreateUpdateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_deserialization(self):
        """Test creating asset from serializer data"""
        data = {
            'asset_id': 'SER-001',
            'vehicle_type': 'van',
            'make': 'Ford',
            'model': 'Transit',
            'year': 2023,
            'current_odometer': 5000,
            'status': 'active'
        }
        
        serializer = AssetCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        asset = serializer.save()
        self.assertEqual(asset.asset_id, 'SER-001')
        self.assertEqual(asset.vehicle_type, 'van')
        self.assertEqual(asset.make, 'Ford')
        self.assertEqual(asset.model, 'Transit')
        self.assertEqual(asset.year, 2023)
        self.assertEqual(asset.current_odometer, 5000)
        self.assertEqual(asset.status, 'active')


class AssetDocumentSerializerTestCase(TestCase):
    """Test cases for AssetDocument serializer"""
    
    def setUp(self):
        """Set up test data"""
        self.asset = Asset.objects.create(
            vehicle_type='truck',
            make='Ford',
            model='F-150',
            year=2022
        )
        
        self.test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
    
    def test_document_serializer_serialization(self):
        """Test AssetDocumentSerializer serialization"""
        document = AssetDocument.objects.create(
            asset=self.asset,
            document_type='registration',
            title='Vehicle Registration',
            file=self.test_file,
            description='Primary registration document'
        )
        
        serializer = AssetDocumentSerializer(document)
        data = serializer.data
        
        self.assertEqual(data['document_type'], 'registration')
        self.assertEqual(data['title'], 'Vehicle Registration')
        self.assertEqual(data['description'], 'Primary registration document')
        self.assertIn('id', data)
        self.assertIn('file', data)
        self.assertIn('uploaded_at', data)
    
    def test_document_serializer_validation(self):
        """Test AssetDocumentSerializer validation"""
        valid_data = {
            'document_type': 'insurance',
            'title': 'Insurance Policy',
            'description': 'Auto insurance policy document'
        }
        
        # Note: file field would be handled separately in multipart requests
        serializer = AssetDocumentSerializer(data=valid_data)
        self.assertFalse(serializer.is_valid())  # file is required
        self.assertIn('file', serializer.errors)
    
    def test_document_choices_validation(self):
        """Test document type choices validation"""
        valid_types = ['registration', 'insurance', 'manual', 'maintenance', 'inspection', 'photo', 'other']
        
        for doc_type in valid_types:
            data = {
                'document_type': doc_type,
                'title': f'Test {doc_type}',
                'file': SimpleUploadedFile(f"test_{doc_type}.pdf", b"content", content_type="application/pdf")
            }
            
            serializer = AssetDocumentSerializer(data=data)
            serializer.is_valid()  # Call is_valid() before accessing errors
            # File validation might fail in test environment, but document_type should be valid
            if 'document_type' in serializer.errors:
                self.fail(f"Document type '{doc_type}' should be valid")
    
    def test_nested_documents_in_asset_serializer(self):
        """Test that documents are properly nested in asset serializer"""
        # Create multiple documents for the asset
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
        
        serializer = AssetSerializer(self.asset)
        data = serializer.data
        
        self.assertEqual(len(data['documents']), 2)
        
        # Check document data structure
        for doc_data in data['documents']:
            self.assertIn('id', doc_data)
            self.assertIn('document_type', doc_data)
            self.assertIn('title', doc_data)
            self.assertIn('file', doc_data)
            self.assertIn('uploaded_at', doc_data)
    
    def test_readonly_fields(self):
        """Test that readonly fields are not updated"""
        document = AssetDocument.objects.create(
            asset=self.asset,
            document_type='photo',
            title='Vehicle Photo',
            file=self.test_file
        )
        
        original_id = document.id
        original_uploaded_at = document.uploaded_at
        
        # Try to update readonly fields
        update_data = {
            'id': 'new-id',
            'document_type': 'manual',
            'title': 'Updated Title',
            'uploaded_at': '2020-01-01T00:00:00Z'
        }
        
        serializer = AssetDocumentSerializer(document, data=update_data, partial=True)
        if serializer.is_valid():
            updated_document = serializer.save()
            
            # ID and uploaded_at should not change
            self.assertEqual(updated_document.id, original_id)
            self.assertEqual(updated_document.uploaded_at, original_uploaded_at)
            
            # Other fields should update
            self.assertEqual(updated_document.document_type, 'manual')
            self.assertEqual(updated_document.title, 'Updated Title')