from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser


class CookieTokenAuthentication(TokenAuthentication):
    """
    Custom authentication class that reads token from httpOnly cookie
    as well as Authorization header for backward compatibility
    """
    
    def authenticate(self, request):
        # First try the standard Authorization header
        auth_header = super().authenticate(request)
        if auth_header:
            return auth_header
        
        # Try to get token from cookie
        token_key = request.COOKIES.get('auth_token')
        if not token_key:
            return None
            
        return self.authenticate_credentials(token_key)
    
    def authenticate_credentials(self, key):
        """
        Authenticate the given credentials.
        """
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            return None
        
        if not token.user.is_active:
            return None
        
        return (token.user, token)