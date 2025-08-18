#!/usr/bin/env python
"""
Test Fuel Tracking System
Creates sample fuel transactions to demonstrate the system
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal

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

def get_assets(token):
    """Get list of assets"""
    headers = {'Authorization': f'Token {token}'}
    response = requests.get(f'{API_URL}/assets/', headers=headers)
    
    if response.status_code == 200:
        assets = response.json().get('results', [])
        print(f"OK Found {len(assets)} assets")
        return assets
    else:
        print(f"FAIL Failed to get assets: {response.status_code}")
        return []

def create_fuel_transactions(token, assets):
    """Create sample fuel transactions"""
    headers = {'Authorization': f'Token {token}'}
    
    # Sample fuel data for different vehicle types
    fuel_scenarios = [
        # Bus transactions
        {
            'asset_filter': 'BUS',
            'transactions': [
                {
                    'product_type': 'diesel',
                    'volume': 45.5,
                    'unit': 'gal',
                    'unit_price': 3.45,
                    'odometer': 125000,
                    'vendor': 'Shell Station',
                    'location_label': 'Downtown Depot',
                    'days_ago': 5
                },
                {
                    'product_type': 'diesel',
                    'volume': 42.8,
                    'unit': 'gal',
                    'unit_price': 3.52,
                    'odometer': 125580,
                    'vendor': 'BP Station',
                    'location_label': 'Main St',
                    'days_ago': 2
                }
            ]
        },
        # Truck transactions
        {
            'asset_filter': 'TRUCK',
            'transactions': [
                {
                    'product_type': 'gasoline',
                    'volume': 25.2,
                    'unit': 'gal',
                    'unit_price': 3.15,
                    'odometer': 85000,
                    'vendor': 'Exxon',
                    'location_label': 'Highway Rest Stop',
                    'days_ago': 7
                },
                {
                    'product_type': 'gasoline',
                    'volume': 24.8,
                    'unit': 'gal',
                    'unit_price': 3.22,
                    'odometer': 85450,
                    'vendor': 'Shell Station',
                    'location_label': 'Downtown',
                    'days_ago': 3
                }
            ]
        },
        # Van transactions
        {
            'asset_filter': 'VAN',
            'transactions': [
                {
                    'product_type': 'gasoline',
                    'volume': 18.5,
                    'unit': 'gal',
                    'unit_price': 3.18,
                    'odometer': 46000,
                    'vendor': 'Costco Gas',
                    'location_label': 'Costco Warehouse',
                    'days_ago': 4
                },
                {
                    'product_type': 'gasoline',
                    'volume': 19.2,
                    'unit': 'gal',
                    'unit_price': 3.25,
                    'odometer': 46320,
                    'vendor': 'Shell Station',
                    'location_label': 'Main Branch',
                    'days_ago': 1
                }
            ]
        },
        # Car transactions
        {
            'asset_filter': 'CAR',
            'transactions': [
                {
                    'product_type': 'gasoline',
                    'volume': 12.5,
                    'unit': 'gal',
                    'unit_price': 3.20,
                    'odometer': 35000,
                    'vendor': 'BP Station',
                    'location_label': 'Office District',
                    'days_ago': 6
                },
                {
                    'product_type': 'gasoline',
                    'volume': 11.8,
                    'unit': 'gal',
                    'unit_price': 3.28,
                    'odometer': 35280,
                    'vendor': 'Chevron',
                    'location_label': 'City Center',
                    'days_ago': 2
                }
            ]
        }
    ]
    
    created_count = 0
    
    for scenario in fuel_scenarios:
        # Find matching asset
        matching_assets = [a for a in assets if scenario['asset_filter'] in a.get('asset_id', '')]
        
        if not matching_assets:
            print(f"SKIP No assets found matching {scenario['asset_filter']}")
            continue
            
        asset = matching_assets[0]
        print(f"OK Creating transactions for {asset['asset_id']}")
        
        for txn_data in scenario['transactions']:
            # Calculate timestamp (timezone-aware)
            timestamp = datetime.now(timezone.utc) - timedelta(days=txn_data['days_ago'])
            
            # Prepare transaction payload
            transaction = {
                'asset': asset['id'],
                'timestamp': timestamp.isoformat(),
                'product_type': txn_data['product_type'],
                'volume': txn_data['volume'],
                'unit': txn_data['unit'],
                'unit_price': txn_data['unit_price'],
                'total_cost': round(txn_data['volume'] * txn_data['unit_price'], 2),
                'odometer': txn_data['odometer'],
                'vendor': txn_data['vendor'],
                'location_label': txn_data['location_label'],
                'entry_source': 'manual',
                'notes': f"Test transaction created for {asset['asset_id']}"
            }
            
            # Create transaction
            response = requests.post(
                f'{API_URL}/fuel/transactions/',
                json=transaction,
                headers=headers
            )
            
            if response.status_code == 201:
                created_count += 1
                data = response.json()
                mpg = data.get('mpg', 'N/A')
                cost_per_mile = data.get('cost_per_mile', 'N/A')
                print(f"  OK Created: {txn_data['volume']} gal, ${txn_data['unit_price']:.3f}/gal, MPG: {mpg}, CPM: {cost_per_mile}")
            else:
                print(f"  FAIL Failed: {response.status_code} - {response.text}")
    
    return created_count

def get_fuel_stats(token):
    """Get fuel statistics"""
    headers = {'Authorization': f'Token {token}'}
    response = requests.get(f'{API_URL}/fuel/transactions/stats/', headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print(f"\nFuel Statistics:")
        print(f"  Total Transactions: {stats.get('total_transactions', 0)}")
        total_volume = float(stats.get('total_volume') or 0)
        total_cost = float(stats.get('total_cost') or 0)
        avg_mpg = float(stats.get('average_mpg') or 0)
        avg_cost_per_mile = float(stats.get('average_cost_per_mile') or 0)
        
        print(f"  Total Volume: {total_volume:.1f} gallons")
        print(f"  Total Cost: ${total_cost:.2f}")
        print(f"  Average MPG: {avg_mpg:.1f}")
        print(f"  Average Cost/Mile: ${avg_cost_per_mile:.3f}")
        
        # Product breakdown
        breakdown = stats.get('product_breakdown', {})
        if breakdown:
            print(f"\nFuel Type Breakdown:")
            for product, data in breakdown.items():
                print(f"  {product.title()}: {data['count']} transactions, {data['volume'] or 0:.1f} gal, ${data['cost'] or 0:.2f}")
        
        return stats
    else:
        print(f"FAIL Failed to get stats: {response.status_code}")
        return None

def main():
    """Main test execution"""
    print("Fuel Tracking System Test")
    print("=" * 50)
    
    # Authenticate
    token = authenticate()
    if not token:
        return 1
    
    # Get assets
    assets = get_assets(token)
    if not assets:
        return 1
    
    # Create fuel transactions
    print(f"\nCreating sample fuel transactions...")
    created_count = create_fuel_transactions(token, assets)
    print(f"\nOK Created {created_count} fuel transactions")
    
    # Get statistics
    stats = get_fuel_stats(token)
    
    print(f"\nOK Fuel tracking system test completed successfully!")
    print(f"Visit http://localhost:3000/fuel to view the fuel management interface")
    
    return 0

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"FAIL Unexpected error: {e}")
        sys.exit(1)