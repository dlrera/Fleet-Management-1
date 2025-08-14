import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    """
    Validate that the password meets custom security requirements:
    - At least 12 characters long
    - Contains at least one lowercase letter
    - Contains at least one uppercase letter
    - Contains at least one digit
    - Contains at least one special character
    - Does not contain common patterns
    """
    
    def __init__(self, min_length=12):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must be at least %(min_length)d characters long."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter."),
                code='password_no_lower',
            )

        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter."),
                code='password_no_upper',
            )

        if not re.search(r'\d', password):
            raise ValidationError(
                _("Password must contain at least one digit."),
                code='password_no_digit',
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)."),
                code='password_no_special',
            )

        # Check for common patterns
        common_patterns = [
            r'123456',
            r'password',
            r'qwerty',
            r'admin',
            r'letmein',
            r'welcome'
        ]
        
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                raise ValidationError(
                    _("Password contains common patterns that are not allowed."),
                    code='password_common_pattern',
                )

        # Check if password contains user information
        if user:
            user_info = [
                user.username.lower() if user.username else '',
                user.first_name.lower() if user.first_name else '',
                user.last_name.lower() if user.last_name else '',
                user.email.split('@')[0].lower() if user.email else ''
            ]
            
            for info in user_info:
                if info and len(info) > 3 and info in password.lower():
                    raise ValidationError(
                        _("Password cannot contain your personal information."),
                        code='password_contains_user_info',
                    )

    def get_help_text(self):
        return _(
            "Your password must be at least %(min_length)d characters long and contain "
            "at least one lowercase letter, one uppercase letter, one digit, and one "
            "special character (!@#$%^&*(),.?\":{}|<>)."
        ) % {'min_length': self.min_length}


def validate_username(username):
    """Validate username for security"""
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters long.")
    
    if len(username) > 30:
        raise ValidationError("Username must be 30 characters or less.")
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError("Username can only contain letters, numbers, and underscores.")
    
    # Prevent admin-like usernames
    forbidden_usernames = [
        'admin', 'administrator', 'root', 'superuser', 'user', 'test',
        'guest', 'anonymous', 'system', 'operator', 'manager'
    ]
    
    if username.lower() in forbidden_usernames:
        raise ValidationError("This username is not allowed.")


def validate_email(email):
    """Additional email validation"""
    if not email:
        raise ValidationError("Email is required.")
    
    # Basic email regex (Django handles most validation)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError("Enter a valid email address.")
    
    # Prevent disposable email domains (basic list)
    disposable_domains = [
        '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
        'mailinator.com', 'throwaway.email'
    ]
    
    domain = email.split('@')[1].lower()
    if domain in disposable_domains:
        raise ValidationError("Disposable email addresses are not allowed.")