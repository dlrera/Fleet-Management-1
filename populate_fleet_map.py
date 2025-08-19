#!/usr/bin/env python
"""
Populate the fleet map with realistic locations and assets
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
print(f"Logged in successfully with token: {token[:20]}...")

# Define realistic locations across different regions
LOCATIONS = [
    # West Coast
    {
        'name': 'San Francisco Hub',
        'address': '1234 Market Street, San Francisco, CA 94102',
        'latitude': 37.7749,
        'longitude': -122.4194,
        'location_type': 'depot'
    },
    {
        'name': 'Los Angeles Distribution Center',
        'address': '5678 Wilshire Blvd, Los Angeles, CA 90036',
        'latitude': 34.0522,
        'longitude': -118.2437,
        'location_type': 'depot'
    },
    {
        'name': 'Seattle Operations',
        'address': '901 Pike Street, Seattle, WA 98101',
        'latitude': 47.6062,
        'longitude': -122.3321,
        'location_type': 'depot'
    },
    {
        'name': 'Portland Satellite Office',
        'address': '234 SW Morrison St, Portland, OR 97204',
        'latitude': 45.5152,
        'longitude': -122.6784,
        'location_type': 'service_center'
    },
    
    # East Coast
    {
        'name': 'New York Main Depot',
        'address': '789 Broadway, New York, NY 10003',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'location_type': 'depot'
    },
    {
        'name': 'Boston Service Center',
        'address': '456 Commonwealth Ave, Boston, MA 02215',
        'latitude': 42.3601,
        'longitude': -71.0589,
        'location_type': 'service_center'
    },
    {
        'name': 'Washington DC Fleet Base',
        'address': '1600 Pennsylvania Ave, Washington, DC 20500',
        'latitude': 38.9072,
        'longitude': -77.0369,
        'location_type': 'depot'
    },
    {
        'name': 'Miami Regional Hub',
        'address': '321 Ocean Drive, Miami, FL 33139',
        'latitude': 25.7617,
        'longitude': -80.1918,
        'location_type': 'depot'
    },
    
    # Central US
    {
        'name': 'Chicago Central Depot',
        'address': '123 N Michigan Ave, Chicago, IL 60601',
        'latitude': 41.8781,
        'longitude': -87.6298,
        'location_type': 'depot'
    },
    {
        'name': 'Dallas Operations Center',
        'address': '567 Main Street, Dallas, TX 75201',
        'latitude': 32.7767,
        'longitude': -96.7970,
        'location_type': 'depot'
    },
    {
        'name': 'Denver Mountain Region',
        'address': '890 16th Street, Denver, CO 80202',
        'latitude': 39.7392,
        'longitude': -104.9903,
        'location_type': 'service_center'
    },
    {
        'name': 'Phoenix Desert Hub',
        'address': '234 E Washington St, Phoenix, AZ 85004',
        'latitude': 33.4484,
        'longitude': -112.0740,
        'location_type': 'depot'
    },
    
    # Additional strategic locations
    {
        'name': 'Atlanta Southeast Hub',
        'address': '456 Peachtree St, Atlanta, GA 30303',
        'latitude': 33.7490,
        'longitude': -84.3880,
        'location_type': 'depot'
    },
    {
        'name': 'Minneapolis North Central',
        'address': '789 Nicollet Mall, Minneapolis, MN 55402',
        'latitude': 44.9778,
        'longitude': -93.2650,
        'location_type': 'service_center'
    },
    {
        'name': 'Las Vegas Distribution',
        'address': '123 Las Vegas Blvd, Las Vegas, NV 89101',
        'latitude': 36.1699,
        'longitude': -115.1398,
        'location_type': 'depot'
    }
]

# Vehicle data for creating assets
VEHICLES = [
    # Trucks
    {'make': 'Ford', 'model': 'F-150', 'type': 'Pickup Truck', 'year_range': (2020, 2024)},
    {'make': 'Chevrolet', 'model': 'Silverado 1500', 'type': 'Pickup Truck', 'year_range': (2019, 2024)},
    {'make': 'Ram', 'model': '1500', 'type': 'Pickup Truck', 'year_range': (2020, 2024)},
    {'make': 'Ford', 'model': 'F-250', 'type': 'Heavy Duty Truck', 'year_range': (2019, 2023)},
    
    # Vans
    {'make': 'Ford', 'model': 'Transit', 'type': 'Cargo Van', 'year_range': (2020, 2024)},
    {'make': 'Mercedes-Benz', 'model': 'Sprinter', 'type': 'Cargo Van', 'year_range': (2019, 2024)},
    {'make': 'Chevrolet', 'model': 'Express 2500', 'type': 'Cargo Van', 'year_range': (2018, 2023)},
    {'make': 'Nissan', 'model': 'NV200', 'type': 'Compact Van', 'year_range': (2020, 2023)},
    
    # SUVs
    {'make': 'Chevrolet', 'model': 'Tahoe', 'type': 'SUV', 'year_range': (2021, 2024)},
    {'make': 'Ford', 'model': 'Explorer', 'type': 'SUV', 'year_range': (2020, 2024)},
    {'make': 'Toyota', 'model': 'Highlander', 'type': 'SUV', 'year_range': (2020, 2024)},
    
    # Sedans
    {'make': 'Toyota', 'model': 'Camry', 'type': 'Sedan', 'year_range': (2021, 2024)},
    {'make': 'Honda', 'model': 'Accord', 'type': 'Sedan', 'year_range': (2020, 2024)},
    
    # Electric Vehicles
    {'make': 'Tesla', 'model': 'Model 3', 'type': 'Electric Sedan', 'year_range': (2021, 2024)},
    {'make': 'Ford', 'model': 'F-150 Lightning', 'type': 'Electric Truck', 'year_range': (2022, 2024)},
    {'make': 'Rivian', 'model': 'R1T', 'type': 'Electric Truck', 'year_range': (2022, 2024)},
]

STATUSES = ['active', 'active', 'active', 'maintenance', 'retired']  # More active vehicles

print("\n" + "="*60)
print("CREATING LOCATIONS")
print("="*60)

location_ids = []
for loc_data in LOCATIONS:
    response = requests.post(
        f'{API_URL}/locations/locations/',
        json=loc_data,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        location = response.json()
        location_ids.append(location['id'])
        print(f"[OK] Created location: {loc_data['name']} ({loc_data['location_type']})")
    elif response.status_code == 400:
        # Location might already exist, try to get it
        response = requests.get(
            f'{API_URL}/locations/locations/',
            headers=headers
        )
        if response.status_code == 200:
            locations = response.json()
            existing = next((l for l in locations if l['name'] == loc_data['name']), None)
            if existing:
                location_ids.append(existing['id'])
                print(f"  Location already exists: {loc_data['name']}")
    else:
        print(f"[FAIL] Failed to create location: {loc_data['name']} - {response.status_code}")

print(f"\nTotal locations available: {len(location_ids)}")

print("\n" + "="*60)
print("CREATING ASSETS")
print("="*60)

# Generate VIN
def generate_vin():
    """Generate a realistic-looking VIN"""
    chars = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789'
    return ''.join(random.choices(chars, k=17))

# Create multiple assets for each location
asset_count = 0
for location_id in location_ids:
    # Create 3-6 vehicles per location
    num_vehicles = random.randint(3, 6)
    
    for i in range(num_vehicles):
        vehicle = random.choice(VEHICLES)
        year = random.randint(*vehicle['year_range'])
        
        asset_data = {
            'asset_id': f'FLEET-{location_id:03d}-{i+1:03d}',
            'vin': generate_vin(),
            'make': vehicle['make'],
            'model': vehicle['model'],
            'year': year,
            'license_plate': f'{random.choice(["CA", "NY", "TX", "FL", "IL", "WA", "OR", "AZ", "NV", "GA", "MA", "DC", "MN", "CO"])}-{random.randint(1000, 9999)}',
            'color': random.choice(['White', 'Black', 'Silver', 'Gray', 'Blue', 'Red', 'Green']),
            'status': random.choice(STATUSES),
            'mileage': random.randint(5000, 150000),
            'fuel_type': 'Electric' if 'Electric' in vehicle['type'] else random.choice(['Gasoline', 'Diesel', 'Hybrid']),
            'location': location_id,
            'purchase_date': f'{year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
            'purchase_price': random.randint(25000, 85000),
            'notes': f'{vehicle["type"]} - {random.choice(["Regular maintenance schedule", "Fleet vehicle", "Executive transport", "Delivery vehicle", "Service vehicle", "Long-haul transport"])}'
        }
        
        response = requests.post(
            f'{API_URL}/assets/assets/',
            json=asset_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            asset_count += 1
            print(f"[OK] Created asset: {asset_data['asset_id']} - {vehicle['make']} {vehicle['model']} ({asset_data['status']})")
        elif response.status_code == 400 and 'already exists' in response.text.lower():
            print(f"  Asset already exists: {asset_data['asset_id']}")
        else:
            print(f"[FAIL] Failed to create asset: {asset_data['asset_id']} - {response.status_code}")

print(f"\nTotal assets created: {asset_count}")

print("\n" + "="*60)
print("FLEET MAP POPULATION COMPLETE")
print("="*60)

# Get summary statistics
response = requests.get(f'{API_URL}/locations/locations/', headers=headers)
if response.status_code == 200:
    locations = response.json()
    print(f"\nLocation Summary:")
    print(f"  Total Locations: {len(locations)}")
    depots = [l for l in locations if l.get('location_type') == 'depot']
    service_centers = [l for l in locations if l.get('location_type') == 'service_center']
    print(f"  Depots: {len(depots)}")
    print(f"  Service Centers: {len(service_centers)}")

response = requests.get(f'{API_URL}/assets/', headers=headers)
if response.status_code == 200:
    data = response.json()
    assets = data.get('results', []) if 'results' in data else data
    print(f"\nAsset Summary:")
    print(f"  Total Assets: {len(assets)}")
    active = [a for a in assets if a.get('status') == 'active']
    maintenance = [a for a in assets if a.get('status') == 'maintenance']
    retired = [a for a in assets if a.get('status') == 'retired']
    print(f"  Active: {len(active)}")
    print(f"  In Maintenance: {len(maintenance)}")
    print(f"  Retired: {len(retired)}")

print("\n[SUCCESS] Fleet map is now populated with realistic data!")
print("   - Locations span across major US cities")
print("   - Diverse fleet of vehicles including electric options")
print("   - Various statuses to show operational reality")
print("\nOpen http://localhost:3000/locations to see the populated map!")