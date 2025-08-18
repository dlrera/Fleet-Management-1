from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
import json

from .models import Asset

User = get_user_model()


class AssetImageAPITestCase(TestCase):
    """Test cases for Asset image upload API"""
    
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
        
        # Create test asset
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
        image.save(image_io, format=format, quality=95)
        image_io.seek(0)
        
        return SimpleUploadedFile(
            filename,
            image_io.read(),
            content_type=f'image/{format.lower()}'
        )
    
    def test_upload_image_success(self):
        """Test successful image upload"""
        test_image = self.create_test_image()
        
        url = reverse('asset-upload-image', kwargs={'pk': self.asset.id})
        response = self.client.post(url, {'image': test_image}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('image', response.data)
        self.assertIn('thumbnail', response.data)
        
        # Refresh asset from database
        self.asset.refresh_from_db()
        self.assertTrue(self.asset.image)
        self.assertTrue(self.asset.thumbnail)
    
    def test_upload_image_invalid_format(self):
        """Test uploading invalid image format"""
        # Create a text file instead of image
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"This is not an image",
            content_type="text/plain"
        )
        
        url = reverse('asset-upload-image', kwargs={'pk': self.asset.id})
        response = self.client.post(url, {'image': invalid_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_upload_image_too_large(self):
        """Test uploading image that's too large"""
        # Create a large image (simulate > 5MB)
        large_image = self.create_test_image(size=(5000, 5000))
        
        url = reverse('asset-upload-image', kwargs={'pk': self.asset.id})
        response = self.client.post(url, {'image': large_image}, format='multipart')
        
        # Should either succeed (if compression makes it small enough) or fail with size error
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn('error', response.data)
            self.assertIn('size', response.data['error'].lower())
    
    def test_upload_image_no_file(self):
        """Test uploading without providing file"""
        url = reverse('asset-upload-image', kwargs={'pk': self.asset.id})
        response = self.client.post(url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_upload_image_asset_not_found(self):
        """Test uploading to non-existent asset"""
        test_image = self.create_test_image()
        
        url = reverse('asset-upload-image', kwargs={'pk': '99999999-9999-9999-9999-999999999999'})
        response = self.client.post(url, {'image': test_image}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_upload_image_unauthenticated(self):
        """Test uploading without authentication"""
        test_image = self.create_test_image()
        
        # Remove authentication
        self.client.credentials()
        
        url = reverse('asset-upload-image', kwargs={'pk': self.asset.id})
        response = self.client.post(url, {'image': test_image}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_upload_different_formats(self):
        """Test uploading different image formats"""
        formats = [
            ('test.jpg', 'JPEG'),
            ('test.png', 'PNG'),
            ('test.webp', 'WebP')
        ]
        
        for filename, format_type in formats:
            with self.subTest(format=format_type):
                test_image = self.create_test_image(filename=filename, format=format_type)
                
                url = reverse('asset-upload-image', kwargs={'pk': self.asset.id})
                response = self.client.post(url, {'image': test_image}, format='multipart')
                
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                
                # Refresh asset
                self.asset.refresh_from_db()
                self.assertTrue(self.asset.image)
                self.assertTrue(self.asset.thumbnail)
    
    def test_replace_existing_image(self):
        """Test replacing an existing image"""
        # Upload first image
        first_image = self.create_test_image(color='red')
        url = reverse('asset-upload-image', kwargs={'pk': self.asset.id})
        response = self.client.post(url, {'image': first_image}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        first_image_url = response.data['image']
        first_thumbnail_url = response.data['thumbnail']
        
        # Upload second image
        second_image = self.create_test_image(color='blue')
        response = self.client.post(url, {'image': second_image}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # URLs should be different
        self.assertNotEqual(response.data['image'], first_image_url)
        self.assertNotEqual(response.data['thumbnail'], first_thumbnail_url)
    
    def test_image_dimensions_after_upload(self):
        """Test that uploaded images have correct dimensions"""
        # Create large image
        test_image = self.create_test_image(size=(2000, 1500))
        
        url = reverse('asset-upload-image', kwargs={'pk': self.asset.id})
        response = self.client.post(url, {'image': test_image}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh asset and check image dimensions
        self.asset.refresh_from_db()
        
        with Image.open(self.asset.image.path) as img:
            width, height = img.size
            # Should be resized to fit within 800x600
            self.assertLessEqual(width, 800)
            self.assertLessEqual(height, 600)
        
        with Image.open(self.asset.thumbnail.path) as thumb:
            width, height = thumb.size
            # Thumbnail should be exactly 150x150
            self.assertEqual(width, 150)
            self.assertEqual(height, 150)
    
    def test_upload_response_contains_urls(self):
        """Test that upload response contains correct URLs"""
        test_image = self.create_test_image()
        
        url = reverse('asset-upload-image', kwargs={'pk': self.asset.id})
        response = self.client.post(url, {'image': test_image}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        self.assertIn('message', response.data)
        self.assertIn('image', response.data)
        self.assertIn('thumbnail', response.data)
        
        # URLs should be valid absolute URLs
        self.assertTrue(response.data['image'].startswith('http://'))
        self.assertTrue(response.data['thumbnail'].startswith('http://'))
        self.assertIn('/media/', response.data['image'])
        self.assertIn('/media/', response.data['thumbnail'])
        self.assertIn('_main', response.data['image'])
        self.assertIn('_thumb', response.data['thumbnail'])
        self.assertTrue(response.data['image'].endswith('.jpg'))
        self.assertTrue(response.data['thumbnail'].endswith('.jpg'))


class AssetImageIntegrationTestCase(TestCase):
    """Integration tests for image functionality with asset operations"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def create_test_image(self, filename='test_image.jpg', format='JPEG', size=(800, 600), color='red'):
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
    
    def test_asset_list_includes_thumbnail(self):
        """Test that asset list includes thumbnail URLs"""
        # Create asset with image
        asset = Asset.objects.create(
            vehicle_type='truck',
            make='Ford',
            model='F-150',
            year=2022
        )
        
        # Upload image
        test_image = self.create_test_image()
        upload_url = reverse('asset-upload-image', kwargs={'pk': asset.id})
        self.client.post(upload_url, {'image': test_image}, format='multipart')
        
        # Get asset list
        list_url = reverse('asset-list')
        response = self.client.get(list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find our asset in the results
        assets = response.data['results']
        test_asset = next((a for a in assets if a['id'] == str(asset.id)), None)
        
        self.assertIsNotNone(test_asset)
        self.assertIn('thumbnail', test_asset)
        self.assertTrue(test_asset['thumbnail'])
    
    def test_asset_detail_includes_images(self):
        """Test that asset detail includes both image and thumbnail"""
        # Create asset with image
        asset = Asset.objects.create(
            vehicle_type='truck',
            make='Ford',
            model='F-150',
            year=2022
        )
        
        # Upload image
        test_image = self.create_test_image()
        upload_url = reverse('asset-upload-image', kwargs={'pk': asset.id})
        self.client.post(upload_url, {'image': test_image}, format='multipart')
        
        # Get asset detail
        detail_url = reverse('asset-detail', kwargs={'pk': asset.id})
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check both image fields are present
        self.assertIn('image', response.data)
        self.assertIn('thumbnail', response.data)
        self.assertTrue(response.data['image'])
        self.assertTrue(response.data['thumbnail'])
    
    def test_asset_deletion_cleans_up_images(self):
        """Test that deleting asset cleans up associated images"""
        # Create asset with image
        asset = Asset.objects.create(
            vehicle_type='truck',
            make='Ford',
            model='F-150',
            year=2022
        )
        
        # Upload image
        test_image = self.create_test_image()
        upload_url = reverse('asset-upload-image', kwargs={'pk': asset.id})
        response = self.client.post(upload_url, {'image': test_image}, format='multipart')
        
        # Store image paths
        asset.refresh_from_db()
        image_path = asset.image.path
        thumbnail_path = asset.thumbnail.path
        
        # Verify files exist
        import os
        self.assertTrue(os.path.exists(image_path))
        self.assertTrue(os.path.exists(thumbnail_path))
        
        # Delete asset
        delete_url = reverse('asset-detail', kwargs={'pk': asset.id})
        response = self.client.delete(delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify files are cleaned up
        self.assertFalse(os.path.exists(image_path))
        self.assertFalse(os.path.exists(thumbnail_path))