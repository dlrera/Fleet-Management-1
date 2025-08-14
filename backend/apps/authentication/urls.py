from django.urls import path
from .views import (
    RegisterView,
    login_view,
    logout_view,
    user_profile_view,
    update_profile_view,
    change_password_view,
    check_auth_view
)

app_name = 'authentication'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', user_profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update_profile'),
    path('change-password/', change_password_view, name='change_password'),
    path('check-auth/', check_auth_view, name='check_auth'),
]