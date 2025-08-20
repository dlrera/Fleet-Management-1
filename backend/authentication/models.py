from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
import json


class UserInvitation(models.Model):
    """Model for user invitations"""
    INVITATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=50)  # Store group name
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    status = models.CharField(max_length=20, choices=INVITATION_STATUS_CHOICES, default='pending')
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_invitations')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation to {self.email} ({self.status})"
    
    def is_expired(self):
        """Check if invitation has expired"""
        return timezone.now() > self.expires_at
    
    def accept(self, user):
        """Mark invitation as accepted"""
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.save()
        return user


class UserProfile(models.Model):
    """Extended user profile for additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    deactivated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deactivated_users')
    
    def __str__(self):
        return f"{self.user.username} Profile"


class AuditLog(models.Model):
    """Immutable audit log for all system changes"""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('permission_granted', 'Permission Granted'),
        ('permission_denied', 'Permission Denied'),
        ('role_assigned', 'Role Assigned'),
        ('role_removed', 'Role Removed'),
        ('invitation_sent', 'Invitation Sent'),
        ('invitation_accepted', 'Invitation Accepted'),
        ('user_suspended', 'User Suspended'),
        ('user_activated', 'User Activated'),
        ('impersonate_start', 'Impersonation Started'),
        ('impersonate_end', 'Impersonation Ended'),
        ('api_token_created', 'API Token Created'),
        ('api_token_revoked', 'API Token Revoked'),
        ('mfa_enabled', 'MFA Enabled'),
        ('mfa_disabled', 'MFA Disabled'),
        ('export_data', 'Data Exported'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Actor information
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_actions')
    actor_email = models.EmailField()
    actor_role = models.CharField(max_length=50)
    
    # Action details
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    resource_type = models.CharField(max_length=100, db_index=True)
    resource_id = models.CharField(max_length=100, db_index=True)
    resource_name = models.CharField(max_length=255)
    
    # Change details
    before_state = models.JSONField(null=True, blank=True)
    after_state = models.JSONField(null=True, blank=True)
    changes = models.JSONField(null=True, blank=True)
    
    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.UUIDField(null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional context
    reason = models.TextField(blank=True)
    approval_id = models.UUIDField(null=True, blank=True)
    risk_score = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['actor', '-timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['action', '-timestamp']),
        ]
        permissions = [
            ('view_audit_logs', 'Can view audit logs'),
            ('export_audit_logs', 'Can export audit logs'),
        ]
    
    def __str__(self):
        return f"{self.actor_email} - {self.action} - {self.resource_type}/{self.resource_id}"
    
    def save(self, *args, **kwargs):
        """Make audit logs immutable after creation"""
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise ValueError("Audit logs cannot be modified")
        super().save(*args, **kwargs)


class Organization(models.Model):
    """Organization settings and configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    # Settings
    settings = models.JSONField(default=dict)
    identity_settings = models.JSONField(default=dict)
    security_settings = models.JSONField(default=dict)
    
    # Compliance
    retention_days = models.IntegerField(default=365)
    require_mfa = models.BooleanField(default=False)
    require_approval_for_elevation = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Scope(models.Model):
    """Scoping for permissions (region, depot, vehicle group)"""
    SCOPE_TYPE_CHOICES = [
        ('global', 'Global'),
        ('organization', 'Organization'),
        ('region', 'Region'),
        ('depot', 'Depot'),
        ('vehicle_group', 'Vehicle Group'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='scopes')
    name = models.CharField(max_length=255)
    scope_type = models.CharField(max_length=20, choices=SCOPE_TYPE_CHOICES)
    criteria = models.JSONField(default=dict)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scope_type', 'name']
        unique_together = [['organization', 'name']]
    
    def __str__(self):
        return f"{self.scope_type}: {self.name}"


class Permission(models.Model):
    """Granular permission definitions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50)
    risk_level = models.IntegerField(default=1)
    requires_mfa = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.key} - {self.name}"


class CustomRole(models.Model):
    """Custom roles with granular permissions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='custom_roles')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_system = models.BooleanField(default=False)
    inherited_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Permissions
    permissions = models.ManyToManyField(Permission, through='RolePermission')
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_roles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = [['organization', 'name']]
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class RolePermission(models.Model):
    """Many-to-many relationship between roles and permissions with effect"""
    EFFECT_CHOICES = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
    ]
    
    role = models.ForeignKey(CustomRole, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    effect = models.CharField(max_length=10, choices=EFFECT_CHOICES, default='allow')
    conditions = models.JSONField(null=True, blank=True)
    
    class Meta:
        unique_together = [['role', 'permission']]
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.key} ({self.effect})"


class UserRoleAssignment(models.Model):
    """User role assignments with scope"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(CustomRole, on_delete=models.CASCADE)
    scope = models.ForeignKey(Scope, on_delete=models.CASCADE, null=True, blank=True)
    
    # Temporal aspects
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    is_temporary = models.BooleanField(default=False)
    
    # Assignment details
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-assigned_at']
    
    def __str__(self):
        scope_str = f" ({self.scope})" if self.scope else ""
        return f"{self.user.username} - {self.role.name}{scope_str}"
    
    def is_active(self):
        """Check if assignment is currently active"""
        now = timezone.now()
        if self.valid_until and now > self.valid_until:
            return False
        return now >= self.valid_from


class ApprovalRequest(models.Model):
    """Approval workflow for elevated permissions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requestor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approval_requests')
    action_key = models.CharField(max_length=100)
    parameters = models.JSONField()
    reason = models.TextField()
    
    # Approval details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approvals_given')
    approval_notes = models.TextField(blank=True)
    
    # Timing
    requested_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    decided_at = models.DateTimeField(null=True, blank=True)
    
    # Auto-execution
    auto_execute = models.BooleanField(default=False)
    executed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.requestor.username} - {self.action_key} ({self.status})"


class APIToken(models.Model):
    """API tokens with scoped permissions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_tokens')
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    
    # Scopes and permissions
    scopes = models.JSONField(default=list)
    role = models.ForeignKey(CustomRole, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Usage tracking
    last_used_at = models.DateTimeField(null=True, blank=True)
    last_used_ip = models.GenericIPAddressField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    # Lifecycle
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='revoked_tokens')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def is_valid(self):
        """Check if token is still valid"""
        if self.revoked_at:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True


class SessionInfo(models.Model):
    """Track user sessions for security"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=100, unique=True)
    
    # Device info
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_name = models.CharField(max_length=255, blank=True)
    
    # Session details
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    # Security
    is_mfa_verified = models.BooleanField(default=False)
    is_suspicious = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.ip_address} ({self.created_at})"