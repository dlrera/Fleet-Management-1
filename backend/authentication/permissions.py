"""
Custom permission classes for role-based access control
"""
from rest_framework import permissions
from django.contrib.auth.models import User
try:
    from .models import Permission as CustomPermission, RoleAssignment
except ImportError:
    # Fallback if models aren't available yet
    CustomPermission = None
    RoleAssignment = None


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        return False


class IsAdmin(permissions.BasePermission):
    """
    Permission class for Admin users
    Full access to all resources
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Admin').exists()


class IsFleetManager(permissions.BasePermission):
    """
    Permission class for Fleet Manager users
    Can manage fleet operations but not system settings
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is Admin or Fleet Manager
        return request.user.groups.filter(
            name__in=['Admin', 'Fleet Manager']
        ).exists()


class IsTechnician(permissions.BasePermission):
    """
    Permission class for Technician users
    Can create and edit their own entries
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is Admin, Fleet Manager, or Technician
        return request.user.groups.filter(
            name__in=['Admin', 'Fleet Manager', 'Technician']
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        # Admins and Fleet Managers have full access
        if request.user.groups.filter(name__in=['Admin', 'Fleet Manager']).exists():
            return True
        
        # Technicians can only edit their own entries
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if the user created this object
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class IsReadOnly(permissions.BasePermission):
    """
    Permission class for Read-only users
    Can only view data, no modifications allowed
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Only allow GET, HEAD, OPTIONS requests
        return request.method in permissions.SAFE_METHODS


class RoleBasedPermission(permissions.BasePermission):
    """
    Dynamic permission class based on user roles
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_groups = request.user.groups.values_list('name', flat=True)
        
        # Admin has full access
        if 'Admin' in user_groups:
            return True
        
        # Fleet Manager has access to most operations
        if 'Fleet Manager' in user_groups:
            # Restrict certain admin-only views if needed
            restricted_views = ['UserViewSet', 'GroupViewSet']
            if view.__class__.__name__ in restricted_views:
                return request.method in permissions.SAFE_METHODS
            return True
        
        # Technician has limited write access
        if 'Technician' in user_groups:
            # Can create and read, but limited edit/delete
            if request.method in ['GET', 'HEAD', 'OPTIONS', 'POST']:
                return True
            return False
        
        # Read-only users can only read
        if 'Read-only' in user_groups:
            return request.method in permissions.SAFE_METHODS
        
        # Default deny if no recognized role
        return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_groups = request.user.groups.values_list('name', flat=True)
        
        # Admin and Fleet Manager have full object access
        if 'Admin' in user_groups or 'Fleet Manager' in user_groups:
            return True
        
        # Read-only users can only read
        if 'Read-only' in user_groups:
            return request.method in permissions.SAFE_METHODS
        
        # Technicians can read all, but only modify their own
        if 'Technician' in user_groups:
            if request.method in permissions.SAFE_METHODS:
                return True
            
            # Check ownership for write operations
            if hasattr(obj, 'created_by'):
                return obj.created_by == request.user
            if hasattr(obj, 'user'):
                return obj.user == request.user
            
            return False
        
        return False


# Role-specific permissions for different resources
class AssetPermission(RoleBasedPermission):
    """
    Permissions for Asset management
    - Admin: Full access
    - Fleet Manager: Full access
    - Technician: Read only
    - Read-only: Read only
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_groups = request.user.groups.values_list('name', flat=True)
        
        # Admin and Fleet Manager have full access
        if 'Admin' in user_groups or 'Fleet Manager' in user_groups:
            return True
        
        # Technician and Read-only can only read
        if 'Technician' in user_groups or 'Read-only' in user_groups:
            return request.method in permissions.SAFE_METHODS
        
        return False


class FuelTransactionPermission(RoleBasedPermission):
    """
    Permissions for Fuel Transaction management
    - Admin: Full access
    - Fleet Manager: Full access
    - Technician: Can create and edit own entries
    - Read-only: Read only
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_groups = request.user.groups.values_list('name', flat=True)
        
        # Admin and Fleet Manager have full access
        if 'Admin' in user_groups or 'Fleet Manager' in user_groups:
            return True
        
        # Technician can create and read
        if 'Technician' in user_groups:
            return request.method in ['GET', 'HEAD', 'OPTIONS', 'POST']
        
        # Read-only can only read
        if 'Read-only' in user_groups:
            return request.method in permissions.SAFE_METHODS
        
        return False


class DriverPermission(RoleBasedPermission):
    """
    Permissions for Driver management
    - Admin: Full access
    - Fleet Manager: Full access
    - Technician: Can update own profile only
    - Read-only: Read only
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_groups = request.user.groups.values_list('name', flat=True)
        
        # Admin and Fleet Manager have full access
        if 'Admin' in user_groups or 'Fleet Manager' in user_groups:
            return True
        
        # Technician can read all drivers
        if 'Technician' in user_groups:
            return request.method in permissions.SAFE_METHODS
        
        # Read-only can only read
        if 'Read-only' in user_groups:
            return request.method in permissions.SAFE_METHODS
        
        return False


