#!/usr/bin/env python
"""
Image Delete Functionality Test
Tests both Asset and Driver photo deletion
"""

import os
import sys
import requests
from PIL import Image
import io
import json
import time
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:8000'
API_URL = f'{BASE_URL}/api'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}[ERROR] {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}[INFO] {text}{Colors.END}")

def print_test(test_name):
    """Print test name"""
    print(f"\n{Colors.YELLOW}Testing: {test_name}{Colors.END}")

def create_test_image(color='blue', size=(800, 600)):
    """Create a test image with specified color and size"""
    img = Image.new('RGB', size, color=color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def authenticate():
    """Authenticate and get token"""
    print_test("Authentication")
    
    login_url = f'{API_URL}/auth/login/'
    login_data = {'username': ADMIN_USERNAME, 'password': ADMIN_PASSWORD}
    
    response = requests.post(login_url, json=login_data)
    
    if response.status_code == 200:
        token = response.json().get('token')
        if token:
            print_success(f"Authenticated successfully. Token: {token[:20]}...")
            return token
        else:
            print_error("No token in response")
            return None
    else:
        print_error(f"Authentication failed: {response.status_code}")
        print_error(response.text)
        return None

def test_asset_image_delete(token):
    """Test asset image deletion functionality"""
    print_header("ASSET IMAGE DELETE TESTS")
    
    headers = {'Authorization': f'Token {token}'}
    
    # First, upload an image to an asset
    print_test("Setting up test data - Upload image to asset")
    assets_response = requests.get(f'{API_URL}/assets/', headers=headers)
    
    if assets_response.status_code != 200:
        print_error(f"Failed to fetch assets: {assets_response.status_code}")
        return False
    
    assets = assets_response.json().get('results', [])
    if not assets:
        print_error("No assets found in the system")
        return False
    
    asset = assets[0]
    asset_id = asset['id']
    asset_name = asset.get('asset_id', 'Unknown')
    print_success(f"Using asset: {asset_name} (ID: {asset_id})")
    
    # Upload test image
    img_bytes = create_test_image('red', (400, 300))
    files = {'image': ('test_delete.png', img_bytes, 'image/png')}
    
    upload_response = requests.post(
        f'{API_URL}/assets/{asset_id}/upload_image/',
        files=files,
        headers=headers
    )
    
    if upload_response.status_code != 200:
        print_error(f"Failed to upload test image: {upload_response.status_code}")
        return False
    
    print_success("Test image uploaded successfully")
    
    # Verify image exists
    print_test("Verify image exists before deletion")
    asset_response = requests.get(f'{API_URL}/assets/{asset_id}/', headers=headers)
    if asset_response.status_code == 200:
        asset_data = asset_response.json()
        if asset_data.get('image'):
            print_success(f"Image confirmed: {asset_data['image']}")
        else:
            print_error("No image found after upload")
            return False
    
    # Test 1: Valid image deletion
    print_test("Delete asset image")
    delete_response = requests.delete(
        f'{API_URL}/assets/{asset_id}/delete_image/',
        headers=headers
    )
    
    if delete_response.status_code == 200:
        result = delete_response.json()
        print_success(f"Image deleted successfully: {result.get('message')}")
    else:
        print_error(f"Delete failed: {delete_response.status_code}")
        print_error(delete_response.text)
        return False
    
    # Verify image was deleted
    print_test("Verify image was deleted")
    asset_response = requests.get(f'{API_URL}/assets/{asset_id}/', headers=headers)
    if asset_response.status_code == 200:
        asset_data = asset_response.json()
        if not asset_data.get('image') and not asset_data.get('thumbnail'):
            print_success("Image and thumbnail successfully removed from database")
        else:
            print_error(f"Image still exists: {asset_data.get('image')}")
            return False
    
    # Test 2: Try to delete non-existent image
    print_test("Attempt to delete non-existent image")
    delete_response = requests.delete(
        f'{API_URL}/assets/{asset_id}/delete_image/',
        headers=headers
    )
    
    if delete_response.status_code == 400:
        print_success("Correctly rejected deletion of non-existent image")
    else:
        print_error(f"Expected 400 error, got {delete_response.status_code}")
        return False
    
    return True

def test_driver_photo_delete(token):
    """Test driver photo deletion functionality"""
    print_header("DRIVER PHOTO DELETE TESTS")
    
    headers = {'Authorization': f'Token {token}'}
    
    # First, upload a photo to a driver
    print_test("Setting up test data - Upload photo to driver")
    drivers_response = requests.get(f'{API_URL}/drivers/drivers/', headers=headers)
    
    if drivers_response.status_code != 200:
        print_error(f"Failed to fetch drivers: {drivers_response.status_code}")
        return False
    
    drivers = drivers_response.json().get('results', [])
    if not drivers:
        print_error("No drivers found in the system")
        return False
    
    driver = drivers[0]
    driver_id = driver['id']
    driver_name = driver.get('full_name', 'Unknown')
    print_success(f"Using driver: {driver_name} (ID: {driver_id})")
    
    # Upload test photo
    img_bytes = create_test_image('green', (300, 300))
    files = {'photo': ('test_delete_photo.png', img_bytes, 'image/png')}
    
    upload_response = requests.post(
        f'{API_URL}/drivers/drivers/{driver_id}/upload_photo/',
        files=files,
        headers=headers
    )
    
    if upload_response.status_code != 200:
        print_error(f"Failed to upload test photo: {upload_response.status_code}")
        return False
    
    print_success("Test photo uploaded successfully")
    
    # Verify photo exists
    print_test("Verify photo exists before deletion")
    driver_response = requests.get(f'{API_URL}/drivers/drivers/{driver_id}/', headers=headers)
    if driver_response.status_code == 200:
        driver_data = driver_response.json()
        if driver_data.get('profile_photo'):
            print_success(f"Photo confirmed: {driver_data['profile_photo']}")
        else:
            print_error("No photo found after upload")
            return False
    
    # Test 1: Valid photo deletion
    print_test("Delete driver photo")
    delete_response = requests.delete(
        f'{API_URL}/drivers/drivers/{driver_id}/delete_photo/',
        headers=headers
    )
    
    if delete_response.status_code == 200:
        result = delete_response.json()
        print_success(f"Photo deleted successfully: {result.get('message')}")
    else:
        print_error(f"Delete failed: {delete_response.status_code}")
        print_error(delete_response.text)
        return False
    
    # Verify photo was deleted
    print_test("Verify photo was deleted")
    driver_response = requests.get(f'{API_URL}/drivers/drivers/{driver_id}/', headers=headers)
    if driver_response.status_code == 200:
        driver_data = driver_response.json()
        if not driver_data.get('profile_photo'):
            print_success("Photo successfully removed from database")
        else:
            print_error(f"Photo still exists: {driver_data.get('profile_photo')}")
            return False
    
    # Test 2: Try to delete non-existent photo
    print_test("Attempt to delete non-existent photo")
    delete_response = requests.delete(
        f'{API_URL}/drivers/drivers/{driver_id}/delete_photo/',
        headers=headers
    )
    
    if delete_response.status_code == 400:
        print_success("Correctly rejected deletion of non-existent photo")
    else:
        print_error(f"Expected 400 error, got {delete_response.status_code}")
        return False
    
    return True

def main():
    """Main test execution"""
    print_header("IMAGE DELETE FUNCTIONALITY TEST SUITE")
    print_info(f"Testing against: {BASE_URL}")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Authenticate
    token = authenticate()
    if not token:
        print_error("Authentication failed. Cannot proceed with tests.")
        return 1
    
    # Run tests
    test_results = []
    
    # Asset image delete tests
    asset_result = test_asset_image_delete(token)
    test_results.append(('Asset Image Delete', asset_result))
    
    # Driver photo delete tests
    driver_result = test_driver_photo_delete(token)
    test_results.append(('Driver Photo Delete', driver_result))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = f"{Colors.GREEN}PASSED{Colors.END}" if result else f"{Colors.RED}FAILED{Colors.END}"
        print(f"{test_name:.<40} {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print_success("All delete functionality tests passed successfully!")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)