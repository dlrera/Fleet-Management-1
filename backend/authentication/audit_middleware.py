"""
Middleware for automatic audit logging
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import AuditLog
import json
import uuid


class AuditLoggingMiddleware(MiddlewareMixin):
    """Middleware to automatically log all significant actions"""
    
    # Actions to log automatically
    AUDIT_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    # Paths to always audit
    AUDIT_PATHS = [
        '/api/auth/manage/',
        '/api/fuel/transactions/',
        '/api/assets/',
        '/api/drivers/',
    ]
    
    def process_request(self, request):
        """Add request ID for tracking"""
        request.request_id = str(uuid.uuid4())
        return None
    
    def process_response(self, request, response):
        """Log successful actions"""
        if self.should_audit(request, response):
            self.create_audit_log(request, response)
        return response
    
    def should_audit(self, request, response):
        """Determine if this request should be audited"""
        # Don't audit if not authenticated
        if isinstance(request.user, AnonymousUser):
            return False
        
        # Always audit specific methods
        if request.method in self.AUDIT_METHODS:
            return True
        
        # Always audit specific paths
        for path in self.AUDIT_PATHS:
            if request.path.startswith(path):
                return True
        
        # Audit failed permission checks
        if response.status_code == 403:
            return True
        
        return False
    
    def create_audit_log(self, request, response):
        """Create an audit log entry"""
        try:
            # Determine action type
            action = self.get_action_type(request, response)
            
            # Extract resource information
            resource_type, resource_id = self.extract_resource_info(request)
            
            # Get user role
            user_roles = list(request.user.groups.values_list('name', flat=True))
            user_role = user_roles[0] if user_roles else 'No Role'
            
            # Create audit log
            AuditLog.objects.create(
                actor=request.user,
                actor_email=request.user.email,
                actor_role=user_role,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id or '',
                resource_name=self.get_resource_name(request, response),
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                request_id=getattr(request, 'request_id', None),
                session_id=request.session.session_key if hasattr(request, 'session') else '',
                risk_score=self.calculate_risk_score(request, response)
            )
        except Exception as e:
            # Log error but don't break the response
            print(f"Audit logging error: {e}")
    
    def get_action_type(self, request, response):
        """Determine the action type from request"""
        if response.status_code == 403:
            return 'permission_denied'
        
        method_map = {
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
            'GET': 'view'
        }
        
        # Special cases
        if '/login/' in request.path:
            return 'login'
        elif '/logout/' in request.path:
            return 'logout'
        elif '/invite' in request.path:
            return 'invitation_sent'
        elif '/roles' in request.path:
            return 'role_assigned'
        elif '/suspend' in request.path:
            return 'user_suspended'
        elif '/activate' in request.path:
            return 'user_activated'
        elif '/export' in request.path:
            return 'export_data'
        
        return method_map.get(request.method, 'unknown')
    
    def extract_resource_info(self, request):
        """Extract resource type and ID from request path"""
        path_parts = request.path.strip('/').split('/')
        
        if len(path_parts) >= 3:
            # e.g., /api/assets/123/
            resource_type = path_parts[1]
            resource_id = path_parts[2] if len(path_parts) > 2 and path_parts[2] else None
            return resource_type, resource_id
        
        return 'unknown', None
    
    def get_resource_name(self, request, response):
        """Try to get a human-readable resource name"""
        if response.status_code == 200 or response.status_code == 201:
            try:
                data = json.loads(response.content)
                # Try common fields
                for field in ['name', 'username', 'email', 'asset_id', 'driver_id', 'title']:
                    if field in data:
                        return str(data[field])
            except:
                pass
        
        return request.path
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def calculate_risk_score(self, request, response):
        """Calculate risk score for the action"""
        score = 0
        
        # High risk methods
        if request.method in ['DELETE']:
            score += 30
        elif request.method in ['PUT', 'PATCH', 'POST']:
            score += 20
        
        # High risk paths
        if '/users/' in request.path:
            score += 20
        if '/roles/' in request.path:
            score += 25
        if '/permissions/' in request.path:
            score += 30
        if '/export' in request.path:
            score += 15
        
        # Failed attempts
        if response.status_code >= 400:
            score += 10
        
        # Unusual time (outside business hours - simplified)
        from datetime import datetime
        hour = datetime.now().hour
        if hour < 6 or hour > 22:
            score += 10
        
        return min(score, 100)  # Cap at 100