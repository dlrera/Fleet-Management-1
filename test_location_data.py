import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
django.setup()

from locations.models import LocationUpdate, AssetLocationSummary
from assets.models import Asset

def create_test_location_data():
    """Create location data with various timestamps to test filtering"""
    
    # Get some assets
    assets = Asset.objects.filter(status='active')[:5]
    
    if not assets:
        print("No active assets found. Please create some assets first.")
        return
    
    now = timezone.now()
    
    # Create location updates with different timestamps
    test_data = [
        (assets[0], now - timedelta(minutes=30), "30 minutes ago"),
        (assets[1], now - timedelta(hours=2), "2 hours ago"),
        (assets[2], now - timedelta(hours=8), "8 hours ago"),
        (assets[3], now - timedelta(hours=25), "25 hours ago"),
        (assets[4] if len(assets) > 4 else assets[0], now - timedelta(days=4), "4 days ago"),
    ]
    
    for asset, timestamp, description in test_data:
        # Create location update
        location = LocationUpdate.objects.create(
            asset=asset,
            timestamp=timestamp,
            latitude=40.7128 + (timestamp.hour * 0.001),  # Slightly different locations
            longitude=-74.0060 + (timestamp.minute * 0.001),
            source='manual'
        )
        
        # Update or create summary
        summary, created = AssetLocationSummary.objects.update_or_create(
            asset=asset,
            defaults={
                'timestamp': timestamp,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'source': 'manual',
                'address': f"Test Address - {description}"
            }
        )
        
        print(f"Created location for {asset.asset_id}: {description}")
    
    # Test the filtering
    print("\n--- Testing Filters ---")
    
    for hours in [1, 6, 24, 72, 168]:
        threshold = now - timedelta(hours=hours)
        count = AssetLocationSummary.objects.filter(
            timestamp__gte=threshold
        ).values('asset').distinct().count()
        print(f"Within {hours} hours: {count} assets")

if __name__ == "__main__":
    create_test_location_data()