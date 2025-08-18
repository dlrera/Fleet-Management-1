#!/usr/bin/env python
"""
Test Driver Update Functionality
Quick test to debug the driver update issue
"""

import os
import sys
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:8000'
API_URL = f'{BASE_URL}/api'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

def authenticate():
    """Authenticate and get token"""
    login_url = f'{API_URL}/auth/login/'
    login_data = {'username': ADMIN_USERNAME, 'password': ADMIN_PASSWORD}
    
    response = requests.post(login_url, json=login_data)
    
    if response.status_code == 200:
        token = response.json().get('token')
        print("OK Authenticated successfully")
        return token
    else:
        print(f"FAIL Authentication failed: {response.status_code}")
        return None

def test_driver_update(token):
    """Test driver update functionality"""
    headers = {'Authorization': f'Token {token}'}
    
    # Get first driver
    drivers_response = requests.get(f'{API_URL}/drivers/drivers/', headers=headers)
    
    if drivers_response.status_code != 200:
        print(f"FAIL Failed to fetch drivers: {drivers_response.status_code}")
        return False
    
    drivers = drivers_response.json().get('results', [])
    if not drivers:
        print("FAIL No drivers found")
        return False
    
    driver = drivers[0]
    driver_id = driver['id']
    print(f"OK Testing with driver: {driver.get('full_name', 'Unknown')} (ID: {driver_id})")
    
    # Get full driver details
    driver_response = requests.get(f'{API_URL}/drivers/drivers/{driver_id}/', headers=headers)
    if driver_response.status_code != 200:
        print(f"FAIL Failed to fetch driver details: {driver_response.status_code}")
        return False
    
    full_driver = driver_response.json()
    print("OK Fetched driver details")
    
    # Create update data (exclude profile_photo and other read-only fields)
    update_data = {
        'first_name': full_driver['first_name'],
        'last_name': full_driver['last_name'], 
        'email': full_driver['email'],
        'phone': full_driver['phone'],
        'date_of_birth': full_driver['date_of_birth'],
        'hire_date': full_driver['hire_date'],
        'employment_status': full_driver['employment_status'],
        'department': full_driver.get('department', ''),
        'position': full_driver.get('position', ''),
        'employee_number': full_driver.get('employee_number', ''),
        'license_number': full_driver['license_number'],
        'license_type': full_driver['license_type'],
        'license_expiration': full_driver['license_expiration'],
        'license_state': full_driver['license_state'],
        'address_line1': full_driver['address_line1'],
        'address_line2': full_driver.get('address_line2', ''),
        'city': full_driver['city'],
        'state': full_driver['state'],
        'zip_code': full_driver['zip_code'],
        'emergency_contact_name': full_driver['emergency_contact_name'],
        'emergency_contact_phone': full_driver['emergency_contact_phone'],
        'emergency_contact_relationship': full_driver['emergency_contact_relationship'],
        'notes': full_driver.get('notes', '')
    }
    
    # Make a small change
    update_data['notes'] = f"Updated at {datetime.now().isoformat()}"
    
    print("OK Prepared update data")
    print(f"Update payload: {json.dumps(update_data, indent=2)}")
    
    # Attempt update
    update_response = requests.put(
        f'{API_URL}/drivers/drivers/{driver_id}/',
        json=update_data,
        headers=headers
    )
    
    print(f"Update response status: {update_response.status_code}")
    print(f"Update response: {update_response.text}")
    
    if update_response.status_code == 200:
        print("OK Driver updated successfully!")
        return True
    else:
        print(f"FAIL Update failed: {update_response.status_code}")
        try:
            error_data = update_response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Raw error: {update_response.text}")
        return False

def main():
    print("Driver Update Test")
    print("=" * 50)
    
    token = authenticate()
    if not token:
        return 1
    
    success = test_driver_update(token)
    
    if success:
        print("\nOK All tests passed!")
        return 0
    else:
        print("\nFAIL Tests failed!")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"FAIL Unexpected error: {e}")
        sys.exit(1)