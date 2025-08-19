#!/usr/bin/env python
"""
Populate the fleet map with location zones and asset location updates
"""
import requests
import json
import random
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:8000'
API_URL = f'{BASE_URL}/api'

# Login as admin
print("Authenticating as admin...")
response = requests.post(
    f'{API_URL}/auth/login/',
    json={'username': 'admin', 'password': 'admin123'}
)

if response.status_code != 200:
    print(f"Failed to login: {response.status_code}")
    exit(1)

token = response.json()['token']
headers = {'Authorization': f'Token {token}'}
print(f"Logged in successfully!")

# Define location zones (depots and service areas)
ZONES = [
    # West Coast
    {
        'name': 'San Francisco Hub',
        'zone_type': 'depot',
        'center_lat': 37.7749,
        'center_lng': -122.4194,
        'radius': 5000,  # 5km radius
        'description': 'Main West Coast distribution hub'
    },
    {
        'name': 'Los Angeles Distribution Center',
        'zone_type': 'depot',
        'center_lat': 34.0522,
        'center_lng': -118.2437,
        'radius': 7000,
        'description': 'Southern California operations center'
    },
    {
        'name': 'Seattle Operations',
        'zone_type': 'depot',
        'center_lat': 47.6062,
        'center_lng': -122.3321,
        'radius': 4500,
        'description': 'Pacific Northwest hub'
    },
    # East Coast
    {
        'name': 'New York Main Depot',
        'zone_type': 'depot',
        'center_lat': 40.7128,
        'center_lng': -74.0060,
        'radius': 8000,
        'description': 'East Coast headquarters'
    },
    {
        'name': 'Boston Service Center',
        'zone_type': 'service_area',
        'center_lat': 42.3601,
        'center_lng': -71.0589,
        'radius': 3500,
        'description': 'New England service facility'
    },
    {
        'name': 'Miami Regional Hub',
        'zone_type': 'depot',
        'center_lat': 25.7617,
        'center_lng': -80.1918,
        'radius': 6000,
        'description': 'Southeast distribution center'
    },
    # Central US
    {
        'name': 'Chicago Central Depot',
        'zone_type': 'depot',
        'center_lat': 41.8781,
        'center_lng': -87.6298,
        'radius': 5500,
        'description': 'Midwest operations hub'
    },
    {
        'name': 'Dallas Operations Center',
        'zone_type': 'depot',
        'center_lat': 32.7767,
        'center_lng': -96.7970,
        'radius': 6500,
        'description': 'Texas regional center'
    },
    {
        'name': 'Denver Mountain Region',
        'zone_type': 'service_area',
        'center_lat': 39.7392,
        'center_lng': -104.9903,
        'radius': 4000,
        'description': 'Rocky Mountain service area'
    },
]

print("\n" + "="*60)
print("CREATING LOCATION ZONES")
print("="*60)