# Granular permission classes using custom Permission model
class GranularPermission(permissions.BasePermission):
    """Base class for granular permissions using custom Permission model"""
    
    def has_permission(self, request, view):
        """Check if user has permission for the view"""
        if not request.user.is_authenticated:
            return False
            
        # Superusers always have permission
        if request.user.is_superuser:
            return True
            
        # Check custom permissions
        return self.check_custom_permission(request, view)
    
    def check_custom_permission(self, request, view):
        """Override in subclasses"""
        return False
    
    def get_user_permissions(self, user):
        """Get all permissions for a user through their roles"""
        permissions = set()
        
        # Check if models are available
        if RoleAssignment and CustomPermission:
            # Get role assignments for the user
            role_assignments = RoleAssignment.objects.filter(
                user=user,
                is_active=True
            ).select_related('role')
            
            # Collect permissions from all roles
            for assignment in role_assignments:
                role_permissions = CustomPermission.objects.filter(
                    permissionassignment__role=assignment.role,
                    permissionassignment__is_active=True
                ).values_list('name', flat=True)
                permissions.update(role_permissions)
        
        return permissions


class GranularAssetPermission(GranularPermission):
    """Granular permission class for Asset operations"""
    
    def check_custom_permission(self, request, view):
        user_permissions = self.get_user_permissions(request.user)
        
        # Map HTTP methods to permission names
        if request.method == 'GET':
            return 'assets.view' in user_permissions
        elif request.method == 'POST':
            return 'assets.create' in user_permissions
        elif request.method in ['PUT', 'PATCH']:
            return 'assets.edit' in user_permissions
        elif request.method == 'DELETE':
            return 'assets.delete' in user_permissions
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions"""
        if request.user.is_superuser:
            return True
            
        user_permissions = self.get_user_permissions(request.user)
        
        # Check department-based scoping
        if hasattr(obj, 'department') and hasattr(request.user, 'profile'):
            user_department = getattr(request.user.profile, 'department', None)
            if user_department and obj.department != user_department:
                # User can only view assets from other departments
                if request.method == 'GET':
                    return 'assets.view_all' in user_permissions
                return False
        
        # Standard object permissions
        if request.method == 'GET':
            return 'assets.view' in user_permissions
        elif request.method in ['PUT', 'PATCH']:
            return 'assets.edit' in user_permissions
        elif request.method == 'DELETE':
            return 'assets.delete' in user_permissions
        
        return False


class GranularLocationPermission(GranularPermission):
    """Granular permission class for Location operations"""
    
    def check_custom_permission(self, request, view):
        user_permissions = self.get_user_permissions(request.user)
        
        # Location updates require special permission
        if view.action == 'create' and request.path.endswith('/updates/'):
            return 'locations.update' in user_permissions
        
        if request.method == 'GET':
            return 'locations.view' in user_permissions
        elif request.method == 'POST':
            return 'locations.create' in user_permissions
        elif request.method in ['PUT', 'PATCH']:
            return 'locations.edit' in user_permissions
        elif request.method == 'DELETE':
            return 'locations.delete' in user_permissions
        
        return False


class GranularZonePermission(GranularPermission):
    """Granular permission class for Zone operations"""
    
    def check_custom_permission(self, request, view):
        user_permissions = self.get_user_permissions(request.user)
        
        if request.method == 'GET':
            return 'zones.view' in user_permissions
        elif request.method == 'POST':
            return 'zones.create' in user_permissions
        elif request.method in ['PUT', 'PATCH']:
            return 'zones.edit' in user_permissions
        elif request.method == 'DELETE':
            return 'zones.delete' in user_permissions
        
        return False


def check_permission(user, permission_name):
    """Utility function to check if a user has a specific permission"""
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Check if models are available
    if CustomPermission:
        # Check through role assignments
        return CustomPermission.objects.filter(
            permissionassignment__role__roleassignment__user=user,
            permissionassignment__is_active=True,
            permissionassignment__role__roleassignment__is_active=True,
            name=permission_name
        ).exists()
    
    return False


def get_user_scopes(user):
    """Get all scopes assigned to a user"""
    if not user.is_authenticated:
        return []
    
    if user.is_superuser:
        return ['global']  # Superusers have global scope
    
    scopes = []
    
    # Check if models are available
    if RoleAssignment:
        # Get scopes through role assignments
        role_assignments = RoleAssignment.objects.filter(
            user=user,
            is_active=True
        ).select_related('scope')
        
        for assignment in role_assignments:
            if assignment.scope:
                scopes.append({
                    'type': assignment.scope.scope_type,
                    'value': assignment.scope.scope_value,
                    'name': assignment.scope.name
                })
    
    return scopes