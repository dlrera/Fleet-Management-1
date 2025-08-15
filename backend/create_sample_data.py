import os
import django
from decimal import Decimal
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assets.models import Asset, AssetDocument

def create_sample_assets():
    """Create sample assets for testing"""
    
    # Clear existing assets (for testing)
    Asset.objects.all().delete()
    
    # Sample assets data
    sample_assets = [
        {
            'asset_id': 'TRUCK-001',
            'vehicle_type': 'truck',
            'make': 'Ford',
            'model': 'F-150',
            'year': 2022,
            'vin': '1FTFW1ET5DFC10312',
            'license_plate': 'FL-001',
            'department': 'Operations',
            'purchase_date': date(2022, 1, 15),
            'purchase_cost': Decimal('35000.00'),
            'current_odometer': 15000,
            'status': 'active',
            'notes': 'Primary fleet vehicle for operations'
        },
        {
            'asset_id': 'BUS-001',
            'vehicle_type': 'bus',
            'make': 'Mercedes',
            'model': 'Sprinter',
            'year': 2021,
            'vin': '2GTBV8DX3G1234567',
            'license_plate': 'FL-002',
            'department': 'Transportation',
            'purchase_date': date(2021, 8, 10),
            'purchase_cost': Decimal('45000.00'),
            'current_odometer': 25000,
            'status': 'active',
            'notes': 'Employee transportation vehicle'
        },
        {
            'asset_id': 'VAN-001',
            'vehicle_type': 'van',
            'make': 'Ford',
            'model': 'Transit',
            'year': 2023,
            'vin': '2FTBW2CM5HCA12345',
            'license_plate': 'FL-003',
            'department': 'Delivery',
            'purchase_date': date(2023, 5, 15),
            'purchase_cost': Decimal('32000.00'),
            'current_odometer': 1200,
            'status': 'active',
            'notes': 'New delivery van for logistics'
        },
        {
            'asset_id': 'CAR-001',
            'vehicle_type': 'car',
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2020,
            'vin': '4T1BF1FK5CU123456',
            'license_plate': 'FL-004',
            'department': 'Administration',
            'purchase_date': date(2020, 3, 20),
            'purchase_cost': Decimal('28000.00'),
            'current_odometer': 45000,
            'status': 'maintenance',
            'notes': 'Administrative vehicle currently in maintenance'
        },
        {
            'asset_id': 'TRACTOR-001',
            'vehicle_type': 'tractor',
            'make': 'John Deere',
            'model': '5075E',
            'year': 2019,
            'license_plate': 'FL-005',
            'department': 'Maintenance',
            'purchase_date': date(2019, 6, 30),
            'purchase_cost': Decimal('65000.00'),
            'current_odometer': 1200,  # Hours for equipment
            'status': 'active',
            'notes': 'Grounds maintenance tractor'
        },
        {
            'asset_id': 'EQUIP-001',
            'vehicle_type': 'equipment',
            'make': 'Caterpillar',
            'model': 'Mini Excavator',
            'year': 2018,
            'department': 'Construction',
            'purchase_date': date(2018, 9, 15),
            'purchase_cost': Decimal('85000.00'),
            'current_odometer': 2500,  # Hours
            'status': 'retired',
            'notes': 'Retired construction equipment'
        }
    ]
    
    created_assets = []
    for asset_data in sample_assets:
        asset = Asset.objects.create(**asset_data)
        created_assets.append(asset)
        print(f"Created asset: {asset.asset_id} - {asset.year} {asset.make} {asset.model}")
    
    print(f"\nCreated {len(created_assets)} sample assets")
    return created_assets

def print_api_info():
    """Print API endpoint information"""
    print("\n" + "="*60)
    print("FLEET MANAGEMENT API ENDPOINTS")
    print("="*60)
    print("\nASSET MANAGEMENT:")
    print("  GET    /api/assets/                 - List all assets")
    print("  POST   /api/assets/                 - Create new asset")
    print("  GET    /api/assets/{id}/            - Get asset details")
    print("  PUT    /api/assets/{id}/            - Update asset")
    print("  PATCH  /api/assets/{id}/            - Partial update")
    print("  DELETE /api/assets/{id}/            - Delete asset")
    
    print("\nSEARCH & FILTERING:")
    print("  GET    /api/assets/?search=term     - Search assets")
    print("  GET    /api/assets/?vehicle_type=truck - Filter by type")
    print("  GET    /api/assets/?status=active   - Filter by status")
    print("  GET    /api/assets/?department=ops  - Filter by department")
    print("  GET    /api/assets/?year=2022       - Filter by year")
    print("  GET    /api/assets/?ordering=make   - Order results")
    
    print("\nDOCUMENTS:")
    print("  GET    /api/assets/{id}/documents/  - Get asset documents")
    print("  POST   /api/assets/{id}/upload_document/ - Upload document")
    print("  GET    /api/documents/              - List all documents")
    print("  GET    /api/documents/{id}/         - Get document details")
    
    print("\nSTATISTICS:")
    print("  GET    /api/assets/stats/           - Get asset statistics")
    
    print("\nAUTHENTICATION:")
    print("  POST   /api/auth/login/             - Login")
    print("  POST   /api/auth/logout/            - Logout")
    print("  GET    /api/auth/user/              - Get current user")
    
    print("\nEXAMPLE REQUESTS:")
    print("  curl -H 'Authorization: Token YOUR_TOKEN' http://localhost:8000/api/assets/")
    print("  curl -H 'Authorization: Token YOUR_TOKEN' http://localhost:8000/api/assets/stats/")

if __name__ == "__main__":
    print("Creating sample data for Fleet Management System...")
    assets = create_sample_assets()
    print_api_info()
    print("\nSample data created successfully!")
    print("Start the development server with: python manage.py runserver")
    print("Visit http://localhost:8000/admin to view assets in Django admin")
    print("Login credentials: admin / admin123")