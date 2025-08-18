#!/usr/bin/env python
"""
Create test drivers for fuel tracking tests
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:8000'
API_URL = f'{BASE_URL}/api'

def authenticate():
    """Authenticate and get token"""
    login_url = f'{API_URL}/auth/login/'
    login_data = {'username': 'admin', 'password': 'admin123'}
    
    response = requests.post(login_url, json=login_data)
    
    if response.status_code == 200:
        token = response.json().get('token')
        print("[OK] Authenticated successfully")
        return token
    else:
        print(f"[FAIL] Authentication failed: {response.status_code}")
        return None

def create_drivers(token):
    """Create test drivers"""
    headers = {'Authorization': f'Token {token}'}
    
    drivers = [
        {
            'driver_id': 'DRV001',
            'first_name': 'John',
            'last_name': 'Smith',
            'employee_id': 'EMP001',
            'email': 'john.smith@fleet.com',
            'phone': '+15555550101',
            'date_of_birth': '1985-05-15',
            'hire_date': '2020-01-15',
            'license_number': 'JS123456',
            'license_state': 'CA',
            'license_type': 'class_a',
            'license_expiration': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'license_class': 'CDL-A',
            'status': 'active',
            'address_line1': '123 Main St',
            'city': 'San Francisco',
            'state': 'CA',
            'zip_code': '94102',
            'emergency_contact_name': 'Mary Smith',
            'emergency_contact_phone': '+15555550201',
            'emergency_contact_relationship': 'Spouse'
        },
        {
            'driver_id': 'DRV002',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'employee_id': 'EMP002',
            'email': 'jane.doe@fleet.com',
            'phone': '+15555550102',
            'date_of_birth': '1990-08-22',
            'hire_date': '2021-03-10',
            'license_number': 'JD789012',
            'license_state': 'CA',
            'license_type': 'class_b',
            'license_expiration': (datetime.now() + timedelta(days=400)).strftime('%Y-%m-%d'),
            'license_class': 'CDL-B',
            'status': 'active',
            'address_line1': '456 Oak Ave',
            'city': 'Oakland',
            'state': 'CA',
            'zip_code': '94612',
            'emergency_contact_name': 'Bob Doe',
            'emergency_contact_phone': '+15555550202',
            'emergency_contact_relationship': 'Father'
        },
        {
            'driver_id': 'DRV003',
            'first_name': 'Mike',
            'last_name': 'Johnson',
            'employee_id': 'EMP003',
            'email': 'mike.johnson@fleet.com',
            'phone': '+15555550103',
            'date_of_birth': '1988-12-03',
            'hire_date': '2019-06-20',
            'license_number': 'MJ345678',
            'license_state': 'CA',
            'license_type': 'regular',
            'license_expiration': (datetime.now() + timedelta(days=300)).strftime('%Y-%m-%d'),
            'license_class': 'Regular',
            'status': 'active',
            'address_line1': '789 Pine St',
            'city': 'San Jose',
            'state': 'CA',
            'zip_code': '95112',
            'emergency_contact_name': 'Lisa Johnson',
            'emergency_contact_phone': '+15555550203',
            'emergency_contact_relationship': 'Sister'
        }
    ]
    
    created_count = 0
    for driver_data in drivers:
        response = requests.post(
            f'{API_URL}/drivers/drivers/',
            json=driver_data,
            headers=headers
        )
        
        if response.status_code == 201:
            created_count += 1
            print(f"[OK] Created driver: {driver_data['first_name']} {driver_data['last_name']}")
        else:
            print(f"[FAIL] Failed to create driver {driver_data['employee_id']}: {response.status_code}")
            if response.text:
                print(f"      Error: {response.text}")
    
    return created_count

def main():
    print("Creating test drivers for fuel tracking tests...")
    print("=" * 50)
    
    token = authenticate()
    if not token:
        return 1
    
    created = create_drivers(token)
    print(f"\n[OK] Created {created} test drivers")
    
    return 0

if __name__ == '__main__':
    exit(main())