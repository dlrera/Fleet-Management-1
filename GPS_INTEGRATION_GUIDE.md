# GPS Integration Guide for Fleet Management System

## Overview
This guide outlines how to integrate external GPS tracking devices/services with your Fleet Management System.

## Current System Capabilities

Your system already has the infrastructure ready for GPS integration:

### Existing Backend Support
1. **LocationUpdate Model** - Stores GPS coordinates with timestamps
   - Fields: latitude, longitude, timestamp, source, asset
   - Source types: 'manual', 'gps_device', 'mobile_app', 'telematics'

2. **API Endpoints Ready**
   - `POST /api/locations/updates/` - Create location updates
   - `GET /api/locations/current/` - Get current locations
   - `GET /api/locations/current/map_data/` - Get map visualization data

3. **Real-time Tracking Infrastructure**
   - AssetLocationSummary model for current positions
   - Time-based filtering (last 1hr, 6hr, 24hr, etc.)
   - Zone detection and alerts

## Integration Options

### Option 1: Direct API Integration (Recommended for Most GPS Providers)

**What You Need:**
- GPS tracking devices with cellular/satellite connectivity
- GPS provider's API credentials
- Webhook endpoint or polling service

**Implementation Steps:**

1. **Create GPS Integration Service**
```python
# backend/locations/gps_integration.py
import requests
from datetime import datetime
from locations.models import LocationUpdate
from assets.models import Asset

class GPSIntegrationService:
    def __init__(self, provider_name, api_key):
        self.provider = provider_name
        self.api_key = api_key
    
    def fetch_locations(self):
        """Poll GPS provider for latest positions"""
        # Example for common GPS provider
        response = requests.get(
            f'https://api.{self.provider}.com/v1/positions',
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        return response.json()
    
    def process_gps_data(self, gps_data):
        """Convert GPS provider data to LocationUpdate"""
        for device in gps_data:
            # Map device ID to your asset
            asset = Asset.objects.filter(
                gps_device_id=device['device_id']
            ).first()
            
            if asset:
                LocationUpdate.objects.create(
                    asset=asset,
                    latitude=device['lat'],
                    longitude=device['lng'],
                    timestamp=device['timestamp'],
                    source='gps_device',
                    speed=device.get('speed'),
                    heading=device.get('heading'),
                    accuracy=device.get('accuracy', 10)
                )
```

2. **Add Webhook Receiver**
```python
# backend/locations/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def gps_webhook(request):
    """Receive GPS updates via webhook"""
    data = request.data
    
    # Validate webhook signature (provider-specific)
    if not validate_webhook_signature(request):
        return Response({'error': 'Invalid signature'}, status=401)
    
    # Process GPS data
    service = GPSIntegrationService()
    service.process_gps_data(data['positions'])
    
    return Response({'status': 'received'})
```

3. **Set Up Periodic Polling (Alternative to Webhooks)**
```python
# backend/locations/tasks.py
from celery import shared_task
from .gps_integration import GPSIntegrationService

@shared_task
def poll_gps_positions():
    """Poll GPS provider every 30 seconds"""
    service = GPSIntegrationService(
        provider_name='your_provider',
        api_key='your_api_key'
    )
    
    gps_data = service.fetch_locations()
    service.process_gps_data(gps_data)
```

### Option 2: MQTT Integration (For Real-time Streaming)

**What You Need:**
- GPS devices supporting MQTT
- MQTT broker (e.g., Mosquitto)
- Django Channels for WebSocket support

**Implementation:**
```python
# backend/locations/mqtt_client.py
import paho.mqtt.client as mqtt
import json
from locations.models import LocationUpdate
from assets.models import Asset

class GPSMQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
    
    def on_connect(self, client, userdata, flags, rc):
        # Subscribe to GPS topic
        client.subscribe("fleet/+/location")
    
    def on_message(self, client, userdata, msg):
        # Parse GPS data
        topic_parts = msg.topic.split('/')
        device_id = topic_parts[1]
        data = json.loads(msg.payload)
        
        # Store in database
        asset = Asset.objects.filter(gps_device_id=device_id).first()
        if asset:
            LocationUpdate.objects.create(
                asset=asset,
                latitude=data['lat'],
                longitude=data['lng'],
                timestamp=data['timestamp'],
                source='gps_device'
            )
```

### Option 3: CSV/FTP Batch Import (For Legacy Systems)

**What You Need:**
- FTP access to GPS provider's data
- Scheduled import job

**Implementation:**
```python
# backend/locations/batch_import.py
import csv
import ftplib
from datetime import datetime

def import_gps_batch():
    """Import GPS data from FTP CSV files"""
    ftp = ftplib.FTP('ftp.gpsprovider.com')
    ftp.login('username', 'password')
    
    # Download latest GPS data file
    with open('gps_data.csv', 'wb') as f:
        ftp.retrbinary('RETR latest_positions.csv', f.write)
    
    # Process CSV
    with open('gps_data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            asset = Asset.objects.filter(
                asset_id=row['vehicle_id']
            ).first()
            
            if asset:
                LocationUpdate.objects.create(
                    asset=asset,
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    source='gps_device'
                )
```

## Popular GPS Provider Integrations

### 1. **Samsara**
- REST API with webhooks
- Real-time vehicle tracking
- Integration: Direct API
```python
# Samsara example
headers = {'Authorization': f'Bearer {SAMSARA_API_TOKEN}'}
response = requests.get(
    'https://api.samsara.com/fleet/vehicles/locations',
    headers=headers
)
```

### 2. **Geotab**
- SDK available for Python
- Real-time and historical data
- Integration: SDK or API
```python
# Geotab example
from mygeotab import API
api = API(username='user', password='pass', database='db')
devices = api.get('Device')
```

