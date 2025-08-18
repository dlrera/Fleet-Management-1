from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from authentication.permissions import DriverPermission
from django.db.models import Q, Count
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
import csv
import io
from datetime import datetime, date, timedelta
from .models import Driver, DriverCertification, DriverAssetAssignment, DriverViolation
from .serializers import (
    DriverSerializer,
    DriverListSerializer,
    DriverCreateUpdateSerializer,
    DriverCertificationSerializer,
    DriverCertificationCreateUpdateSerializer,
    DriverAssetAssignmentSerializer,
    DriverAssetAssignmentCreateUpdateSerializer,
    DriverViolationSerializer
)


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all().prefetch_related(
        'certifications', 'asset_assignments__asset', 'violations'
    )
    permission_classes = [DriverPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employment_status', 'license_type', 'department', 'position']
    search_fields = ['driver_id', 'first_name', 'last_name', 'email', 'license_number']
    ordering_fields = ['driver_id', 'first_name', 'last_name', 'hire_date', 'license_expiration', 'created_at']
    ordering = ['driver_id']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DriverListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DriverCreateUpdateSerializer
        return DriverSerializer
    
    def get_queryset(self):
        queryset = Driver.objects.all().prefetch_related(
            'certifications', 'asset_assignments__asset', 'violations'
        )
        
        # Custom filtering for advanced search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(driver_id__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(license_number__icontains=search) |
                Q(department__icontains=search) |
                Q(position__icontains=search)
            )
        
        # Filter by license expiration status
        license_status = self.request.query_params.get('license_status', None)
        if license_status == 'expired':
            queryset = queryset.filter(license_expiration__lt=date.today())
        elif license_status == 'expiring_soon':
            thirty_days_from_now = date.today() + timedelta(days=30)
            queryset = queryset.filter(
                license_expiration__gte=date.today(),
                license_expiration__lte=thirty_days_from_now
            )
        
        # Filter by age range
        min_age = self.request.query_params.get('min_age', None)
        max_age = self.request.query_params.get('max_age', None)
        if min_age or max_age:
            today = date.today()
            if min_age:
                max_birth_date = today.replace(year=today.year - int(min_age))
                queryset = queryset.filter(date_of_birth__lte=max_birth_date)
            if max_age:
                min_birth_date = today.replace(year=today.year - int(max_age) - 1)
                queryset = queryset.filter(date_of_birth__gte=min_birth_date)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def certifications(self, request, pk=None):
        """Get all certifications for a driver"""
        driver = self.get_object()
        certifications = driver.certifications.all()
        serializer = DriverCertificationSerializer(certifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_certification(self, request, pk=None):
        """Add a certification for a driver"""
        driver = self.get_object()
        serializer = DriverCertificationCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(driver=driver)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def assignments(self, request, pk=None):
        """Get all asset assignments for a driver"""
        driver = self.get_object()
        assignments = driver.asset_assignments.all()
        serializer = DriverAssetAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_asset(self, request, pk=None):
        """Assign an asset to a driver"""
        driver = self.get_object()
        data = request.data.copy()
        data['driver'] = driver.id
        if 'assigned_date' not in data:
            data['assigned_date'] = timezone.now()
        
        serializer = DriverAssetAssignmentCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unassign_asset(self, request, pk=None):
        """Unassign an asset from a driver"""
        driver = self.get_object()
        asset_id = request.data.get('asset_id')
        
        if not asset_id:
            return Response(
                {'error': 'asset_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Handle multiple assignments for the same driver-asset pair
            assignments = driver.asset_assignments.filter(
                asset__id=asset_id,
                status='active',
                unassigned_date__isnull=True
            )
            
            if not assignments.exists():
                return Response(
                    {'error': 'Active assignment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Unassign all active assignments for this driver-asset pair
            updated_assignments = []
            for assignment in assignments:
                assignment.unassigned_date = timezone.now()
                assignment.status = 'completed'
                assignment.save()
                updated_assignments.append(assignment)
            
            # Return the first assignment data (or could return all)
            serializer = DriverAssetAssignmentSerializer(updated_assignments[0])
            return Response({
                'assignment': serializer.data,
                'unassigned_count': len(updated_assignments)
            })
        except DriverAssetAssignment.DoesNotExist:
            return Response(
                {'error': 'Active assignment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def violations(self, request, pk=None):
        """Get all violations for a driver"""
        driver = self.get_object()
        violations = driver.violations.all()
        serializer = DriverViolationSerializer(violations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        """Upload a profile photo for a driver"""
        driver = self.get_object()
        
        if 'photo' not in request.FILES:
            return Response(
                {'error': 'No photo file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photo_file = request.FILES['photo']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if photo_file.content_type not in allowed_types:
            return Response(
                {'error': 'Invalid image type. Only JPEG, PNG, and WebP are allowed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 2MB)
        if photo_file.size > 2097152:
            return Response(
                {'error': 'Photo file size must be less than 2MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete old photo if it exists
        if driver.profile_photo:
            driver.profile_photo.delete(save=False)
        
        # Set new photo and save (this will trigger photo processing)
        driver.profile_photo = photo_file
        driver.save()
        
        # Return success response with photo URL
        return Response({
            'message': 'Photo uploaded successfully',
            'photo': request.build_absolute_uri(driver.profile_photo.url) if driver.profile_photo else None
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'])
    def delete_photo(self, request, pk=None):
        """Delete the profile photo for a driver"""
        driver = self.get_object()
        
        # Check if driver has a photo
        if not driver.profile_photo:
            return Response(
                {'error': 'Driver has no photo to delete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete photo file
        driver.profile_photo.delete(save=False)
        driver.profile_photo = None
        
        # Save the driver
        driver.save()
        
        return Response({
            'message': 'Photo deleted successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get basic statistics about drivers"""
        total_drivers = Driver.objects.count()
        active_drivers = Driver.objects.filter(employment_status='active').count()
        inactive_drivers = Driver.objects.filter(employment_status='inactive').count()
        suspended_drivers = Driver.objects.filter(employment_status='suspended').count()
        
        # License statistics
        today = date.today()
        thirty_days_from_now = today + timedelta(days=30)
        expired_licenses = Driver.objects.filter(license_expiration__lt=today).count()
        expiring_licenses = Driver.objects.filter(
            license_expiration__gte=today,
            license_expiration__lte=thirty_days_from_now
        ).count()
        
        # License types
        license_types = {}
        for choice in Driver.LICENSE_TYPE_CHOICES:
            count = Driver.objects.filter(license_type=choice[0]).count()
            license_types[choice[1]] = count
        
        # Age statistics
        age_ranges = {
            '18-25': 0,
            '26-35': 0,
            '36-45': 0,
            '46-55': 0,
            '56-65': 0,
            '65+': 0
        }
        
        for driver in Driver.objects.all():
            age = driver.age
            if 18 <= age <= 25:
                age_ranges['18-25'] += 1
            elif 26 <= age <= 35:
                age_ranges['26-35'] += 1
            elif 36 <= age <= 45:
                age_ranges['36-45'] += 1
            elif 46 <= age <= 55:
                age_ranges['46-55'] += 1
            elif 56 <= age <= 65:
                age_ranges['56-65'] += 1
            else:
                age_ranges['65+'] += 1
        
        return Response({
            'total_drivers': total_drivers,
            'active_drivers': active_drivers,
            'inactive_drivers': inactive_drivers,
            'suspended_drivers': suspended_drivers,
            'expired_licenses': expired_licenses,
            'expiring_licenses': expiring_licenses,
            'license_types': license_types,
            'age_ranges': age_ranges
        })
    
    @action(detail=False, methods=['get'])
    def expiration_alerts(self, request):
        """Get drivers with expiring licenses or certifications"""
        days_ahead = int(request.query_params.get('days', 30))
        future_date = date.today() + timedelta(days=days_ahead)
        
        # Drivers with expiring licenses
        expiring_licenses = Driver.objects.filter(
            license_expiration__gte=date.today(),
            license_expiration__lte=future_date
        ).values('id', 'driver_id', 'first_name', 'last_name', 'license_expiration')
        
        # Drivers with expiring certifications
        expiring_certifications = Driver.objects.filter(
            certifications__expiration_date__gte=date.today(),
            certifications__expiration_date__lte=future_date
        ).distinct().values('id', 'driver_id', 'first_name', 'last_name')
        
        return Response({
            'expiring_licenses': list(expiring_licenses),
            'expiring_certifications': list(expiring_certifications),
            'days_ahead': days_ahead
        })
    
    @action(detail=False, methods=['get'])
    def available_drivers(self, request):
        """Get drivers available for assignment"""
        # Drivers who don't have active primary assignments
        available_drivers = Driver.objects.filter(
            employment_status='active'
        ).exclude(
            asset_assignments__assignment_type='primary',
            asset_assignments__status='active',
            asset_assignments__unassigned_date__isnull=True
        )
        
        serializer = DriverListSerializer(available_drivers, many=True)
        return Response(serializer.data)


class DriverCertificationViewSet(viewsets.ModelViewSet):
    queryset = DriverCertification.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['certification_type', 'status', 'driver']
    search_fields = ['certification_name', 'certification_number', 'issuing_authority']
    ordering_fields = ['issued_date', 'expiration_date', 'created_at']
    ordering = ['-expiration_date']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DriverCertificationCreateUpdateSerializer
        return DriverCertificationSerializer


class DriverAssetAssignmentViewSet(viewsets.ModelViewSet):
    queryset = DriverAssetAssignment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['assignment_type', 'status', 'driver', 'asset']
    search_fields = ['driver__driver_id', 'driver__first_name', 'driver__last_name', 'asset__asset_id']
    ordering_fields = ['assigned_date', 'unassigned_date', 'created_at']
    ordering = ['-assigned_date']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DriverAssetAssignmentCreateUpdateSerializer
        return DriverAssetAssignmentSerializer
    
    @action(detail=False, methods=['get'])
    def current_assignments(self, request):
        """Get all current active assignments"""
        assignments = self.queryset.filter(
            status='active',
            unassigned_date__isnull=True
        )
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)


class DriverViolationViewSet(viewsets.ModelViewSet):
    queryset = DriverViolation.objects.all()
    serializer_class = DriverViolationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['violation_type', 'severity', 'resolved', 'driver', 'asset']
    search_fields = ['description', 'citation_number', 'driver__driver_id']
    ordering_fields = ['violation_date', 'fine_amount', 'created_at']
    ordering = ['-violation_date']
