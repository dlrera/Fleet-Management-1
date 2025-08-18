"""
Management command to set up user roles and permissions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction


class Command(BaseCommand):
    help = 'Sets up user roles and permissions for the Fleet Management System'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up roles and permissions...')
        
        with transaction.atomic():
            # Create groups
            groups = self.create_groups()
            
            # Assign permissions to groups
            self.assign_permissions(groups)
            
            # Create sample users for testing (optional)
            if options.get('create_sample_users', False):
                self.create_sample_users(groups)
        
        self.stdout.write(self.style.SUCCESS('Successfully set up roles and permissions'))
    
    def create_groups(self):
        """Create the four main user groups"""
        group_names = ['Admin', 'Fleet Manager', 'Technician', 'Read-only']
        groups = {}
        
        for name in group_names:
            group, created = Group.objects.get_or_create(name=name)
            groups[name] = group
            if created:
                self.stdout.write(f'Created group: {name}')
            else:
                self.stdout.write(f'Group already exists: {name}')
        
        return groups
    
    def assign_permissions(self, groups):
        """Assign permissions to each group"""
        
        # Get all permissions
        all_permissions = Permission.objects.all()
        
        # Admin - gets all permissions
        admin_group = groups['Admin']
        admin_group.permissions.set(all_permissions)
        self.stdout.write('Assigned all permissions to Admin group')
        
        # Fleet Manager - gets most permissions except user management
        fleet_manager_group = groups['Fleet Manager']
        fleet_manager_permissions = all_permissions.exclude(
            content_type__app_label='auth',
            codename__in=['add_user', 'change_user', 'delete_user', 'add_group', 'change_group', 'delete_group']
        )
        fleet_manager_group.permissions.set(fleet_manager_permissions)
        self.stdout.write('Assigned fleet management permissions to Fleet Manager group')
        
        # Technician - limited permissions
        technician_group = groups['Technician']
        technician_permissions = Permission.objects.filter(
            codename__in=[
                # Fuel permissions
                'add_fueltransaction',
                'view_fueltransaction',
                'change_fueltransaction',  # Will be limited by object permission
                'view_fuelsite',
                'view_fuelcard',
                'view_fuelalert',
                
                # Driver permissions (view only)
                'view_driver',
                'view_drivercertification',
                'view_driverassetassignment',
                
                # Asset permissions (view only)
                'view_asset',
                'view_assetdocument',
                'view_maintenanceschedule',
                
                # Location permissions (view only)
                'view_location',
            ]
        )
        technician_group.permissions.set(technician_permissions)
        self.stdout.write('Assigned technician permissions to Technician group')
        
        # Read-only - view permissions only
        readonly_group = groups['Read-only']
        readonly_permissions = Permission.objects.filter(
            codename__startswith='view_'
        )
        readonly_group.permissions.set(readonly_permissions)
        self.stdout.write('Assigned read-only permissions to Read-only group')
    
    def create_sample_users(self, groups):
        """Create sample users for testing"""
        sample_users = [
            {
                'username': 'admin',
                'email': 'admin@fleet.com',
                'password': 'admin123',
                'group': 'Admin',
                'first_name': 'Admin',
                'last_name': 'User'
            },
            {
                'username': 'fleet_manager',
                'email': 'manager@fleet.com',
                'password': 'manager123',
                'group': 'Fleet Manager',
                'first_name': 'Fleet',
                'last_name': 'Manager'
            },
            {
                'username': 'technician',
                'email': 'tech@fleet.com',
                'password': 'tech123',
                'group': 'Technician',
                'first_name': 'Tech',
                'last_name': 'User'
            },
            {
                'username': 'viewer',
                'email': 'viewer@fleet.com',
                'password': 'viewer123',
                'group': 'Read-only',
                'first_name': 'View',
                'last_name': 'Only'
            }
        ]
        
        for user_data in sample_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'Created user: {user_data["username"]}')
            
            # Add user to group
            group = groups[user_data['group']]
            user.groups.add(group)
            self.stdout.write(f'Added {user_data["username"]} to {user_data["group"]} group')
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample-users',
            action='store_true',
            help='Create sample users for testing',
        )