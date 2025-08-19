#!/usr/bin/env python
"""
Manual test for audit logging
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
django.setup()

from authentication.models import AuditLog
from django.contrib.auth.models import User
from django.utils import timezone

# Check current count
print(f"Initial audit log count: {AuditLog.objects.count()}")

# Try to create a manual audit log
try:
    admin_user = User.objects.get(username='admin')
    
    audit_log = AuditLog.objects.create(
        actor=admin_user,
        actor_email=admin_user.email or 'admin@fleet.local',
        actor_role='Admin',
        action='create',
        resource_type='test',
        resource_id='manual-test-1',
        resource_name='Manual Test Entry',
        ip_address='127.0.0.1',
        risk_score=10
    )
    
    print(f"Created audit log: {audit_log}")
    print(f"New audit log count: {AuditLog.objects.count()}")
    
    # Test immutability
    try:
        audit_log.risk_score = 20
        audit_log.save()
        print("ERROR: Audit log was modified (should not happen)")
    except ValueError as e:
        print(f"Good: Audit log is immutable - {e}")
        
except Exception as e:
    print(f"Error creating audit log: {e}")
    import traceback
    traceback.print_exc()

# Check if middleware is creating logs
print("\nChecking recent audit logs:")
recent_logs = AuditLog.objects.all().order_by('-timestamp')[:5]
for log in recent_logs:
    print(f"  - {log.timestamp}: {log.actor_email} - {log.action} - {log.resource_type}")

if not recent_logs:
    print("  No audit logs found")

# Test the middleware paths
print("\nChecking middleware configuration:")
from authentication.audit_middleware import AuditLoggingMiddleware
middleware = AuditLoggingMiddleware(lambda x: None)
print(f"  Audit methods: {middleware.AUDIT_METHODS}")
print(f"  Audit paths: {middleware.AUDIT_PATHS}")