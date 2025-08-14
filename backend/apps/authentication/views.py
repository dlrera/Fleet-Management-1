from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django_ratelimit.decorators import ratelimit
from axes.decorators import axes_dispatch
import logging

from .serializers import (
    UserSerializer, 
    RegisterSerializer, 
    LoginSerializer, 
    ChangePasswordSerializer
)

logger = logging.getLogger('security')


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            
            logger.info(f"User registration successful: {user.username} from IP: {self.get_client_ip(request)}")
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Registration failed from IP: {self.get_client_ip(request)}, Error: {str(e)}")
            return Response({
                'message': 'Registration failed. Please try again.'
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='10/m', method='POST')
@axes_dispatch
@csrf_protect
def login_view(request):
    try:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Delete existing tokens for security (single session)
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        
        logger.info(f"Login successful: {user.username} from IP: {get_client_ip(request)}")
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        })
    except Exception as e:
        logger.warning(f"Login failed from IP: {get_client_ip(request)}, Error: {str(e)}")
        return Response({
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='5/m', method='POST')
def logout_view(request):
    try:
        request.user.auth_token.delete()
        logger.info(f"User logged out: {request.user.username}")
    except Exception as e:
        logger.error(f"Logout error for user {request.user.username}: {str(e)}")
    
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='30/m', method='GET')
def user_profile_view(request):
    try:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Profile view error for user {request.user.username}: {str(e)}")
        return Response({
            'message': 'Error retrieving profile'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='10/m', method='PUT')
def update_profile_view(request):
    try:
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Profile updated: {request.user.username}")
            return Response({
                'user': serializer.data,
                'message': 'Profile updated successfully'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Profile update error for user {request.user.username}: {str(e)}")
        return Response({
            'message': 'Error updating profile'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='3/h', method='POST')  # Strict limit for password changes
def change_password_view(request):
    try:
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Delete all existing tokens (force re-login on all devices)
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            
            logger.info(f"Password changed: {user.username}")
            
            return Response({
                'message': 'Password changed successfully',
                'token': token.key
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Password change error for user {request.user.username}: {str(e)}")
        return Response({
            'message': 'Error changing password'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='60/m', method='GET')
def check_auth_view(request):
    try:
        if request.user.is_authenticated:
            return Response({
                'authenticated': True,
                'user': UserSerializer(request.user).data
            })
        return Response({'authenticated': False})
    except Exception as e:
        logger.error(f"Auth check error: {str(e)}")
        return Response({'authenticated': False})


def get_client_ip(request):
    """Safely get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip