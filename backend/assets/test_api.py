from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from decimal import Decimal
from datetime import date
import json

from .models import Asset, AssetDocument


class AssetAPITestCase(APITestCase):
    """Test cases for Asset API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user and token
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        
        # Set up authentication
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Create test assets
        self.asset1 = Asset.objects.create(
            asset_id='TEST-001',
            vehicle_type='truck',
            make='Ford',
            model='F-150',
            year=2022,
            vin='1FTFW1ET5DFC10312',
            license_plate='ABC123',
            department='Operations',
            current_odometer=15000,
            status='active'
        )
        
        self.asset2 = Asset.objects.create(
            asset_id='TEST-002',
            vehicle_type='bus',
            make='Mercedes',
            model='Sprinter',
            year=2021,
            department='Transportation',
            current_odometer=25000,
            status='maintenance'
        )
    
    def test_get_assets_list(self):
        """Test GET /api/assets/ - List all assets"""
        url = '/api/assets/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check pagination structure
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        # Check asset data structure (list serializer)
        asset_data = response.data['results'][0]
        expected_fields = [
            'id', 'asset_id', 'vehicle_type', 'make', 'model', 'year',
            'license_plate', 'department', 'current_odometer', 'status',
            'created_at', 'documents_count'
        ]
        for field in expected_fields:
            self.assertIn(field, asset_data)
    
    def test_get_asset_detail(self):
        """Test GET /api/assets/{id}/ - Get asset detail"""
        url = f'/api/assets/{self.asset1.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check detailed asset data structure
        data = response.data
        expected_fields = [
            'id', 'asset_id', 'vehicle_type', 'make', 'model', 'year',
            'vin', 'license_plate', 'department', 'purchase_date',
            'purchase_cost', 'current_odometer', 'status', 'notes',
            'created_at', 'updated_at', 'documents'
        ]
        for field in expected_fields:
            self.assertIn(field, data)
        
        self.assertEqual(data['asset_id'], 'TEST-001')
        self.assertEqual(data['make'], 'Ford')
        self.assertEqual(data['model'], 'F-150')
    
    def test_create_asset(self):
        """Test POST /api/assets/ - Create new asset"""
        url = '/api/assets/'
        data = {
            'vehicle_type': 'van',
            'make': 'Ford',
            'model': 'Transit',
            'year': 2023,
            'vin': '2FTBW2CM5HCA12345',
            'license_plate': 'XYZ789',
            'department': 'Delivery',
            'purchase_date': '2023-05-15',
            'purchase_cost': '32000.00',
            'current_odometer': 1200,
            'status': 'active',
            'notes': 'New delivery van'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Debug: print response data
        print("Response data:", response.data)
        
        # Verify asset was created
        if 'id' in response.data:
            asset = Asset.objects.get(id=response.data['id'])
        else:
            # If ID not in response, find by asset_id
            asset = Asset.objects.get(asset_id=response.data.get('asset_id'))
        self.assertEqual(asset.vehicle_type, 'van')
        self.assertEqual(asset.make, 'Ford')
        self.assertEqual(asset.model, 'Transit')
        self.assertEqual(asset.vin, '2FTBW2CM5HCA12345')
    
    def test_create_asset_auto_id(self):
        """Test asset creation with auto-generated ID"""
        url = '/api/assets/'
        data = {
            'vehicle_type': 'tractor',
            'make': 'John Deere',
            'model': '5075E',
            'year': 2022
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check auto-generated asset ID
        asset = Asset.objects.get(id=response.data['id'])
        self.assertTrue(asset.asset_id.startswith('TRA-'))
    
    def test_update_asset(self):
        """Test PUT /api/assets/{id}/ - Update asset"""
        url = f'/api/assets/{self.asset1.id}/'
        data = {
            'vehicle_type': 'truck',
            'make': 'Ford',
            'model': 'F-250',  # Changed model
            'year': 2022,
            'current_odometer': 18000,  # Updated odometer
            'status': 'maintenance'  # Changed status
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify updates
        self.asset1.refresh_from_db()
        self.assertEqual(self.asset1.model, 'F-250')
        self.assertEqual(self.asset1.current_odometer, 18000)
        self.assertEqual(self.asset1.status, 'maintenance')
    
    def test_partial_update_asset(self):
        """Test PATCH /api/assets/{id}/ - Partial update"""
        url = f'/api/assets/{self.asset1.id}/'
        data = {
            'current_odometer': 16500,
            'notes': 'Updated odometer reading'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify partial updates
        self.asset1.refresh_from_db()
        self.assertEqual(self.asset1.current_odometer, 16500)
        self.assertEqual(self.asset1.notes, 'Updated odometer reading')
        # Other fields should remain unchanged
        self.assertEqual(self.asset1.make, 'Ford')
        self.assertEqual(self.asset1.model, 'F-150')
    
    def test_delete_asset(self):
        """Test DELETE /api/assets/{id}/ - Delete asset"""
        url = f'/api/assets/{self.asset1.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify asset was deleted
        self.assertFalse(Asset.objects.filter(id=self.asset1.id).exists())
    
    def test_authentication_required(self):
        """Test that authentication is required for all endpoints"""
        # Remove authentication
        self.client.credentials()
        
        # Test various endpoints without authentication
        endpoints = [
            '/api/assets/',
            f'/api/assets/{self.asset1.id}/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_invalid_asset_id(self):
        """Test accessing non-existent asset"""
        url = '/api/assets/99999999-9999-9999-9999-999999999999/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_validation_errors(self):
        """Test validation error responses"""
        url = '/api/assets/'
        
        # Test missing required fields
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('vehicle_type', response.data)
        self.assertIn('make', response.data)
        self.assertIn('model', response.data)
        self.assertIn('year', response.data)
        
        # Test invalid year
        data = {
            'vehicle_type': 'car',
            'make': 'Tesla',
            'model': 'Model 3',
            'year': 2030  # Future year
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('year', response.data)
        
        # Test invalid VIN length
        data = {
            'vehicle_type': 'car',
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2022,
            'vin': 'TOOSHORT'  # Invalid VIN length
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('vin', response.data)


class AssetSearchFilterTestCase(APITestCase):
    """Test cases for Asset search and filtering"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user and token
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Create diverse test assets
        Asset.objects.create(
            asset_id='TRUCK-001',
            vehicle_type='truck',
            make='Ford',
            model='F-150',
            year=2022,
            department='Operations',
            status='active'
        )
        
        Asset.objects.create(
            asset_id='BUS-001',
            vehicle_type='bus',
            make='Mercedes',
            model='Sprinter',
            year=2021,
            department='Transportation',
            status='maintenance'
        )
        
        Asset.objects.create(
            asset_id='VAN-001',
            vehicle_type='van',
            make='Ford',
            model='Transit',
            year=2023,
            department='Delivery',
            status='active'
        )
        
        Asset.objects.create(
            asset_id='CAR-001',
            vehicle_type='car',
            make='Toyota',
            model='Camry',
            year=2020,
            department='Administration',
            status='retired'
        )
    
    def test_search_by_asset_id(self):
        """Test searching by asset ID"""
        url = '/api/assets/?search=TRUCK'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['asset_id'], 'TRUCK-001')
    
    def test_search_by_make(self):
        """Test searching by make"""
        url = '/api/assets/?search=Ford'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # TRUCK-001 and VAN-001
        
        asset_ids = [asset['asset_id'] for asset in response.data['results']]
        self.assertIn('TRUCK-001', asset_ids)
        self.assertIn('VAN-001', asset_ids)
    
    def test_search_by_model(self):
        """Test searching by model"""
        url = '/api/assets/?search=Sprinter'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['asset_id'], 'BUS-001')
    
    def test_filter_by_vehicle_type(self):
        """Test filtering by vehicle type"""
        url = '/api/assets/?vehicle_type=truck'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['vehicle_type'], 'truck')
    
    def test_filter_by_status(self):
        """Test filtering by status"""
        url = '/api/assets/?status=active'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # TRUCK-001 and VAN-001
        
        for asset in response.data['results']:
            self.assertEqual(asset['status'], 'active')
    
    def test_filter_by_department(self):
        """Test filtering by department"""
        url = '/api/assets/?department=Operations'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['department'], 'Operations')
    
    def test_filter_by_year(self):
        """Test filtering by year"""
        url = '/api/assets/?year=2022'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['year'], 2022)
    
    def test_multiple_filters(self):
        """Test combining multiple filters"""
        url = '/api/assets/?vehicle_type=van&status=active&make=Ford'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        asset = response.data['results'][0]
        self.assertEqual(asset['vehicle_type'], 'van')
        self.assertEqual(asset['status'], 'active')
        self.assertEqual(asset['make'], 'Ford')
    
    def test_search_with_filters(self):
        """Test combining search with filters"""
        url = '/api/assets/?search=Ford&status=active'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        for asset in response.data['results']:
            self.assertEqual(asset['make'], 'Ford')
            self.assertEqual(asset['status'], 'active')
    
    def test_ordering(self):
        """Test ordering results"""
        # Test ordering by asset_id (default)
        url = '/api/assets/?ordering=asset_id'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asset_ids = [asset['asset_id'] for asset in response.data['results']]
        self.assertEqual(asset_ids, sorted(asset_ids))
        
        # Test reverse ordering
        url = '/api/assets/?ordering=-asset_id'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asset_ids = [asset['asset_id'] for asset in response.data['results']]
        self.assertEqual(asset_ids, sorted(asset_ids, reverse=True))
    
    def test_pagination(self):
        """Test pagination functionality"""
        # Create more assets to test pagination
        for i in range(25):
            Asset.objects.create(
                asset_id=f'TEST-{i:03d}',
                vehicle_type='equipment',
                make='Test',
                model=f'Model{i}',
                year=2022
            )
        
        # Test first page
        url = '/api/assets/?page=1'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 20)  # Default page size
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        
        # Test second page
        url = '/api/assets/?page=2'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['previous'])
        self.assertTrue(len(response.data['results']) > 0)


