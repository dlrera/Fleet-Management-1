from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from datetime import date, timedelta

from .models import Driver, DriverCertification, DriverIncident, DriverTraining
from .serializers import (
    DriverListSerializer, DriverDetailSerializer, DriverCreateUpdateSerializer,
    DriverCertificationSerializer, DriverIncidentSerializer, DriverTrainingSerializer
)


class DriverViewSet(viewsets.ModelViewSet):
    """ViewSet for Driver management with comprehensive filtering and actions"""
    
    queryset = Driver.objects.select_related('user').prefetch_related(
        'certifications', 'incidents', 'training_records', 'assigned_vehicles'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employment_status', 'license_class']
    search_fields = ['user__first_name', 'user__last_name', 'license_number', 'phone_number']
    ordering_fields = ['user__last_name', 'hire_date', 'license_expiry_date', 'created_at']
    ordering = ['user__last_name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return DriverListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DriverCreateUpdateSerializer
        return DriverDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by license expiry
        if self.request.query_params.get('license_expiring'):
            days_ahead = int(self.request.query_params.get('days_ahead', 30))
            future_date = date.today() + timedelta(days=days_ahead)
            queryset = queryset.filter(license_expiry_date__lte=future_date)
        
        # Filter by recent incidents
        if self.request.query_params.get('recent_incidents'):
            days_back = int(self.request.query_params.get('days_back', 365))
            past_date = date.today() - timedelta(days=days_back)
            driver_ids = DriverIncident.objects.filter(
                incident_date__gte=past_date
            ).values_list('driver_id', flat=True).distinct()
            queryset = queryset.filter(driver_id__in=driver_ids)
        
        # Filter by certification expiry
        if self.request.query_params.get('cert_expiring'):
            days_ahead = int(self.request.query_params.get('days_ahead', 30))
            future_date = date.today() + timedelta(days=days_ahead)
            driver_ids = DriverCertification.objects.filter(
                expiry_date__lte=future_date
            ).values_list('driver_id', flat=True).distinct()
            queryset = queryset.filter(driver_id__in=driver_ids)
        
        # Filter by vehicle assignment
        if self.request.query_params.get('has_vehicle'):
            has_vehicle = self.request.query_params.get('has_vehicle').lower() == 'true'
            if has_vehicle:
                queryset = queryset.filter(assigned_vehicles__isnull=False).distinct()
            else:
                queryset = queryset.filter(assigned_vehicles__isnull=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get driver statistics and metrics"""
        queryset = self.get_queryset()
        
        # License expiry stats
        today = date.today()
        future_30 = today + timedelta(days=30)
        future_60 = today + timedelta(days=60)
        
        stats = {
            'total_drivers': queryset.count(),
            'active_drivers': queryset.filter(employment_status='active').count(),
            'inactive_drivers': queryset.filter(employment_status='inactive').count(),
            'on_leave_drivers': queryset.filter(employment_status='on_leave').count(),
            'terminated_drivers': queryset.filter(employment_status='terminated').count(),
            'licenses_expired': queryset.filter(license_expiry_date__lt=today).count(),
            'licenses_expiring_30_days': queryset.filter(
                license_expiry_date__gte=today,
                license_expiry_date__lte=future_30
            ).count(),
            'licenses_expiring_60_days': queryset.filter(
                license_expiry_date__gte=today,
                license_expiry_date__lte=future_60
            ).count(),
            'drivers_with_vehicles': queryset.filter(assigned_vehicles__isnull=False).distinct().count(),
            'drivers_without_vehicles': queryset.filter(assigned_vehicles__isnull=True).count(),
            'average_safety_rating': queryset.aggregate(avg_rating=Avg('safety_rating'))['avg_rating'],
        }
        
        # Incident stats
        recent_incidents = DriverIncident.objects.filter(
            incident_date__gte=today - timedelta(days=365)
        ).count()
        stats['incidents_last_year'] = recent_incidents
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def license_alerts(self, request):
        """Get drivers with license-related alerts"""
        days_ahead = int(request.query_params.get('days_ahead', 30))
        future_date = date.today() + timedelta(days=days_ahead)
        
        expiring_drivers = self.get_queryset().filter(
            license_expiry_date__lte=future_date,
            license_expiry_date__gte=date.today()
        )
        
        expired_drivers = self.get_queryset().filter(
            license_expiry_date__lt=date.today()
        )
        
        return Response({
            'expiring_licenses': DriverListSerializer(expiring_drivers, many=True).data,
            'expired_licenses': DriverListSerializer(expired_drivers, many=True).data,
        })
    
    @action(detail=False, methods=['get'])
    def certification_alerts(self, request):
        """Get drivers with expiring certifications"""
        days_ahead = int(request.query_params.get('days_ahead', 30))
        future_date = date.today() + timedelta(days=days_ahead)
        
        expiring_certs = DriverCertification.objects.filter(
            expiry_date__lte=future_date,
            expiry_date__gte=date.today()
        ).select_related('driver__user')
        
        expired_certs = DriverCertification.objects.filter(
            expiry_date__lt=date.today()
        ).select_related('driver__user')
        
        return Response({
            'expiring_certifications': DriverCertificationSerializer(expiring_certs, many=True).data,
            'expired_certifications': DriverCertificationSerializer(expired_certs, many=True).data,
        })
    
    @action(detail=True, methods=['get'])
    def safety_report(self, request, pk=None):
        """Get safety report for a specific driver"""
        driver = self.get_object()
        
        # Get incidents by year
        incidents_by_year = {}
        for incident in driver.driver_incidents.all():
            year = incident.incident_date.year
            if year not in incidents_by_year:
                incidents_by_year[year] = 0
            incidents_by_year[year] += 1
        
        # Get recent training
        recent_training = driver.driver_training.filter(
            completion_date__gte=date.today() - timedelta(days=365)
        ).order_by('-completion_date')
        
        return Response({
            'driver_id': str(driver.driver_id),
            'safety_rating': driver.safety_rating,
            'total_incidents': driver.driver_incidents.count(),
            'incidents_by_year': incidents_by_year,
            'recent_incidents': DriverIncidentSerializer(
                driver.driver_incidents.filter(
                    incident_date__gte=date.today() - timedelta(days=365)
                ).order_by('-incident_date'), many=True
            ).data,
            'recent_training': DriverTrainingSerializer(recent_training, many=True).data,
            'last_training_date': recent_training.first().completion_date if recent_training.exists() else None,
        })


class DriverCertificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Driver Certification management"""
    
    queryset = DriverCertification.objects.select_related('driver__user')
    serializer_class = DriverCertificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['driver', 'certification_name', 'issuing_authority']
    search_fields = ['certification_name', 'issuing_authority', 'certification_number']
    ordering = ['-issue_date']
    
    def perform_create(self, serializer):
        """Auto-assign driver if not provided"""
        if not serializer.validated_data.get('driver'):
            driver_id = self.request.data.get('driver_id')
            if driver_id:
                serializer.save(driver_id=driver_id)
        else:
            serializer.save()


class DriverIncidentViewSet(viewsets.ModelViewSet):
    """ViewSet for Driver Incident management"""
    
    queryset = DriverIncident.objects.select_related('driver__user')
    serializer_class = DriverIncidentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['driver', 'incident_type', 'severity', 'fault_determination']
    search_fields = ['location', 'description', 'police_report_number']
    ordering = ['-incident_date']
    
    def perform_create(self, serializer):
        """Auto-assign driver if not provided"""
        if not serializer.validated_data.get('driver'):
            driver_id = self.request.data.get('driver_id')
            if driver_id:
                serializer.save(driver_id=driver_id)
        else:
            serializer.save()


class DriverTrainingViewSet(viewsets.ModelViewSet):
    """ViewSet for Driver Training management"""
    
    queryset = DriverTraining.objects.select_related('driver__user')
    serializer_class = DriverTrainingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['driver', 'training_type', 'provider']
    search_fields = ['training_name', 'provider', 'certificate_number']
    ordering = ['-completion_date']
    
    def perform_create(self, serializer):
        """Auto-assign driver if not provided"""
        if not serializer.validated_data.get('driver'):
            driver_id = self.request.data.get('driver_id')
            if driver_id:
                serializer.save(driver_id=driver_id)
        else:
            serializer.save()
