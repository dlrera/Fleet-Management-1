#!/usr/bin/env python
"""
Set up Western New York fleet locations
"""
import requests
import json
import random
from datetime import datetime

BASE_URL = 'http://localhost:8000'
API_URL = f'{BASE_URL}/api'

# Login
print("Authenticating...")
response = requests.post(f'{API_URL}/auth/login/', json={'username': 'admin', 'password': 'admin123'})
if response.status_code != 200:
    print(f"Failed to login")
    exit(1)

token = response.json()['token']
headers = {'Authorization': f'Token {token}'}
print("Logged in successfully!")

# Western New York zones
WNY_ZONES = [
    # Buffalo Metro
    {'name': 'Buffalo Downtown Depot', 'zone_type': 'depot', 'center_lat': 42.8864, 'center_lng': -78.8784, 'radius': 5000, 'description': 'Main Buffalo hub'},
    {'name': 'Buffalo Airport', 'zone_type': 'depot', 'center_lat': 42.9405, 'center_lng': -78.7322, 'radius': 4000, 'description': 'Airport logistics'},
    {'name': 'Amherst Operations', 'zone_type': 'depot', 'center_lat': 42.9786, 'center_lng': -78.7998, 'radius': 3500, 'description': 'North Buffalo'},
    {'name': 'Cheektowaga Hub', 'zone_type': 'depot', 'center_lat': 42.9034, 'center_lng': -78.7542, 'radius': 3500, 'description': 'East Buffalo'},
    {'name': 'West Seneca Base', 'zone_type': 'service_area', 'center_lat': 42.8500, 'center_lng': -78.7997, 'radius': 3000, 'description': 'South Buffalo service'},
    
    # Rochester Metro  
    {'name': 'Rochester Downtown', 'zone_type': 'depot', 'center_lat': 43.1566, 'center_lng': -77.6088, 'radius': 4500, 'description': 'Rochester main'},
    {'name': 'Henrietta Center', 'zone_type': 'service_area', 'center_lat': 43.0631, 'center_lng': -77.6120, 'radius': 3500, 'description': 'South Rochester'},
    {'name': 'Greece Operations', 'zone_type': 'depot', 'center_lat': 43.2099, 'center_lng': -77.6931, 'radius': 3000, 'description': 'Northwest Rochester'},
    
    # Between Cities
    {'name': 'Batavia Distribution', 'zone_type': 'depot', 'center_lat': 42.9981, 'center_lng': -78.1875, 'radius': 4000, 'description': 'Midpoint depot'},
    
    # Niagara
    {'name': 'Niagara Falls Hub', 'zone_type': 'depot', 'center_lat': 43.0962, 'center_lng': -79.0377, 'radius': 4500, 'description': 'Border crossing'},
]

print("\n" + "="*60)
print("CREATING WESTERN NEW YORK ZONES")
print("="*60)

zone_ids = []
for zone in WNY_ZONES:
    resp = requests.post(f'{API_URL}/locations/zones/', json=zone, headers=headers)
    if resp.status_code in [200, 201]:
        zone_ids.append(resp.json()['id'])
        print(f"[OK] Created: {zone['name']}")
    else:
        # Try to get existing
        get_resp = requests.get(f'{API_URL}/locations/zones/', headers=headers)
        if get_resp.status_code == 200:
            zones_list = get_resp.json()
            if isinstance(zones_list, list):
                for z in zones_list:
                    if z.get('name') == zone['name']:
                        zone_ids.append(z['id'])
                        print(f"[EXISTS] {zone['name']}")
                        break

print(f"\nZones available: {len(zone_ids)}")

print("\n" + "="*60)
print("POSITIONING FLEET IN WESTERN NY")
print("="*60)

# Get existing assets
resp = requests.get(f'{API_URL}/assets/', headers=headers)
if resp.status_code == 200:
    data = resp.json()
    assets = data.get('results', []) if 'results' in data else data
    
    print(f"Found {len(assets)} assets to position")
    
    # Position each asset in WNY
    for i, asset in enumerate(assets[:15]):  # Limit to 15 for quick setup
        if zone_ids:
            zone_id = zone_ids[i % len(zone_ids)]
            
            # Get zone info
            zone_resp = requests.get(f'{API_URL}/locations/zones/{zone_id}/', headers=headers)
            if zone_resp.status_code == 200:
                zone_info = zone_resp.json()
                
                # Position near zone center with small offset
                location = {
                    'asset': asset['id'],
                    'asset_id': asset['asset_id'],
                    'latitude': round(float(zone_info['center_lat']) + random.uniform(-0.01, 0.01), 6),
                    'longitude': round(float(zone_info['center_lng']) + random.uniform(-0.01, 0.01), 6),
                    'speed': random.uniform(0, 50) if asset['status'] == 'active' else 0,
                    'heading': random.randint(0, 359),
                    'accuracy': 10,
                    'source': 'gps_device',
                    'timestamp': datetime.now().isoformat()
                }
                
                loc_resp = requests.post(f'{API_URL}/locations/updates/', json=location, headers=headers)
                if loc_resp.status_code in [200, 201]:
                    print(f"[OK] {asset['asset_id']} -> {zone_info['name']}")
                else:
                    print(f"[FAIL] {asset['asset_id']}: {loc_resp.status_code}")

print("\n" + "="*60)
print("WESTERN NY FLEET SETUP COMPLETE")
print("="*60)

# Summary
resp = requests.get(f'{API_URL}/locations/current/map_data/', headers=headers)
if resp.status_code == 200:
    map_data = resp.json()
    print(f"\nMap Summary:")
    print(f"  Active zones: {len(map_data.get('zones', []))}")
    print(f"  Vehicles positioned: {len(map_data.get('assets', []))}")
    
    # Coverage calculation - Western NY is roughly 150km x 100km
    zone_coverage = len(zone_ids) * 25  # Each zone covers ~25 sq km
    total_area = 150 * 100  # Total WNY area in sq km
    coverage_pct = min(100, (zone_coverage / total_area) * 100)
    print(f"  Regional coverage: ~{coverage_pct:.0f}%")

print("\n[SUCCESS] Fleet is now operating in Western New York!")
print("  Primary hubs: Buffalo, Rochester, Niagara Falls")
print("  Service areas: Amherst, Cheektowaga, Henrietta, Batavia")
print("\nView at: http://localhost:3000/locations")