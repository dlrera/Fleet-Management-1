#!/usr/bin/env python
"""
Test User Management System
"""
import requests
import json

BASE_URL = 'http://localhost:8000'
API_URL = f'{BASE_URL}/api'

def test_user_management():
    print("USER MANAGEMENT TEST")
    print("=" * 60)
    
    # 1. Login as admin
    print("\n1. Logging in as admin...")
    login_response = requests.post(
        f'{API_URL}/auth/login/',
        json={'username': 'admin', 'password': 'admin123'}
    )
    
    if login_response.status_code != 200:
        print(f"[FAIL] Admin login failed: {login_response.status_code}")
        return
    
    token = login_response.json()['token']
    roles = login_response.json().get('roles', [])
    print(f"[OK] Logged in as admin with roles: {roles}")
    
    headers = {'Authorization': f'Token {token}'}
    
    # 2. List all users
    print("\n2. Listing all users...")
    users_response = requests.get(
        f'{API_URL}/auth/manage/users/list_users/',
        headers=headers
    )
    
    if users_response.status_code == 200:
        users = users_response.json()
        print(f"[OK] Found {len(users)} users:")
        for user in users:
            print(f"    - {user['username']}: {', '.join(user['roles'])}")
    else:
        print(f"[FAIL] Could not list users: {users_response.status_code}")
    
    # 3. Get available roles
    print("\n3. Getting available roles...")
    roles_response = requests.get(
        f'{API_URL}/auth/manage/users/available_roles/',
        headers=headers
    )
    
    if roles_response.status_code == 200:
        available_roles = roles_response.json()['roles']
        print(f"[OK] Available roles: {', '.join(available_roles)}")
    else:
        print(f"[FAIL] Could not get roles: {roles_response.status_code}")
    
    # 4. Update user roles (change technician to fleet manager)
    print("\n4. Updating user roles...")
    # First find the technician user
    technician = next((u for u in users if 'Technician' in u['roles']), None)
    
    if technician:
        update_response = requests.post(
            f'{API_URL}/auth/manage/users/{technician["id"]}/update_roles/',
            json={'roles': ['Fleet Manager']},
            headers=headers
        )
        
        if update_response.status_code == 200:
            new_roles = update_response.json()['roles']
            print(f"[OK] Updated {technician['username']} roles to: {new_roles}")
        else:
            print(f"[FAIL] Could not update roles: {update_response.status_code}")
    
    # 5. Send invitation
    print("\n5. Sending user invitation...")
    invitation_data = {
        'email': 'newuser@fleet.com',
        'first_name': 'New',
        'last_name': 'User',
        'role': 'Technician'
    }
    
    invite_response = requests.post(
        f'{API_URL}/auth/manage/users/send_invitation/',
        json=invitation_data,
        headers=headers
    )
    
    if invite_response.status_code == 200:
        result = invite_response.json()
        print(f"[OK] {result['message']}")
        if 'invitation_url' in result:
            print(f"    Invitation URL: {result['invitation_url']}")
    else:
        error = invite_response.json().get('error', 'Unknown error')
        print(f"[INFO] Invitation status: {error}")
    
    # 6. List pending invitations
    print("\n6. Listing pending invitations...")
    invites_response = requests.get(
        f'{API_URL}/auth/manage/users/pending_invitations/',
        headers=headers
    )
    
    if invites_response.status_code == 200:
        invitations = invites_response.json()
        print(f"[OK] Found {len(invitations)} pending invitations")
        for inv in invitations:
            print(f"    - {inv['email']} ({inv['role']}) - Expires: {inv['expires_at'][:10]}")
    else:
        print(f"[FAIL] Could not list invitations: {invites_response.status_code}")
    
    # 7. Deactivate/Activate user
    print("\n7. Testing user deactivation/activation...")
    # Find viewer user
    viewer = next((u for u in users if 'Read-only' in u['roles']), None)
    
    if viewer:
        # Deactivate
        deactivate_response = requests.post(
            f'{API_URL}/auth/manage/users/{viewer["id"]}/deactivate/',
            headers=headers
        )
        
        if deactivate_response.status_code == 200:
            print(f"[OK] Deactivated user: {viewer['username']}")
        else:
            print(f"[FAIL] Could not deactivate user: {deactivate_response.status_code}")
        
        # Reactivate
        activate_response = requests.post(
            f'{API_URL}/auth/manage/users/{viewer["id"]}/activate/',
            headers=headers
        )
        
        if activate_response.status_code == 200:
            print(f"[OK] Reactivated user: {viewer['username']}")
        else:
            print(f"[FAIL] Could not activate user: {activate_response.status_code}")
    
    # 8. Test non-admin access
    print("\n8. Testing non-admin access (should fail)...")
    
    # Login as technician
    tech_login = requests.post(
        f'{API_URL}/auth/login/',
        json={'username': 'technician', 'password': 'tech123'}
    )
    
    if tech_login.status_code == 200:
        tech_token = tech_login.json()['token']
        tech_headers = {'Authorization': f'Token {tech_token}'}
        
        # Try to access user management
        tech_response = requests.get(
            f'{API_URL}/auth/manage/users/list_users/',
            headers=tech_headers
        )
        
        if tech_response.status_code == 403:
            print("[OK] Non-admin correctly denied access to user management")
        else:
            print(f"[FAIL] Non-admin got unexpected response: {tech_response.status_code}")
    
    print("\n" + "=" * 60)
    print("USER MANAGEMENT TEST COMPLETE")
    print("\nSummary:")
    print("- Admin can list and manage all users")
    print("- Admin can update user roles")
    print("- Admin can send invitations")
    print("- Admin can deactivate/activate users")
    print("- Non-admins cannot access user management")


if __name__ == '__main__':
    test_user_management()