#!/usr/bin/env python
"""
Clean up duplicate zones and show zone management
"""
import requests
import json

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

print("\n" + "="*60)
print("ANALYZING CURRENT ZONES")
print("="*60)

# Get all zones
response = requests.get(f'{API_URL}/locations/zones/', headers=headers)
if response.status_code == 200:
    zones = response.json()
    
    # Handle paginated response
    if isinstance(zones, dict) and 'results' in zones:
        zones = zones['results']
    
    print(f"Total zones found: {len(zones)}")
    
    # Group zones by name to find duplicates
    zone_names = {}
    for zone in zones:
        name = zone.get('name', 'Unknown')
        if name not in zone_names:
            zone_names[name] = []
        zone_names[name].append(zone)
    
    # Show duplicates
    duplicates_found = False
    for name, zone_list in zone_names.items():
        if len(zone_list) > 1:
            duplicates_found = True
            print(f"\nDuplicate zone: {name} ({len(zone_list)} instances)")
            for z in zone_list:
                print(f"  - ID: {z['id']}, Active: {z.get('is_active', True)}, Type: {z.get('zone_type', 'unknown')}")
    
    if not duplicates_found:
        print("No duplicate zones found!")

print("\n" + "="*60)
print("CLEANING UP DUPLICATES")
print("="*60)

# Delete duplicates, keeping only the first of each
deleted_count = 0
kept_zones = []

for name, zone_list in zone_names.items():
    if len(zone_list) > 1:
        # Keep the first one
        kept_zones.append(zone_list[0])
        print(f"Keeping: {name} (ID: {zone_list[0]['id']})")
        
        # Delete the rest
        for zone in zone_list[1:]:
            del_response = requests.delete(
                f"{API_URL}/locations/zones/{zone['id']}/",
                headers=headers
            )
            if del_response.status_code in [204, 200]:
                deleted_count += 1
                print(f"  [DELETED] Duplicate with ID: {zone['id']}")
            else:
                print(f"  [FAIL] Could not delete ID: {zone['id']}")
    else:
        kept_zones.append(zone_list[0])

print(f"\nDeleted {deleted_count} duplicate zones")

print("\n" + "="*60)
print("REMAINING ZONES")
print("="*60)

# Get updated zone list
response = requests.get(f'{API_URL}/locations/zones/', headers=headers)
if response.status_code == 200:
    zones = response.json()
    if isinstance(zones, dict) and 'results' in zones:
        zones = zones['results']
    
    print(f"Total zones after cleanup: {len(zones)}")
    
    # Group by type
    by_type = {}
    for zone in zones:
        zone_type = zone.get('zone_type', 'unknown')
        if zone_type not in by_type:
            by_type[zone_type] = []
        by_type[zone_type].append(zone)
    
    for zone_type, type_zones in by_type.items():
        print(f"\n{zone_type.upper()} ({len(type_zones)} zones):")
        for zone in type_zones:
            active_status = "ACTIVE" if zone.get('is_active', True) else "INACTIVE"
            print(f"  [{active_status}] {zone['name']}")
            lat = float(zone.get('center_lat', 0))
            lng = float(zone.get('center_lng', 0))
            print(f"        Location: ({lat:.4f}, {lng:.4f})")
            print(f"        Radius: {zone.get('radius', 0)}m")

print("\n" + "="*60)
print("ZONE MANAGEMENT INFO")
print("="*60)

print("\nHow 'Active Zones' Work:")
print("  - Each zone has an 'is_active' field (boolean)")
print("  - Active zones are included in coverage calculations")
print("  - Inactive zones are hidden from map display")
print("  - Zones can be toggled active/inactive via API")

print("\nAvailable Zone Types:")
print("  - depot: Major distribution center")
print("  - service_area: Maintenance facility")
print("  - customer_site: Client location")
print("  - restricted: No-go zone")
print("  - maintenance: Service station")
print("  - other: General purpose")

print("\nAPI Endpoints for Zone Management:")
print("  GET    /api/locations/zones/        - List all zones")
print("  POST   /api/locations/zones/        - Create new zone")
print("  GET    /api/locations/zones/{id}/   - Get zone details")
print("  PUT    /api/locations/zones/{id}/   - Update zone")
print("  DELETE /api/locations/zones/{id}/   - Delete zone")
print("  GET    /api/locations/zones/{id}/assets_in_zone/ - Get assets in zone")

print("\n" + "="*60)
print("CLEANUP COMPLETE")
print("="*60)
print("\nZones are now cleaned up and ready for use!")
print("View the clean map at: http://localhost:3000/locations")