"""
User management views for admin users
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import UserInvitation, UserProfile
from .serializers import UserSerializer
from .permissions import IsAdmin


class UserManagementViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users - Admin only"""
    queryset = User.objects.all().prefetch_related('groups')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        """Get all users with their groups and profiles"""
        return User.objects.all().prefetch_related('groups').select_related('profile')
    
    @action(detail=False, methods=['get'])
    def list_users(self, request):
        """List all users with their roles"""
        users = self.get_queryset()
        user_data = []
        
        for user in users:
            roles = list(user.groups.values_list('name', flat=True))
            profile = getattr(user, 'profile', None)
            
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'roles': roles,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'department': profile.department if profile else '',
                'position': profile.position if profile else '',
                'employee_id': profile.employee_id if profile else ''
            })
        
        return Response(user_data)
    
    @action(detail=True, methods=['post'])
    def update_roles(self, request, pk=None):
        """Update user roles"""
        user = self.get_object()
        roles = request.data.get('roles', [])
        
        # Clear existing groups
        user.groups.clear()
        
        # Add new groups
        for role_name in roles:
            try:
                group = Group.objects.get(name=role_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                return Response(
                    {'error': f'Role {role_name} does not exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Return updated user data
        updated_roles = list(user.groups.values_list('name', flat=True))
        return Response({
            'message': 'Roles updated successfully',
            'roles': updated_roles
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user account"""
        user = self.get_object()
        
        # Prevent self-deactivation
        if user == request.user:
            return Response(
                {'error': 'You cannot deactivate your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Deactivate user
        user.is_active = False
        user.save()
        
        # Update profile if exists
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.is_active = False
        profile.deactivated_at = timezone.now()
        profile.deactivated_by = request.user
        profile.save()
        
        return Response({'message': f'User {user.username} has been deactivated'})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Reactivate a user account"""
        user = self.get_object()
        
        # Activate user
        user.is_active = True
        user.save()
        
        # Update profile if exists
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.is_active = True
        profile.deactivated_at = None
        profile.deactivated_by = None
        profile.save()
        
        return Response({'message': f'User {user.username} has been activated'})
    
    @action(detail=False, methods=['post'])
    def send_invitation(self, request):
        """Send invitation email to new user"""
        email = request.data.get('email')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        role = request.data.get('role', 'Read-only')
        
        # Validate email
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'User with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if invitation already sent
        existing_invitation = UserInvitation.objects.filter(
            email=email,
            status='pending'
        ).first()
        
        if existing_invitation and not existing_invitation.is_expired():
            return Response(
                {'error': 'An active invitation already exists for this email'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create invitation
        invitation = UserInvitation.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            invited_by=request.user,
            expires_at=timezone.now() + timedelta(days=7)  # 7 day expiration
        )
        
        # Generate invitation URL
        invitation_url = f"{request.build_absolute_uri('/')[:-1]}/register?token={invitation.token}"
        
        # Send email (in production, use proper email template)
        try:
            send_mail(
                subject='Invitation to Fleet Management System',
                message=f'''
                Hello {first_name or 'User'},
                
                You have been invited to join the Fleet Management System with the role of {role}.
                
                Please click the following link to create your account:
                {invitation_url}
                
                This invitation will expire in 7 days.
                
                Best regards,
                Fleet Management Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@fleetmanagement.com',
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response({
                'message': f'Invitation sent to {email}',
                'invitation_id': str(invitation.id)
            })
        except Exception as e:
            # If email fails, still return success but note that email wasn't sent
            return Response({
                'message': f'Invitation created but email could not be sent',
                'invitation_id': str(invitation.id),
                'invitation_url': invitation_url,
                'error': str(e)
            })
    
    @action(detail=False, methods=['get'])
    def pending_invitations(self, request):
        """Get list of pending invitations"""
        invitations = UserInvitation.objects.filter(status='pending')
        
        invitation_data = []
        for inv in invitations:
            invitation_data.append({
                'id': str(inv.id),
                'email': inv.email,
                'first_name': inv.first_name,
                'last_name': inv.last_name,
                'role': inv.role,
                'status': inv.status,
                'invited_by': inv.invited_by.username if inv.invited_by else None,
                'created_at': inv.created_at,
                'expires_at': inv.expires_at,
                'is_expired': inv.is_expired()
            })
        
        return Response(invitation_data)
    
    @action(detail=False, methods=['post'])
    def cancel_invitation(self, request):
        """Cancel a pending invitation"""
        invitation_id = request.data.get('invitation_id')
        
        try:
            invitation = UserInvitation.objects.get(id=invitation_id, status='pending')
            invitation.status = 'cancelled'
            invitation.save()
            
            return Response({'message': f'Invitation to {invitation.email} has been cancelled'})
        except UserInvitation.DoesNotExist:
            return Response(
                {'error': 'Invitation not found or already processed'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def available_roles(self, request):
        """Get list of available roles"""
        groups = Group.objects.all()
        roles = [group.name for group in groups]
        return Response({'roles': roles})
    
    def destroy(self, request, *args, **kwargs):
        """Delete a user (soft delete by deactivating)"""
        user = self.get_object()
        
        # Prevent self-deletion
        if user == request.user:
            return Response(
                {'error': 'You cannot delete your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent deleting the last admin
        if user.groups.filter(name='Admin').exists():
            admin_count = User.objects.filter(
                groups__name='Admin',
                is_active=True
            ).count()
            
            if admin_count <= 1:
                return Response(
                    {'error': 'Cannot delete the last admin user'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Soft delete by deactivating
        user.is_active = False
        user.save()
        
        # Update profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.is_active = False
        profile.deactivated_at = timezone.now()
        profile.deactivated_by = request.user
        profile.save()
        
        return Response({'message': f'User {user.username} has been deleted'})