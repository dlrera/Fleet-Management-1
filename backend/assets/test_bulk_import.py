from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Asset, AssetDocument
import csv
import io


class BulkImportTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def create_csv_file(self, data):
        """Helper to create CSV file from data"""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        output.seek(0)
        return SimpleUploadedFile(
            "test.csv",
            output.getvalue().encode('utf-8'),
            content_type="text/csv"
        )
    
    def test_bulk_import_success(self):
        """Test successful bulk import of assets"""
        data = [
            {
                'asset_id': 'TEST-001',
                'vehicle_type': 'bus',
                'make': 'Blue Bird',
                'model': 'Vision',
                'year': '2023',
                'vin': 'TEST1234567890123',  # Must be 17 characters
                'license_plate': 'TEST-123',
                'department': 'Transportation',
                'status': 'active',
                'current_odometer': '5000',
                'purchase_date': '2023-01-15',
                'purchase_cost': '95000.00',
                'notes': 'Test import'
            },
            {
                'asset_id': 'TEST-002',
                'vehicle_type': 'truck',
                'make': 'Ford',
                'model': 'F-250',
                'year': '2022',
                'vin': 'TEST9876543210987',  # Must be 17 characters
                'license_plate': 'TEST-456',
                'department': 'Maintenance',
                'status': 'active',
                'current_odometer': '15000',
                'purchase_date': '2022-06-01',
                'purchase_cost': '55000.00',
                'notes': 'Another test'
            }
        ]
        
        csv_file = self.create_csv_file(data)
        response = self.client.post(
            '/api/assets/bulk_import/',
            {'file': csv_file},
            format='multipart'
        )
        
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success_count'], 2)
        self.assertEqual(response.data['error_count'], 0)
        
        # Verify assets were created
        self.assertTrue(Asset.objects.filter(asset_id='TEST-001').exists())
        self.assertTrue(Asset.objects.filter(asset_id='TEST-002').exists())
    
    def test_bulk_import_with_errors(self):
        """Test bulk import with some invalid rows"""
        data = [
            {
                'asset_id': 'TEST-003',
                'vehicle_type': 'bus',
                'make': 'Blue Bird',
                'model': 'Vision',
                'year': '2023',
            },
            {
                'asset_id': 'TEST-004',
                'vehicle_type': 'invalid_type',  # Invalid vehicle type
                'make': 'Ford',
                'model': 'F-250',
                'year': '2022',
            }
        ]
        
        csv_file = self.create_csv_file(data)
        response = self.client.post(
            '/api/assets/bulk_import/',
            {'file': csv_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success_count'], 1)
        self.assertEqual(response.data['error_count'], 1)
        self.assertIn('errors', response.data)
        
        # Verify only valid asset was created
        self.assertTrue(Asset.objects.filter(asset_id='TEST-003').exists())
        self.assertFalse(Asset.objects.filter(asset_id='TEST-004').exists())
    
    def test_bulk_import_missing_required_fields(self):
        """Test bulk import with missing required fields"""
        data = [
            {
                'asset_id': 'TEST-005',
                'vehicle_type': 'bus',
                # Missing 'make', 'model', 'year'
            }
        ]
        
        csv_file = self.create_csv_file(data)
        response = self.client.post(
            '/api/assets/bulk_import/',
            {'file': csv_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Missing required columns', response.data['error'])
    
    def test_bulk_import_duplicate_asset_id(self):
        """Test bulk import with duplicate asset_id"""
        # Create existing asset
        Asset.objects.create(
            asset_id='EXISTING-001',
            vehicle_type='bus',
            make='Test',
            model='Model',
            year=2020
        )
        
        data = [
            {
                'asset_id': 'EXISTING-001',  # Duplicate
                'vehicle_type': 'truck',
                'make': 'Ford',
                'model': 'F-250',
                'year': '2022',
            }
        ]
        
        csv_file = self.create_csv_file(data)
        response = self.client.post(
            '/api/assets/bulk_import/',
            {'file': csv_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_count'], 1)
        self.assertIn('already exists', response.data['errors'][0]['error'])
    
    def test_bulk_import_invalid_file_type(self):
        """Test bulk import with non-CSV file"""
        txt_file = SimpleUploadedFile(
            "test.txt",
            b"Not a CSV file",
            content_type="text/plain"
        )
        
        response = self.client.post(
            '/api/assets/bulk_import/',
            {'file': txt_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('File must be CSV format', response.data['error'])
    
    def test_bulk_import_file_too_large(self):
        """Test bulk import with file exceeding size limit"""
        # Create a large CSV content (> 5MB)
        large_content = "a" * (5 * 1024 * 1024 + 1)
        large_file = SimpleUploadedFile(
            "large.csv",
            large_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        response = self.client.post(
            '/api/assets/bulk_import/',
            {'file': large_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('File size must be less than 5MB', response.data['error'])
    
    def test_download_csv_template(self):
        """Test downloading CSV template"""
        response = self.client.get('/api/assets/download_template/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="assets_import_template.csv"', 
                     response['Content-Disposition'])
        
        # Parse CSV content
        content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        
        # Check headers
        expected_headers = [
            'asset_id', 'vehicle_type', 'make', 'model', 'year',
            'vin', 'license_plate', 'department', 'status',
            'current_odometer', 'purchase_date', 'purchase_cost', 'notes'
        ]
        self.assertEqual(list(reader.fieldnames), expected_headers)
        
        # Check sample data exists
        rows = list(reader)
        self.assertGreater(len(rows), 0)
    
    def test_bulk_import_unauthorized(self):
        """Test bulk import without authentication"""
        self.client.credentials()  # Remove auth
        
        csv_file = self.create_csv_file([{'asset_id': 'TEST'}])
        response = self.client.post(
            '/api/assets/bulk_import/',
            {'file': csv_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DocumentUploadTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Create test asset
        self.asset = Asset.objects.create(
            asset_id='DOC-TEST-001',
            vehicle_type='bus',
            make='Test Make',
            model='Test Model',
            year=2023
        )
    
    def test_upload_document_success(self):
        """Test successful document upload"""
        # Create a test file
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"PDF file content",
            content_type="application/pdf"
        )
        
        response = self.client.post(
            f'/api/assets/{self.asset.id}/upload_document/',
            {
                'file': test_file,
                'document_type': 'registration',
                'title': 'Test Registration',
                'description': 'Test description'
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Registration')
        self.assertEqual(response.data['document_type'], 'registration')
        
        # Verify document was created
        self.assertEqual(AssetDocument.objects.count(), 1)
        doc = AssetDocument.objects.first()
        self.assertEqual(doc.asset, self.asset)
        self.assertEqual(doc.title, 'Test Registration')
    
    def test_upload_multiple_documents(self):
        """Test uploading multiple documents to same asset"""
        documents = [
            ('registration.pdf', 'registration', 'Vehicle Registration'),
            ('insurance.pdf', 'insurance', 'Insurance Certificate'),
            ('manual.pdf', 'manual', 'Owner Manual')
        ]
        
        for filename, doc_type, title in documents:
            test_file = SimpleUploadedFile(
                filename,
                b"File content",
                content_type="application/pdf"
            )
            
            response = self.client.post(
                f'/api/assets/{self.asset.id}/upload_document/',
                {
                    'file': test_file,
                    'document_type': doc_type,
                    'title': title
                },
                format='multipart'
            )
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify all documents were created
        self.assertEqual(AssetDocument.objects.count(), 3)
        self.assertEqual(self.asset.documents.count(), 3)
    
    def test_upload_invalid_document_type(self):
        """Test uploading document with invalid type"""
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"PDF content",
            content_type="application/pdf"
        )
        
        response = self.client.post(
            f'/api/assets/{self.asset.id}/upload_document/',
            {
                'file': test_file,
                'document_type': 'invalid_type',
                'title': 'Test'
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_asset_documents(self):
        """Test retrieving documents for an asset"""
        # Create some documents
        for i in range(3):
            AssetDocument.objects.create(
                asset=self.asset,
                document_type='registration',
                title=f'Document {i}',
                file=f'path/to/file{i}.pdf'
            )
        
        response = self.client.get(f'/api/assets/{self.asset.id}/documents/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_upload_document_unauthorized(self):
        """Test document upload without authentication"""
        self.client.credentials()  # Remove auth
        
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"PDF content",
            content_type="application/pdf"
        )
        
        response = self.client.post(
            f'/api/assets/{self.asset.id}/upload_document/',
            {'file': test_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_upload_document_nonexistent_asset(self):
        """Test uploading document to non-existent asset"""
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"PDF content",
            content_type="application/pdf"
        )
        
        fake_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
        response = self.client.post(
            f'/api/assets/{fake_id}/upload_document/',
            {
                'file': test_file,
                'document_type': 'registration',
                'title': 'Test'
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)