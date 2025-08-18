from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        
        response = Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        })
        
        # Set httpOnly cookie for token
        response.set_cookie(
            'auth_token',
            token.key,
            max_age=86400 * 7,  # 7 days
            httponly=True,
            secure=request.is_secure(),
            samesite='Lax'
        )
        
        return response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        response = Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
        
        # Set httpOnly cookie for token
        response.set_cookie(
            'auth_token',
            token.key,
            max_age=86400 * 7,  # 7 days
            httponly=True,
            secure=request.is_secure(),
            samesite='Lax'
        )
        
        return response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    if request.user.auth_token:
        request.user.auth_token.delete()
    logout(request)
    
    response = Response({'detail': 'Successfully logged out'})
    # Clear the auth cookie
    response.delete_cookie('auth_token')
    
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_view(request):
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_auth(request):
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': UserSerializer(request.user).data
        })
    return Response({'authenticated': False})