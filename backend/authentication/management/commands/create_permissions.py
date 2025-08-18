"""
Management command to create the permission catalog
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from authentication.models import Permission, Organization


class Command(BaseCommand):
    help = 'Creates the permission catalog and system roles'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating permission catalog...')
        
        # Define all permissions
        permissions_data = [
            # Asset Management
            {'key': 'assets.view', 'name': 'View Assets', 'category': 'Assets', 'risk_level': 1},
            {'key': 'assets.create', 'name': 'Create Assets', 'category': 'Assets', 'risk_level': 2},
            {'key': 'assets.edit', 'name': 'Edit Assets', 'category': 'Assets', 'risk_level': 2},
            {'key': 'assets.delete', 'name': 'Delete Assets', 'category': 'Assets', 'risk_level': 3},
            {'key': 'assets.export', 'name': 'Export Assets', 'category': 'Assets', 'risk_level': 2},
            {'key': 'assets.bulk_import', 'name': 'Bulk Import Assets', 'category': 'Assets', 'risk_level': 3},
            {'key': 'assets.view_pii', 'name': 'View Asset PII', 'category': 'Assets', 'risk_level': 3, 'requires_mfa': True},
            
            # Driver Management
            {'key': 'drivers.view', 'name': 'View Drivers', 'category': 'Drivers', 'risk_level': 1},
            {'key': 'drivers.create', 'name': 'Create Drivers', 'category': 'Drivers', 'risk_level': 2},
            {'key': 'drivers.edit', 'name': 'Edit Drivers', 'category': 'Drivers', 'risk_level': 2},
            {'key': 'drivers.delete', 'name': 'Delete Drivers', 'category': 'Drivers', 'risk_level': 3},
            {'key': 'drivers.view_pii', 'name': 'View Driver PII', 'category': 'Drivers', 'risk_level': 3, 'requires_mfa': True},
            {'key': 'drivers.assign_vehicle', 'name': 'Assign Vehicle to Driver', 'category': 'Drivers', 'risk_level': 2},
            
            # Fuel Management
            {'key': 'fuel.view', 'name': 'View Fuel Transactions', 'category': 'Fuel', 'risk_level': 1},
            {'key': 'fuel.create', 'name': 'Create Fuel Transactions', 'category': 'Fuel', 'risk_level': 2},
            {'key': 'fuel.edit', 'name': 'Edit Fuel Transactions', 'category': 'Fuel', 'risk_level': 2},
            {'key': 'fuel.delete', 'name': 'Delete Fuel Transactions', 'category': 'Fuel', 'risk_level': 3},
            {'key': 'fuel.approve', 'name': 'Approve Fuel Transactions', 'category': 'Fuel', 'risk_level': 3, 'requires_approval': True},
            {'key': 'fuel.export', 'name': 'Export Fuel Data', 'category': 'Fuel', 'risk_level': 2},
            
            # Location Management
            {'key': 'locations.view', 'name': 'View Locations', 'category': 'Locations', 'risk_level': 1},
            {'key': 'locations.create', 'name': 'Create Locations', 'category': 'Locations', 'risk_level': 2},
            {'key': 'locations.edit', 'name': 'Edit Locations', 'category': 'Locations', 'risk_level': 2},
            {'key': 'locations.delete', 'name': 'Delete Locations', 'category': 'Locations', 'risk_level': 3},
            
            # User Management
            {'key': 'users.view', 'name': 'View Users', 'category': 'Users', 'risk_level': 2},
            {'key': 'users.create', 'name': 'Create Users', 'category': 'Users', 'risk_level': 4, 'requires_mfa': True},
            {'key': 'users.edit', 'name': 'Edit Users', 'category': 'Users', 'risk_level': 4, 'requires_mfa': True},
            {'key': 'users.delete', 'name': 'Delete Users', 'category': 'Users', 'risk_level': 5, 'requires_mfa': True, 'requires_approval': True},
            {'key': 'users.suspend', 'name': 'Suspend Users', 'category': 'Users', 'risk_level': 4, 'requires_mfa': True},
            {'key': 'users.impersonate', 'name': 'Impersonate Users', 'category': 'Users', 'risk_level': 5, 'requires_mfa': True, 'requires_approval': True},
            
            # Role Management
            {'key': 'roles.view', 'name': 'View Roles', 'category': 'Roles', 'risk_level': 2},
            {'key': 'roles.create', 'name': 'Create Roles', 'category': 'Roles', 'risk_level': 5, 'requires_mfa': True, 'requires_approval': True},
            {'key': 'roles.edit', 'name': 'Edit Roles', 'category': 'Roles', 'risk_level': 5, 'requires_mfa': True, 'requires_approval': True},
            {'key': 'roles.delete', 'name': 'Delete Roles', 'category': 'Roles', 'risk_level': 5, 'requires_mfa': True, 'requires_approval': True},
            {'key': 'roles.assign', 'name': 'Assign Roles', 'category': 'Roles', 'risk_level': 4, 'requires_mfa': True},
            
            # Audit & Compliance
            {'key': 'audit.view', 'name': 'View Audit Logs', 'category': 'Audit', 'risk_level': 3, 'requires_mfa': True},
            {'key': 'audit.export', 'name': 'Export Audit Logs', 'category': 'Audit', 'risk_level': 4, 'requires_mfa': True},
            {'key': 'audit.delete', 'name': 'Delete Audit Logs', 'category': 'Audit', 'risk_level': 5, 'requires_mfa': True, 'requires_approval': True},
            
            # System Administration
            {'key': 'system.configure', 'name': 'Configure System Settings', 'category': 'System', 'risk_level': 5, 'requires_mfa': True, 'requires_approval': True},
            {'key': 'system.backup', 'name': 'Create System Backup', 'category': 'System', 'risk_level': 4, 'requires_mfa': True},
            {'key': 'system.restore', 'name': 'Restore System Backup', 'category': 'System', 'risk_level': 5, 'requires_mfa': True, 'requires_approval': True},
            
            # API Management
            {'key': 'api.create_token', 'name': 'Create API Token', 'category': 'API', 'risk_level': 3, 'requires_mfa': True},
            {'key': 'api.revoke_token', 'name': 'Revoke API Token', 'category': 'API', 'risk_level': 3, 'requires_mfa': True},
            {'key': 'api.view_tokens', 'name': 'View API Tokens', 'category': 'API', 'risk_level': 2},
        ]
        
        # Create permissions
        created_count = 0
        for perm_data in permissions_data:
            perm, created = Permission.objects.get_or_create(
                key=perm_data['key'],
                defaults={
                    'name': perm_data['name'],
                    'description': perm_data['name'],
                    'category': perm_data['category'],
                    'risk_level': perm_data['risk_level'],
                    'requires_mfa': perm_data.get('requires_mfa', False),
                    'requires_approval': perm_data.get('requires_approval', False),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"  Created permission: {perm.key}")
        
        self.stdout.write(self.style.SUCCESS(f"Created {created_count} new permissions"))
        
        # Create Dispatcher role if it doesn't exist
        dispatcher_group, created = Group.objects.get_or_create(name='Dispatcher')
        if created:
            self.stdout.write(self.style.SUCCESS("Created Dispatcher role"))
        
        # Create default organization if it doesn't exist
        org, created = Organization.objects.get_or_create(
            domain='fleet.local',
            defaults={
                'name': 'Default Fleet Organization',
                'retention_days': 365,
                'require_mfa': False,
                'require_approval_for_elevation': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created default organization"))
        
        self.stdout.write(self.style.SUCCESS("Permission catalog created successfully!"))