zone_ids = []
for zone_data in ZONES:
    response = requests.post(
        f'{API_URL}/locations/zones/',
        json=zone_data,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        zone = response.json()
        zone_ids.append(zone['id'])
        print(f"[OK] Created zone: {zone_data['name']} ({zone_data['zone_type']})")
    else:
        print(f"[FAIL] Failed to create zone: {zone_data['name']} - {response.status_code}")
        # Try to get existing zones
        response = requests.get(f'{API_URL}/locations/zones/', headers=headers)
        if response.status_code == 200:
            zones = response.json()
            existing = next((z for z in zones if z['name'] == zone_data['name']), None)
            if existing:
                zone_ids.append(existing['id'])
                print(f"     Zone already exists: {zone_data['name']}")

print(f"\nTotal zones available: {len(zone_ids)}")

print("\n" + "="*60)
print("CREATING VEHICLE LOCATION UPDATES")
print("="*60)

# Get all assets
response = requests.get(f'{API_URL}/assets/', headers=headers)
if response.status_code != 200:
    print(f"Failed to get assets: {response.status_code}")
    exit(1)

data = response.json()
assets = data.get('results', []) if 'results' in data else data

if not assets:
    print("No assets found. Creating sample assets first...")
    
    # Create some sample assets
    SAMPLE_VEHICLES = [
        {'make': 'Ford', 'model': 'F-150', 'year': 2023, 'type': 'Truck'},
        {'make': 'Chevrolet', 'model': 'Silverado', 'year': 2023, 'type': 'Truck'},
        {'make': 'Ford', 'model': 'Transit', 'year': 2022, 'type': 'Van'},
        {'make': 'Mercedes-Benz', 'model': 'Sprinter', 'year': 2023, 'type': 'Van'},
        {'make': 'Tesla', 'model': 'Model 3', 'year': 2023, 'type': 'Sedan'},
        {'make': 'Chevrolet', 'model': 'Tahoe', 'year': 2022, 'type': 'SUV'},
        {'make': 'Ford', 'model': 'Explorer', 'year': 2023, 'type': 'SUV'},
        {'make': 'Rivian', 'model': 'R1T', 'year': 2023, 'type': 'Electric Truck'},
    ]
    
    for i, vehicle in enumerate(SAMPLE_VEHICLES):
        asset_data = {
            'asset_id': f'FLEET-{i+1:03d}',
            'vin': ''.join(random.choices('ABCDEFGHJKLMNPRSTUVWXYZ0123456789', k=17)),
            'make': vehicle['make'],
            'model': vehicle['model'],
            'year': vehicle['year'],
            'license_plate': f'{random.choice(["CA", "NY", "TX"])}-{random.randint(1000, 9999)}',
            'status': random.choice(['active', 'active', 'active', 'maintenance']),
            'mileage': random.randint(5000, 50000),
            'fuel_type': 'Electric' if 'Electric' in vehicle.get('type', '') else 'Gasoline',
            'purchase_date': f'{vehicle["year"]}-01-{random.randint(1, 28):02d}',
            'notes': f'{vehicle["type"]} - Fleet vehicle'
        }
        
        response = requests.post(
            f'{API_URL}/assets/assets/',
            json=asset_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            print(f"[OK] Created asset: {asset_data['asset_id']} - {vehicle['make']} {vehicle['model']}")
        else:
            print(f"[FAIL] Failed to create asset: {asset_data['asset_id']} - {response.status_code}")
    
    # Re-fetch assets
    response = requests.get(f'{API_URL}/assets/', headers=headers)
    data = response.json()
    assets = data.get('results', []) if 'results' in data else data

print(f"\nTotal assets found: {len(assets)}")

# Create location updates for each asset
location_count = 0
for asset in assets[:20]:  # Limit to first 20 assets to avoid overwhelming
    # Pick a random zone for this asset
    if zone_ids:
        zone_id = random.choice(zone_ids)
        
        # Get zone details
        zone_response = requests.get(f'{API_URL}/locations/zones/{zone_id}/', headers=headers)
        if zone_response.status_code == 200:
            zone = zone_response.json()
            
            # Generate a random location within the zone's radius
            # This is a simplified calculation - in reality you'd use proper geographic calculations
            lat_offset = random.uniform(-0.05, 0.05)
            lon_offset = random.uniform(-0.05, 0.05)
            
            location_data = {
                'asset': asset['id'],
                'asset_id': asset['asset_id'],  # Add asset_id field
                'latitude': round(float(zone['center_lat']) + lat_offset, 6),  # Limit decimal places
                'longitude': round(float(zone['center_lng']) + lon_offset, 6),  # Limit decimal places
                'speed': random.uniform(0, 65) if asset['status'] == 'active' else 0,
                'heading': random.randint(0, 359),
                'accuracy': random.uniform(5, 20),
                'source': random.choice(['gps_device', 'mobile_app', 'manual']),
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f'{API_URL}/locations/updates/',
                json=location_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                location_count += 1
                status_text = "[ACTIVE]" if asset['status'] == 'active' else "[MAINT]"
                print(f"[OK] {status_text} Asset {asset['asset_id']} positioned near {zone['name']}")
            else:
                print(f"[FAIL] Failed to update location for {asset['asset_id']}: {response.status_code}")
                if response.status_code == 400:
                    print(f"      Error: {response.json()}")
    else:
        # Create location without zone
        location_data = {
            'asset': asset['id'],
            'latitude': random.uniform(25.0, 48.0),  # US latitude range
            'longitude': random.uniform(-125.0, -66.0),  # US longitude range
            'speed': random.uniform(0, 65) if asset['status'] == 'active' else 0,
            'heading': random.randint(0, 359),
            'accuracy': random.uniform(5, 20),
            'location_source': 'gps',
            'timestamp': datetime.now().isoformat()
        }
        
        response = requests.post(
            f'{API_URL}/locations/updates/',
            json=location_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            location_count += 1
            print(f"[OK] Asset {asset['asset_id']} positioned")

print(f"\nTotal location updates created: {location_count}")

print("\n" + "="*60)
print("GETTING MAP DATA")
print("="*60)

# Get optimized map data
response = requests.get(f'{API_URL}/locations/current/map_data/', headers=headers)
if response.status_code == 200:
    map_data = response.json()
    print(f"Map data retrieved:")
    print(f"  Active vehicles: {len([a for a in map_data.get('assets', []) if a.get('status') == 'active'])}")
    print(f"  In maintenance: {len([a for a in map_data.get('assets', []) if a.get('status') == 'maintenance'])}")
    print(f"  Total zones: {len(map_data.get('zones', []))}")
    
    # Show distribution by zone
    if 'zones' in map_data:
        for zone in map_data['zones'][:5]:  # Show first 5 zones
            assets_in_zone = zone.get('asset_count', 0)
            print(f"  {zone['name']}: {assets_in_zone} assets")

print("\n" + "="*60)
print("FLEET MAP POPULATION COMPLETE")
print("="*60)

print("\n[SUCCESS] Fleet map is now populated with realistic data!")
print("   - Location zones created across major US cities")
print("   - Asset locations distributed across zones")
print("   - Real-time tracking data simulated")
print("   - Different vehicle statuses shown on map")
print("\nOpen http://localhost:3000/locations to see the populated map!")
print("\nMap Legend:")
print("   [TRUCK] Active vehicles (moving)")
print("   [WRENCH] Vehicles in maintenance (stationary)")
print("   [PIN] Depot zones")
print("   [SERVICE] Service zones")