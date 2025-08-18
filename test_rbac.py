#!/usr/bin/env python
"""
Test Role-Based Access Control (RBAC) Implementation
"""

import requests
import json
from datetime import datetime, timezone

BASE_URL = 'http://localhost:8000'
API_URL = f'{BASE_URL}/api'

# Test users with different roles
USERS = {
    'admin': {'username': 'admin', 'password': 'admin123'},
    'fleet_manager': {'username': 'fleet_manager', 'password': 'manager123'},
    'technician': {'username': 'technician', 'password': 'tech123'},
    'viewer': {'username': 'viewer', 'password': 'viewer123'}
}


class RBACTester:
    def __init__(self):
        self.tokens = {}
        self.test_data = {}
        
    def authenticate_all_users(self):
        """Authenticate all test users and store tokens"""
        print("=" * 60)
        print("AUTHENTICATING USERS")
        print("=" * 60)
        
        for role, credentials in USERS.items():
            response = requests.post(
                f'{API_URL}/auth/login/',
                json=credentials
            )
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data['token']
                roles = data.get('roles', [])
                print(f"[OK] {role}: Authenticated with roles: {', '.join(roles)}")
            else:
                print(f"[FAIL] {role}: Authentication failed")
                self.tokens[role] = None
    
    def test_asset_permissions(self):
        """Test asset CRUD permissions for each role"""
        print("\n" + "=" * 60)
        print("TESTING ASSET PERMISSIONS")
        print("=" * 60)
        
        # Test data for asset creation
        asset_data = {
            'asset_id': 'TEST-001',
            'vehicle_type': 'car',
            'make': 'Test',
            'model': 'Vehicle',
            'year': 2024,
            'vin': 'TEST123456789',
            'license_plate': 'TEST123',
            'status': 'active'
        }
        
        for role, token in self.tokens.items():
            if not token:
                continue
                
            print(f"\n{role.upper()}:")
            headers = {'Authorization': f'Token {token}'}
            
            # Test READ
            response = requests.get(f'{API_URL}/assets/', headers=headers)
            if response.status_code == 200:
                print(f"  [OK] Can read assets")
            else:
                print(f"  [FAIL] Cannot read assets: {response.status_code}")
            
            # Test CREATE
            response = requests.post(
                f'{API_URL}/assets/',
                json=asset_data,
                headers=headers
            )
            if response.status_code == 201:
                print(f"  [OK] Can create assets")
                asset_id = response.json()['id']
                self.test_data['asset_id'] = asset_id
                
                # Test UPDATE
                update_data = {'status': 'maintenance'}
                response = requests.patch(
                    f'{API_URL}/assets/{asset_id}/',
                    json=update_data,
                    headers=headers
                )
                if response.status_code == 200:
                    print(f"  [OK] Can update assets")
                else:
                    print(f"  [FAIL] Cannot update assets: {response.status_code}")
                
                # Test DELETE
                response = requests.delete(
                    f'{API_URL}/assets/{asset_id}/',
                    headers=headers
                )
                if response.status_code == 204:
                    print(f"  [OK] Can delete assets")
                else:
                    print(f"  [FAIL] Cannot delete assets: {response.status_code}")
            elif response.status_code == 403:
                print(f"  [OK] Cannot create assets (Permission denied)")
            else:
                print(f"  [FAIL] Unexpected response for create: {response.status_code}")
    
    def test_fuel_permissions(self):
        """Test fuel transaction permissions for each role"""
        print("\n" + "=" * 60)
        print("TESTING FUEL TRANSACTION PERMISSIONS")
        print("=" * 60)
        
        # First, get an asset for fuel transactions
        admin_headers = {'Authorization': f'Token {self.tokens["admin"]}'}
        response = requests.get(f'{API_URL}/assets/', headers=admin_headers)
        
        if response.status_code != 200 or not response.json().get('results'):
            print("[FAIL] No assets available for fuel testing")
            return
            
        asset_id = response.json()['results'][0]['id']
        
        # Test data for fuel transaction
        fuel_data = {
            'asset': asset_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'product_type': 'gasoline',
            'volume': 10.0,
            'unit': 'gal',
            'total_cost': 35.00,
            'odometer': 52000,
            'entry_source': 'manual',
            'notes': 'RBAC test transaction'
        }
        
        for role, token in self.tokens.items():
            if not token:
                continue
                
            print(f"\n{role.upper()}:")
            headers = {'Authorization': f'Token {token}'}
            
            # Test READ
            response = requests.get(f'{API_URL}/fuel/transactions/', headers=headers)
            if response.status_code == 200:
                print(f"  [OK] Can read fuel transactions")
            else:
                print(f"  [FAIL] Cannot read fuel transactions: {response.status_code}")
            
            # Test CREATE
            response = requests.post(
                f'{API_URL}/fuel/transactions/',
                json=fuel_data,
                headers=headers
            )
            if response.status_code == 201:
                print(f"  [OK] Can create fuel transactions")
                transaction_id = response.json()['id']
                
                # Test UPDATE (technicians can only update their own)
                update_data = {'notes': 'Updated by ' + role}
                response = requests.patch(
                    f'{API_URL}/fuel/transactions/{transaction_id}/',
                    json=update_data,
                    headers=headers
                )
                if response.status_code == 200:
                    print(f"  [OK] Can update fuel transactions")
                elif response.status_code == 403:
                    print(f"  [OK] Cannot update others' transactions (Permission denied)")
                else:
                    print(f"  [FAIL] Unexpected update response: {response.status_code}")
                
                # Test DELETE
                response = requests.delete(
                    f'{API_URL}/fuel/transactions/{transaction_id}/',
                    headers=headers
                )
                if response.status_code == 204:
                    print(f"  [OK] Can delete fuel transactions")
                elif response.status_code == 403:
                    print(f"  [OK] Cannot delete transactions (Permission denied)")
                else:
                    print(f"  [FAIL] Unexpected delete response: {response.status_code}")
                    
            elif response.status_code == 403:
                print(f"  [OK] Cannot create fuel transactions (Permission denied)")
            else:
                print(f"  [FAIL] Unexpected response for create: {response.status_code}")
    
    def test_driver_permissions(self):
        """Test driver management permissions for each role"""
        print("\n" + "=" * 60)
        print("TESTING DRIVER PERMISSIONS")
        print("=" * 60)
        
        # Test data for driver creation
        driver_data = {
            'driver_id': 'TEST-DRV-001',
            'first_name': 'Test',
            'last_name': 'Driver',
            'employee_id': 'TEST-EMP-001',
            'email': 'test.driver@fleet.com',
            'phone': '+15555551234',
            'date_of_birth': '1990-01-01',
            'hire_date': '2020-01-01',
            'license_number': 'TEST123',
            'license_state': 'CA',
            'license_type': 'regular',
            'license_expiration': '2025-12-31',
            'status': 'active',
            'address_line1': '123 Test St',
            'city': 'Test City',
            'state': 'CA',
            'zip_code': '12345',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '+15555555678',
            'emergency_contact_relationship': 'Spouse'
        }
        
        for role, token in self.tokens.items():
            if not token:
                continue
                
            print(f"\n{role.upper()}:")
            headers = {'Authorization': f'Token {token}'}
            
            # Test READ
            response = requests.get(f'{API_URL}/drivers/drivers/', headers=headers)
            if response.status_code == 200:
                print(f"  [OK] Can read drivers")
            else:
                print(f"  [FAIL] Cannot read drivers: {response.status_code}")
            
            # Test CREATE
            response = requests.post(
                f'{API_URL}/drivers/drivers/',
                json=driver_data,
                headers=headers
            )
            if response.status_code == 201:
                print(f"  [OK] Can create drivers")
                driver_id = response.json()['id']
                
                # Test UPDATE
                update_data = {'position': 'Senior Driver'}
                response = requests.patch(
                    f'{API_URL}/drivers/drivers/{driver_id}/',
                    json=update_data,
                    headers=headers
                )
                if response.status_code == 200:
                    print(f"  [OK] Can update drivers")
                else:
                    print(f"  [FAIL] Cannot update drivers: {response.status_code}")
                
                # Test DELETE
                response = requests.delete(
                    f'{API_URL}/drivers/drivers/{driver_id}/',
                    headers=headers
                )
                if response.status_code == 204:
                    print(f"  [OK] Can delete drivers")
                else:
                    print(f"  [FAIL] Cannot delete drivers: {response.status_code}")
                    
            elif response.status_code == 403:
                print(f"  [OK] Cannot create drivers (Permission denied)")
            else:
                print(f"  [FAIL] Unexpected response for create: {response.status_code}")
    
    def run_tests(self):
        """Run all RBAC tests"""
        print("ROLE-BASED ACCESS CONTROL TEST SUITE")
        print("=" * 60)
        
        # Authenticate all users
        self.authenticate_all_users()
        
        # Test permissions for each resource
        self.test_asset_permissions()
        self.test_fuel_permissions()
        self.test_driver_permissions()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print("\nExpected Permissions Matrix:")
        print("----------------------------------------")
        print("Resource    | Admin | Manager | Tech | Viewer")
        print("------------|-------|---------|------|-------")
        print("Assets R    |  Yes  |   Yes   | Yes  |  Yes")
        print("Assets CUD  |  Yes  |   Yes   | No   |  No")
        print("Fuel R      |  Yes  |   Yes   | Yes  |  Yes")
        print("Fuel C      |  Yes  |   Yes   | Yes  |  No")
        print("Fuel UD     |  Yes  |   Yes   | Own  |  No")
        print("Drivers R   |  Yes  |   Yes   | Yes  |  Yes")
        print("Drivers CUD |  Yes  |   Yes   | No   |  No")
        print("----------------------------------------")
        print("\nR=Read, C=Create, U=Update, D=Delete")
        print("Own = Can only modify their own entries")


if __name__ == '__main__':
    tester = RBACTester()
    tester.run_tests()