class AssetCustomEndpointsTestCase(APITestCase):
    """Test cases for custom Asset endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user and token
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Create test asset
        self.asset = Asset.objects.create(
            vehicle_type='truck',
            make='Ford',
            model='F-150',
            year=2022
        )
        
        # Create diverse assets for stats
        Asset.objects.create(vehicle_type='bus', make='Mercedes', model='Sprinter', year=2021, status='active')
        Asset.objects.create(vehicle_type='van', make='Ford', model='Transit', year=2023, status='maintenance')
        Asset.objects.create(vehicle_type='car', make='Toyota', model='Camry', year=2020, status='retired')
    
    def test_asset_stats_endpoint(self):
        """Test GET /api/assets/stats/ - Get asset statistics"""
        url = '/api/assets/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('total_assets', data)
        self.assertIn('active_assets', data)
        self.assertIn('maintenance_assets', data)
        self.assertIn('retired_assets', data)
        self.assertIn('vehicle_types', data)
        
        # Verify counts
        self.assertEqual(data['total_assets'], 4)
        self.assertEqual(data['active_assets'], 2)  # truck and bus
        self.assertEqual(data['maintenance_assets'], 1)  # van
        self.assertEqual(data['retired_assets'], 1)  # car
        
        # Verify vehicle type breakdown
        vehicle_types = data['vehicle_types']
        self.assertEqual(vehicle_types['Truck'], 1)
        self.assertEqual(vehicle_types['Bus'], 1)
        self.assertEqual(vehicle_types['Van'], 1)
        self.assertEqual(vehicle_types['Car'], 1)
    
    def test_asset_documents_endpoint(self):
        """Test GET /api/assets/{id}/documents/ - Get asset documents"""
        # Create test documents
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
        
        url = f'/api/assets/{self.asset.id}/documents/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Verify document data
        doc_titles = [doc['title'] for doc in response.data]
        self.assertIn('Registration', doc_titles)
        self.assertIn('Insurance', doc_titles)
    
    def test_upload_document_endpoint(self):
        """Test POST /api/assets/{id}/upload_document/ - Upload document"""
        url = f'/api/assets/{self.asset.id}/upload_document/'
        
        # Create test file
        test_file = SimpleUploadedFile(
            "test_upload.pdf",
            b"test file content",
            content_type="application/pdf"
        )
        
        data = {
            'document_type': 'manual',
            'title': 'Owner Manual',
            'file': test_file,
            'description': 'Vehicle owner manual'
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify document was created
        document = AssetDocument.objects.get(title='Owner Manual')
        self.assertEqual(document.asset, self.asset)
        self.assertEqual(document.document_type, 'manual')
        self.assertEqual(document.description, 'Vehicle owner manual')
    
    def test_upload_document_validation(self):
        """Test document upload validation"""
        url = f'/api/assets/{self.asset.id}/upload_document/'
        
        # Test missing required fields
        data = {
            'title': 'Test Document'
            # Missing document_type and file
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('document_type', response.data)
        self.assertIn('file', response.data)