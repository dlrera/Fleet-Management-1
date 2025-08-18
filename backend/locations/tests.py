from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status
from decimal import Decimal
from datetime import timedelta
import json

from assets.models import Asset
from .models import LocationUpdate, LocationZone, AssetLocationSummary


class LocationUpdateModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.asset = Asset.objects.create(
            asset_id='TEST001',
            make='Test',
            model='Vehicle',
            year=2023,
            vehicle_type='truck',
            status='active',
            department='Fleet'
        )

    def test_location_update_creation(self):
        """Test basic location update creation"""
        location = LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now(),
            source='manual'
        )
        
        self.assertEqual(location.asset, self.asset)
        self.assertEqual(location.latitude, Decimal('40.7128'))
        self.assertEqual(location.longitude, Decimal('-74.0060'))
        self.assertEqual(location.source, 'manual')

    def test_coordinates_property(self):
        """Test coordinates property returns tuple"""
        location = LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now(),
            source='manual'
        )
        
        coords = location.coordinates
        self.assertEqual(coords, (40.7128, -74.0060))
        self.assertIsInstance(coords[0], float)
        self.assertIsInstance(coords[1], float)

    def test_coordinate_validation(self):
        """Test coordinate range validation"""
        with self.assertRaises(ValueError):
            LocationUpdate.objects.create(
                asset=self.asset,
                latitude=Decimal('91.0'),  # Invalid latitude
                longitude=Decimal('0.0'),
                timestamp=timezone.now(),
                source='manual'
            )
        
        with self.assertRaises(ValueError):
            LocationUpdate.objects.create(
                asset=self.asset,
                latitude=Decimal('0.0'),
                longitude=Decimal('181.0'),  # Invalid longitude
                timestamp=timezone.now(),
                source='manual'
            )

    def test_string_representation(self):
        """Test string representation"""
        location = LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now(),
            source='manual'
        )
        
        expected = f"{self.asset.asset_id} at 40.7128, -74.0060 ({location.timestamp})"
        self.assertEqual(str(location), expected)


class LocationZoneModelTests(TestCase):
    def setUp(self):
        self.zone = LocationZone.objects.create(
            name='Test Depot',
            description='Test depot zone',
            zone_type='depot',
            center_lat=Decimal('40.7128'),
            center_lng=Decimal('-74.0060'),
            radius=1000.0,
            color='#1976d2'
        )

    def test_zone_creation(self):
        """Test basic zone creation"""
        self.assertEqual(self.zone.name, 'Test Depot')
        self.assertEqual(self.zone.zone_type, 'depot')
        self.assertEqual(self.zone.radius, 1000.0)
        self.assertTrue(self.zone.is_active)

    def test_center_coordinates_property(self):
        """Test center coordinates property"""
        coords = self.zone.center_coordinates
        self.assertEqual(coords, (40.7128, -74.0060))
        self.assertIsInstance(coords[0], float)
        self.assertIsInstance(coords[1], float)

    def test_contains_point_inside(self):
        """Test point containment - point inside zone"""
        # Point very close to center (should be inside 1000m radius)
        latitude = 40.7130
        longitude = -74.0062
        
        result = self.zone.contains_point(latitude, longitude)
        self.assertTrue(result)

    def test_contains_point_outside(self):
        """Test point containment - point outside zone"""
        # Point far from center (should be outside 1000m radius)
        latitude = 41.0000
        longitude = -75.0000
        
        result = self.zone.contains_point(latitude, longitude)
        self.assertFalse(result)

    def test_string_representation(self):
        """Test string representation"""
        expected = "Test Depot (Depot)"
        self.assertEqual(str(self.zone), expected)


class AssetLocationSummaryModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.asset = Asset.objects.create(
            asset_id='TEST001',
            make='Test',
            model='Vehicle',
            year=2023,
            vehicle_type='truck',
            status='active',
            department='Fleet'
        )
        self.zone = LocationZone.objects.create(
            name='Test Zone',
            center_lat=Decimal('40.7128'),
            center_lng=Decimal('-74.0060'),
            radius=1000.0
        )

    def test_update_for_asset_creation(self):
        """Test creating new asset location summary"""
        location_update = LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now(),
            source='manual',
            address='New York, NY'
        )
        
        summary = AssetLocationSummary.update_for_asset(location_update)
        
        self.assertIsNotNone(summary)
        self.assertEqual(summary.asset, self.asset)
        self.assertEqual(summary.latitude, location_update.latitude)
        self.assertEqual(summary.longitude, location_update.longitude)
        self.assertEqual(summary.address, 'New York, NY')

    def test_update_for_asset_with_zone(self):
        """Test asset location summary with zone detection"""
        # Create location inside the zone
        location_update = LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),  # Same as zone center
            longitude=Decimal('-74.0060'),  # Same as zone center
            timestamp=timezone.now(),
            source='manual'
        )
        
        summary = AssetLocationSummary.update_for_asset(location_update)
        
        self.assertEqual(summary.current_zone, self.zone)

    def test_update_for_asset_newer_location(self):
        """Test updating with newer location"""
        # Create initial location
        old_location = LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now() - timedelta(hours=1),
            source='manual'
        )
        
        summary = AssetLocationSummary.update_for_asset(old_location)
        old_timestamp = summary.timestamp
        
        # Create newer location
        new_location = LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7130'),
            longitude=Decimal('-74.0062'),
            timestamp=timezone.now(),
            source='gps_device'
        )
        
        updated_summary = AssetLocationSummary.update_for_asset(new_location)
        
        self.assertEqual(summary.id, updated_summary.id)  # Same object
        self.assertEqual(updated_summary.latitude, new_location.latitude)
        self.assertEqual(updated_summary.longitude, new_location.longitude)
        self.assertEqual(updated_summary.source, 'gps_device')
        self.assertGreater(updated_summary.timestamp, old_timestamp)

    def test_update_for_asset_older_location(self):
        """Test that older locations don't update summary"""
        # Create recent location
        recent_location = LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now(),
            source='manual'
        )
        
        summary = AssetLocationSummary.update_for_asset(recent_location)
        original_timestamp = summary.timestamp
        
        # Create older location
        old_location = LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7130'),
            longitude=Decimal('-74.0062'),
            timestamp=timezone.now() - timedelta(hours=1),
            source='gps_device'
        )
        
        AssetLocationSummary.update_for_asset(old_location)
        summary.refresh_from_db()
        
        # Summary should not be updated with older data
        self.assertEqual(summary.timestamp, original_timestamp)
        self.assertEqual(summary.latitude, recent_location.latitude)
        self.assertEqual(summary.source, 'manual')


class LocationUpdateAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.asset = Asset.objects.create(
            asset_id='TEST001',
            make='Test',
            model='Vehicle',
            year=2023,
            vehicle_type='truck',
            status='active',
            department='Fleet'
        )

    def test_create_location_update(self):
        """Test creating location update via API"""
        url = reverse('locationupdate-list')
        data = {
            'asset_id': 'TEST001',
            'latitude': '40.7128',
            'longitude': '-74.0060',
            'timestamp': timezone.now().isoformat(),
            'source': 'manual'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LocationUpdate.objects.count(), 1)
        
        location = LocationUpdate.objects.first()
        self.assertEqual(location.asset, self.asset)
        self.assertEqual(str(location.latitude), '40.71280000')

    def test_create_location_update_invalid_asset(self):
        """Test creating location update with invalid asset"""
        url = reverse('locationupdate-list')
        data = {
            'asset_id': 'INVALID',
            'latitude': '40.7128',
            'longitude': '-74.0060',
            'timestamp': timezone.now().isoformat(),
            'source': 'manual'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('asset_id', response.data)

    def test_create_location_update_invalid_coordinates(self):
        """Test creating location update with invalid coordinates"""
        url = reverse('locationupdate-list')
        data = {
            'asset_id': 'TEST001',
            'latitude': '91.0',  # Invalid latitude
            'longitude': '-74.0060',
            'timestamp': timezone.now().isoformat(),
            'source': 'manual'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_location_updates(self):
        """Test listing location updates"""
        LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now(),
            source='manual'
        )
        
        url = reverse('locationupdate-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_latest_locations_endpoint(self):
        """Test latest locations endpoint"""
        LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now(),
            source='manual'
        )
        
        url = reverse('locationupdate-latest')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_manual_entry_endpoint(self):
        """Test manual entry endpoint"""
        url = reverse('locationupdate-manual-entry')
        data = {
            'asset_id': 'TEST001',
            'latitude': '40.7128',
            'longitude': '-74.0060',
            'address': 'New York, NY'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LocationUpdate.objects.count(), 1)
        
        location = LocationUpdate.objects.first()
        self.assertEqual(location.source, 'manual')
        self.assertEqual(location.address, 'New York, NY')

    def test_bulk_create_endpoint(self):
        """Test bulk create endpoint"""
        asset2 = Asset.objects.create(
            asset_id='TEST002',
            make='Test',
            model='Vehicle2',
            year=2023,
            vehicle_type='truck',
            status='active',
            department='Fleet'
        )
        
        url = reverse('locationupdate-bulk-create')
        data = {
            'locations': [
                {
                    'asset_id': 'TEST001',
                    'latitude': '40.7128',
                    'longitude': '-74.0060',
                    'timestamp': timezone.now().isoformat(),
                    'source': 'telematics'
                },
                {
                    'asset_id': 'TEST002',
                    'latitude': '40.7130',
                    'longitude': '-74.0062',
                    'timestamp': timezone.now().isoformat(),
                    'source': 'telematics'
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_count'], 2)
        self.assertEqual(LocationUpdate.objects.count(), 2)

    def test_asset_history_endpoint(self):
        """Test asset history endpoint"""
        LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now(),
            source='manual'
        )
        
        url = reverse('locationupdate-asset-history', kwargs={'asset_id': 'TEST001'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('asset', response.data)
        self.assertIn('locations', response.data)
        self.assertEqual(len(response.data['locations']), 1)
    
    def test_asset_history_with_time_filters(self):
        """Test asset history endpoint with time filters for path tracing"""
        now = timezone.now()
        
        # Create location updates across different time periods
        LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=now - timedelta(days=2),
            source='manual'
        )
        LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7130'),
            longitude=Decimal('-74.0062'),
            timestamp=now - timedelta(hours=12),
            source='gps_device'
        )
        LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7132'),
            longitude=Decimal('-74.0064'),
            timestamp=now,
            source='gps_device'
        )
        
        # Test with days filter
        url = reverse('locationupdate-asset-history', kwargs={'asset_id': 'TEST001'})
        response = self.client.get(url, {'days': 1})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['locations']), 2)  # Only last 24 hours
        
        # Test with limit filter
        response = self.client.get(url, {'limit': 1})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['locations']), 1)  # Only most recent
        
        # Test with combined filters
        response = self.client.get(url, {'days': 7, 'limit': 2})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['locations']), 2)  # Limited to 2 results
    
    def test_asset_history_path_ordering(self):
        """Test that asset history returns locations in chronological order for path tracing"""
        now = timezone.now()
        
        # Create locations out of chronological order
        location3 = LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7132'),
            longitude=Decimal('-74.0064'),
            timestamp=now,
            source='gps_device'
        )
        location1 = LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=now - timedelta(hours=2),
            source='manual'
        )
        location2 = LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7130'),
            longitude=Decimal('-74.0062'),
            timestamp=now - timedelta(hours=1),
            source='gps_device'
        )
        
        url = reverse('locationupdate-asset-history', kwargs={'asset_id': 'TEST001'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        locations = response.data['locations']
        
        # Should be ordered chronologically (oldest first) for path tracing
        self.assertEqual(len(locations), 3)
        timestamps = [location['timestamp'] for location in locations]
        self.assertEqual(timestamps, sorted(timestamps))
    
    def test_asset_history_invalid_asset(self):
        """Test asset history endpoint with invalid asset ID"""
        url = reverse('locationupdate-asset-history', kwargs={'asset_id': 'INVALID'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_asset_history_speed_and_heading_data(self):
        """Test that asset history includes speed and heading data for path analysis"""
        LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now(),
            source='gps_device',
            speed=Decimal('65.5'),
            heading=Decimal('45.0')
        )
        
        url = reverse('locationupdate-asset-history', kwargs={'asset_id': 'TEST001'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        location = response.data['locations'][0]
        
        self.assertIn('speed', location)
        self.assertIn('heading', location)
        self.assertEqual(str(location['speed']), '65.5')
        self.assertEqual(str(location['heading']), '45.0')

    def test_stats_endpoint(self):
        """Test statistics endpoint"""
        LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now(),
            source='manual'
        )
        
        url = reverse('locationupdate-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_updates', response.data)
        self.assertIn('today_updates', response.data)
        self.assertIn('tracking_coverage', response.data)


class LocationZoneAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_location_zone(self):
        """Test creating location zone via API"""
        url = reverse('locationzone-list')
        data = {
            'name': 'Test Depot',
            'description': 'Test depot zone',
            'zone_type': 'depot',
            'center_lat': '40.7128',
            'center_lng': '-74.0060',
            'radius': 1000.0,
            'color': '#1976d2'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LocationZone.objects.count(), 1)
        
        zone = LocationZone.objects.first()
        self.assertEqual(zone.name, 'Test Depot')
        self.assertEqual(zone.zone_type, 'depot')

    def test_create_zone_invalid_color(self):
        """Test creating zone with invalid color"""
        url = reverse('locationzone-list')
        data = {
            'name': 'Test Zone',
            'center_lat': '40.7128',
            'center_lng': '-74.0060',
            'radius': 1000.0,
            'color': 'invalid-color'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('color', response.data)

    def test_create_zone_invalid_radius(self):
        """Test creating zone with invalid radius"""
        url = reverse('locationzone-list')
        data = {
            'name': 'Test Zone',
            'center_lat': '40.7128',
            'center_lng': '-74.0060',
            'radius': 0.5  # Too small
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('radius', response.data)

    def test_check_point_in_zone(self):
        """Test check point in zone endpoint"""
        zone = LocationZone.objects.create(
            name='Test Zone',
            center_lat=Decimal('40.7128'),
            center_lng=Decimal('-74.0060'),
            radius=1000.0
        )
        
        url = reverse('locationzone-check-point', kwargs={'pk': zone.id})
        data = {
            'latitude': 40.7128,  # Same as center
            'longitude': -74.0060  # Same as center
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_within_zone'])


class AssetLocationSummaryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.asset = Asset.objects.create(
            asset_id='TEST001',
            make='Test',
            model='Vehicle',
            year=2023,
            vehicle_type='truck',
            status='active',
            department='Fleet'
        )

    def test_map_data_endpoint(self):
        """Test map data endpoint"""
        # Create location update to generate summary
        LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now(),
            source='manual'
        )
        
        url = reverse('assetlocationsummary-map-data')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('assets', response.data)
        self.assertIn('zones', response.data)
        self.assertIn('last_updated', response.data)

    def test_list_current_locations(self):
        """Test listing current asset locations"""
        # Create location update to generate summary
        LocationUpdate.objects.create(
            asset=self.asset,
            latitude=Decimal('40.7128'),
            longitude=Decimal('-74.0060'),
            timestamp=timezone.now(),
            source='manual'
        )
        
        url = reverse('assetlocationsummary-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertIn('results', response.data)


class LocationUpdatePermissionTests(APITestCase):
    def setUp(self):
        self.asset = Asset.objects.create(
            asset_id='TEST001',
            make='Test',
            model='Vehicle',
            year=2023,
            vehicle_type='truck',
            status='active',
            department='Fleet'
        )

    def test_unauthenticated_access(self):
        """Test that unauthenticated requests are rejected"""
        url = reverse('locationupdate-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_location_without_auth(self):
        """Test creating location without authentication"""
        url = reverse('locationupdate-list')
        data = {
            'asset_id': 'TEST001',
            'latitude': '40.7128',
            'longitude': '-74.0060',
            'timestamp': timezone.now().isoformat(),
            'source': 'manual'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
