#!/usr/bin/env python
"""
Check zone discrepancy between map and zone management
"""
import requests
from collections import Counter

BASE_URL = 'http://localhost:8000'
API_URL = f'{BASE_URL}/api'

# Login
print("Authenticating...")
response = requests.post(f'{API_URL}/auth/login/', json={'username': 'admin', 'password': 'admin123'})
token = response.json()['token']
headers = {'Authorization': f'Token {token}'}

# Get zones from zone management endpoint
zones_resp = requests.get(f'{API_URL}/locations/zones/?page_size=100', headers=headers)
zones_data = zones_resp.json()
all_zones = zones_data.get('results', zones_data)
print(f"\nZone Management endpoint: {len(all_zones)} zones")

# Get zones from map data endpoint  
map_resp = requests.get(f'{API_URL}/locations/current/map_data/?within_hours=24', headers=headers)
map_data = map_resp.json()
map_zones = map_data.get('zones', [])
print(f"Map Data endpoint: {len(map_zones)} zones")

# Check for duplicates in map
map_zone_names = [z['name'] for z in map_zones]
map_counts = Counter(map_zone_names)
duplicates = [name for name, count in map_counts.items() if count > 1]

if duplicates:
    print(f"\nDuplicate zones in map data:")
    for name in duplicates:
        print(f"  '{name}': appears {map_counts[name]} times")

# Compare zone lists
zone_mgmt_names = set([z['name'] for z in all_zones])
map_zone_names_set = set(map_zone_names)

print(f"\nZones in Zone Management but not in Map: {zone_mgmt_names - map_zone_names_set}")
print(f"Zones in Map but not in Zone Management: {map_zone_names_set - zone_mgmt_names}")

# Check the map data query
print("\nLet me check the map_data view implementation to see why it returns more zones...")

# Direct database check
import sys
sys.path.append('backend')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()

from locations.models import LocationZone

db_zones = LocationZone.objects.all()
print(f"\nDatabase has {db_zones.count()} total zones")
print(f"Active zones: {db_zones.filter(is_active=True).count()}")

# Check for actual duplicates in DB
zone_names_db = list(db_zones.values_list('name', flat=True))
db_counts = Counter(zone_names_db)
db_duplicates = [name for name, count in db_counts.items() if count > 1]

if db_duplicates:
    print(f"\nDuplicate zone names in database:")
    for name in db_duplicates:
        zones_with_name = db_zones.filter(name=name)
        print(f"  '{name}': {zones_with_name.count()} zones")
        for zone in zones_with_name:
            print(f"    - ID: {zone.id}, Active: {zone.is_active}, Type: {zone.zone_type}")