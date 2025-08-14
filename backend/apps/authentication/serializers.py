import re
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.authtoken.models import Token
from .validators import validate_username, validate_email, CustomPasswordValidator
import logging

logger = logging.getLogger('security')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')
        read_only_fields = ('id', 'is_staff')

    def validate_email(self, value):
        validate_email(value)
        return value.lower().strip()

    def validate_first_name(self, value):
        if value and not re.match(r'^[a-zA-Z\s\-\']+$', value):
            raise serializers.ValidationError("First name can only contain letters, spaces, hyphens, and apostrophes.")
        return value.strip()

    def validate_last_name(self, value):
        if value and not re.match(r'^[a-zA-Z\s\-\']+$', value):
            raise serializers.ValidationError("Last name can only contain letters, spaces, hyphens, and apostrophes.")
        return value.strip()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate_username(self, value):
        validate_username(value)
        # Check if username already exists (case-insensitive)
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value.lower().strip()

    def validate_email(self, value):
        validate_email(value)
        # Check if email already exists (case-insensitive)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return value.lower().strip()

    def validate_first_name(self, value):
        if not value:
            raise serializers.ValidationError("First name is required.")
        if not re.match(r'^[a-zA-Z\s\-\']+$', value):
            raise serializers.ValidationError("First name can only contain letters, spaces, hyphens, and apostrophes.")
        return value.strip()

    def validate_last_name(self, value):
        if not value:
            raise serializers.ValidationError("Last name is required.")
        if not re.match(r'^[a-zA-Z\s\-\']+$', value):
            raise serializers.ValidationError("Last name can only contain letters, spaces, hyphens, and apostrophes.")
        return value.strip()

    def validate_password(self, value):
        # Use custom password validator
        validator = CustomPasswordValidator()
        try:
            validator.validate(value)
            validate_password(value)  # Django's built-in validation
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords don't match"})
        
        # Additional validation with user context
        validator = CustomPasswordValidator()
        try:
            # Create a temporary user object for validation
            temp_user = User(
                username=attrs['username'],
                email=attrs['email'],
                first_name=attrs['first_name'],
                last_name=attrs['last_name']
            )
            validator.validate(attrs['password'], temp_user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": str(e)})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        try:
            user = User.objects.create_user(**validated_data)
            Token.objects.create(user=user)
            logger.info(f"New user registered: {user.username}")
            return user
        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            raise serializers.ValidationError("Registration failed. Please try again.")


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, max_length=128)

    def validate_username(self, value):
        return value.strip()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("Must include username and password")

        # Sanitize username input
        username = username.strip()
        
        # Attempt authentication
        user = authenticate(username=username, password=password)
        
        if not user:
            logger.warning(f"Failed login attempt for username: {username}")
            raise serializers.ValidationError("Invalid credentials")
        
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {username}")
            raise serializers.ValidationError("Account is disabled")
        
        logger.info(f"Successful login: {user.username}")
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, max_length=128)
    new_password = serializers.CharField(write_only=True, min_length=12, max_length=128)
    confirm_password = serializers.CharField(write_only=True, max_length=128)

    def validate_new_password(self, value):
        # Use custom password validator
        validator = CustomPasswordValidator()
        user = self.context['request'].user
        try:
            validator.validate(value, user)
            validate_password(value, user)  # Django's built-in validation
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            logger.warning(f"Incorrect old password for user: {user.username}")
            raise serializers.ValidationError('Current password is incorrect')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords don't match"})
        
        # Ensure new password is different from old password
        user = self.context['request'].user
        if user.check_password(attrs['new_password']):
            raise serializers.ValidationError({"new_password": "New password must be different from current password"})
        
        return attrs