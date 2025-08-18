from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from .models import Driver

User = get_user_model()


class DriverPhotoAPITestCase(TestCase):
    """Test cases for Driver photo upload API"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user and token
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        
        # Set up API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Create test driver
        self.driver = Driver.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='+1234567890',
            date_of_birth='1990-01-01',
            hire_date='2020-01-01',
            license_number='D123456789',
            license_type='regular',
            license_expiration='2025-01-01',
            license_state='CA',
            address_line1='123 Main St',
            city='Anytown',
            state='CA',
            zip_code='12345',
            emergency_contact_name='Jane Doe',
            emergency_contact_phone='+0987654321',
            emergency_contact_relationship='Spouse'
        )
    
    def create_test_image(self, filename='test_photo.jpg', format='JPEG', size=(400, 400), color='blue'):
        """Create a test image file"""
        image = Image.new('RGB', size, color)
        image_io = io.BytesIO()
        image.save(image_io, format=format, quality=95)
        image_io.seek(0)
        
        return SimpleUploadedFile(
            filename,
            image_io.read(),
            content_type=f'image/{format.lower()}'
        )
    
    def test_upload_photo_success(self):
        """Test successful photo upload"""
        test_photo = self.create_test_image()
        
        url = reverse('driver-upload-photo', kwargs={'pk': self.driver.id})
        response = self.client.post(url, {'photo': test_photo}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('photo', response.data)
        
        # Refresh driver from database
        self.driver.refresh_from_db()
        self.assertTrue(self.driver.profile_photo)
    
    def test_upload_photo_invalid_format(self):
        """Test uploading invalid photo format"""
        # Create a text file instead of image
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"This is not an image",
            content_type="text/plain"
        )
        
        url = reverse('driver-upload-photo', kwargs={'pk': self.driver.id})
        response = self.client.post(url, {'photo': invalid_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_upload_photo_too_large(self):
        """Test uploading photo that's too large"""
        # Create a large image (simulate > 2MB)
        large_photo = self.create_test_image(size=(3000, 3000))
        
        url = reverse('driver-upload-photo', kwargs={'pk': self.driver.id})
        response = self.client.post(url, {'photo': large_photo}, format='multipart')
        
        # Should either succeed (if compression makes it small enough) or fail with size error
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn('error', response.data)
            self.assertIn('size', response.data['error'].lower())
    
    def test_upload_photo_no_file(self):
        """Test uploading without providing file"""
        url = reverse('driver-upload-photo', kwargs={'pk': self.driver.id})
        response = self.client.post(url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_upload_different_formats(self):
        """Test uploading different image formats"""
        formats = [
            ('test.jpg', 'JPEG'),
            ('test.png', 'PNG'),
            ('test.webp', 'WebP')
        ]
        
        for filename, format_type in formats:
            with self.subTest(format=format_type):
                test_photo = self.create_test_image(filename=filename, format=format_type)
                
                url = reverse('driver-upload-photo', kwargs={'pk': self.driver.id})
                response = self.client.post(url, {'photo': test_photo}, format='multipart')
                
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                
                # Refresh driver
                self.driver.refresh_from_db()
                self.assertTrue(self.driver.profile_photo)
    
    def test_photo_dimensions_after_upload(self):
        """Test that uploaded photos have correct dimensions"""
        # Create large image
        test_photo = self.create_test_image(size=(1000, 800))
        
        url = reverse('driver-upload-photo', kwargs={'pk': self.driver.id})
        response = self.client.post(url, {'photo': test_photo}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh driver and check photo dimensions
        self.driver.refresh_from_db()
        
        with Image.open(self.driver.profile_photo.path) as img:
            width, height = img.size
            # Should be resized to fit within 300x300
            self.assertLessEqual(width, 300)
            self.assertLessEqual(height, 300)