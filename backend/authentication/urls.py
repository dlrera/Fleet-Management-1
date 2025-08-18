from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .user_views import UserManagementViewSet
from .audit_views import AuditLogViewSet

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='user-management')
router.register(r'audit', AuditLogViewSet, basename='audit-logs')

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.user_view, name='user'),
    path('check/', views.check_auth, name='check_auth'),
    path('manage/', include(router.urls)),  # User management endpoints
]