### 3. **Verizon Connect**
- REST API
- Webhook support
- Integration: API + Webhooks

### 4. **Fleet Complete**
- REST API
- Real-time tracking
- Integration: Direct API

### 5. **GPS Trackit**
- REST API
- Batch exports
- Integration: API or FTP

## Database Schema Updates Needed

Add GPS-specific fields to your Asset model:

```python
# backend/assets/models.py
class Asset(models.Model):
    # ... existing fields ...
    
    # GPS Integration fields
    gps_device_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        unique=True,
        help_text="External GPS device/unit ID"
    )
    gps_provider = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('samsara', 'Samsara'),
            ('geotab', 'Geotab'),
            ('verizon', 'Verizon Connect'),
            ('fleetcomplete', 'Fleet Complete'),
            ('gpstrackit', 'GPS Trackit'),
            ('custom', 'Custom Provider'),
        ]
    )
    gps_enabled = models.BooleanField(default=False)
    gps_update_frequency = models.IntegerField(
        default=30,
        help_text="Update frequency in seconds"
    )
```

## API Authentication & Security

### 1. **Webhook Security**
```python
# Verify webhook signatures
import hmac
import hashlib

def validate_webhook_signature(request):
    signature = request.headers.get('X-Webhook-Signature')
    body = request.body
    
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)
```

### 2. **API Key Storage**
```python
# backend/config/settings.py
GPS_PROVIDERS = {
    'samsara': {
        'api_key': os.environ.get('SAMSARA_API_KEY'),
        'webhook_secret': os.environ.get('SAMSARA_WEBHOOK_SECRET'),
    },
    'geotab': {
        'username': os.environ.get('GEOTAB_USERNAME'),
        'password': os.environ.get('GEOTAB_PASSWORD'),
        'database': os.environ.get('GEOTAB_DATABASE'),
    }
}
```

## Frontend Updates

The frontend is already configured to display GPS data:
- Map visualization works with any LocationUpdate records
- Real-time updates can be added with WebSockets
- Time filtering already implemented

### Add Real-time Updates (Optional)
```javascript
// frontend/src/stores/locations.js
import { io } from 'socket.io-client'

const socket = io('ws://localhost:8000/ws/locations/')

socket.on('location_update', (data) => {
  // Update map marker position
  this.updateAssetLocation(data.asset_id, data.latitude, data.longitude)
})
```

## Implementation Checklist

### Phase 1: Basic Integration
- [ ] Choose GPS provider
- [ ] Obtain API credentials
- [ ] Add gps_device_id field to Asset model
- [ ] Create GPS integration service
- [ ] Test with single vehicle

### Phase 2: Full Deployment
- [ ] Map all vehicles to GPS device IDs
- [ ] Set up webhook endpoint or polling
- [ ] Configure update frequency
- [ ] Add error handling and logging
- [ ] Set up monitoring/alerts

### Phase 3: Advanced Features
- [ ] Real-time WebSocket updates
- [ ] Geofencing alerts
- [ ] Route optimization
- [ ] Historical playback
- [ ] Driver behavior monitoring

## Testing GPS Integration

```python
# Test script: test_gps_integration.py
from locations.models import LocationUpdate
from assets.models import Asset
from datetime import datetime

def test_gps_update():
    # Create test GPS update
    asset = Asset.objects.first()
    
    location = LocationUpdate.objects.create(
        asset=asset,
        latitude=40.7128,
        longitude=-74.0060,
        timestamp=datetime.now(),
        source='gps_device',
        speed=35.5,
        heading=180,
        accuracy=5
    )
    
    print(f"GPS update created: {location}")
    print(f"View at: http://localhost:3000/locations")
    
    # Verify it appears in API
    response = requests.get(
        'http://localhost:8000/api/locations/current/map_data/',
        headers={'Authorization': 'Token YOUR_TOKEN'}
    )
    
    data = response.json()
    print(f"Assets on map: {len(data['assets'])}")
```

## Common GPS Data Fields

Most GPS providers send these fields:
- **latitude**: Decimal degrees (e.g., 40.7128)
- **longitude**: Decimal degrees (e.g., -74.0060)
- **timestamp**: ISO 8601 format
- **speed**: km/h or mph
- **heading**: Degrees (0-360)
- **altitude**: Meters above sea level
- **accuracy**: GPS accuracy in meters
- **satellite_count**: Number of satellites
- **ignition_status**: On/Off
- **odometer**: Total distance
- **fuel_level**: Percentage or liters
- **engine_hours**: Total runtime

## Troubleshooting

### Issue: GPS updates not showing on map
- Check LocationUpdate records in Django admin
- Verify asset.gps_device_id matches incoming data
- Check time filter on map (may be filtering out old data)

### Issue: Duplicate location records
- Implement deduplication in process_gps_data()
- Check if provider sends multiple webhooks

### Issue: Incorrect timezone
- Ensure GPS timestamps are converted to UTC
- Use Django's timezone.make_aware() for naive datetimes

## Support & Next Steps

1. **Choose your GPS provider** based on:
   - Coverage area needed
   - Update frequency requirements
   - Budget
   - Additional features (fuel, diagnostics, etc.)

2. **Contact GPS provider** for:
   - API documentation
   - Test account/sandbox
   - Device IDs for your vehicles
   - Webhook setup assistance

3. **Start with pilot program**:
   - Test with 1-2 vehicles first
   - Verify data accuracy
   - Train staff on new features
   - Roll out to full fleet

## Additional Resources
- [Django Channels (for WebSockets)](https://channels.readthedocs.io/)
- [Celery (for background tasks)](https://docs.celeryproject.org/)
- [MQTT Python Client](https://pypi.org/project/paho-mqtt/)
- [GeoPy (for geocoding)](https://geopy.readthedocs.io/)