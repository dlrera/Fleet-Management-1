from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from datetime import date, timedelta

from .models import Department, Asset, AssetDocument, AssetImage
from .serializers import (
    DepartmentSerializer, AssetListSerializer, AssetDetailSerializer,
    AssetCreateUpdateSerializer, AssetDocumentSerializer, AssetImageSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department management"""
    
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class AssetViewSet(viewsets.ModelViewSet):
    """ViewSet for Asset management with comprehensive filtering and actions"""
    
    queryset = Asset.objects.select_related('department', 'created_by').prefetch_related('documents', 'images')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehicle_type', 'status', 'department', 'make', 'fuel_type']
    search_fields = ['asset_number', 'make', 'model', 'vin_number', 'license_plate']
    ordering_fields = ['asset_number', 'make', 'model', 'year', 'current_odometer_reading', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return AssetListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AssetCreateUpdateSerializer
        return AssetDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions and query parameters"""
        queryset = super().get_queryset()
        
        # Filter by expiration alerts
        if self.request.query_params.get('expiring_soon'):
            days_ahead = int(self.request.query_params.get('days_ahead', 30))
            future_date = date.today() + timedelta(days=days_ahead)
            
            queryset = queryset.filter(
                Q(insurance_expiry__lte=future_date) |
                Q(warranty_expiry__lte=future_date)
            )
        
        # Filter by service due - placeholder for future implementation
        # if self.request.query_params.get('service_due'):
        #     queryset = queryset.filter(next_service_due__lte=date.today())
        
        # Filter by age range
        min_age = self.request.query_params.get('min_age')
        max_age = self.request.query_params.get('max_age')
        if min_age or max_age:
            current_year = date.today().year
            if min_age:
                queryset = queryset.filter(year__lte=current_year - int(min_age))
            if max_age:
                queryset = queryset.filter(year__gte=current_year - int(max_age))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get asset statistics and metrics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_assets': queryset.count(),
            'active_assets': queryset.filter(status='active').count(),
            'maintenance_assets': queryset.filter(status='maintenance').count(),
            'out_of_service': queryset.filter(status='out_of_service').count(),
            'by_vehicle_type': list(queryset.values('vehicle_type').annotate(count=Count('vehicle_type'))),
            'by_department': list(queryset.select_related('department').values('department__name').annotate(count=Count('department__name'))),
            'average_age': queryset.aggregate(avg_age=Avg('year'))['avg_age'],
            'expiring_soon': self.get_expiring_assets_count(),
            'service_due': 0,  # Placeholder for future maintenance integration
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def expiring_documents(self, request):
        """Get assets with expiring documents"""
        days_ahead = int(request.query_params.get('days_ahead', 30))
        future_date = date.today() + timedelta(days=days_ahead)
        
        expiring_assets = self.get_queryset().filter(
            Q(insurance_expiry__lte=future_date) |
            Q(warranty_expiry__lte=future_date)
        )
        
        serializer = AssetListSerializer(expiring_assets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_document(self, request, pk=None):
        """Upload a document for an asset"""
        asset = self.get_object()
        serializer = AssetDocumentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(asset=asset, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        """Upload an image for an asset"""
        asset = self.get_object()
        serializer = AssetImageSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(asset=asset, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_odometer(self, request, pk=None):
        """Update odometer reading for an asset"""
        asset = self.get_object()
        new_reading = request.data.get('odometer_reading')
        
        if not new_reading:
            return Response({'error': 'odometer_reading is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_reading = int(new_reading)
            if new_reading < asset.current_odometer_reading:
                return Response({'error': 'New reading cannot be less than current reading'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            asset.current_odometer_reading = new_reading
            asset.save(update_fields=['current_odometer_reading', 'updated_at'])
            
            return Response({'message': 'Odometer updated successfully', 
                           'current_reading': asset.current_odometer_reading})
        
        except ValueError:
            return Response({'error': 'Invalid odometer reading'}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    def get_expiring_assets_count(self):
        """Helper method to count expiring assets"""
        future_date = date.today() + timedelta(days=30)
        return self.get_queryset().filter(
            Q(insurance_expiry__lte=future_date) |
            Q(warranty_expiry__lte=future_date)
        ).count()


class AssetDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for Asset Document management"""
    
    queryset = AssetDocument.objects.select_related('asset', 'uploaded_by')
    serializer_class = AssetDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'asset']
    search_fields = ['title', 'description']
    ordering = ['-uploaded_at']
    
    def perform_create(self, serializer):
        """Set the uploaded_by field to current user"""
        serializer.save(uploaded_by=self.request.user)


class AssetImageViewSet(viewsets.ModelViewSet):
    """ViewSet for Asset Image management"""
    
    queryset = AssetImage.objects.select_related('asset', 'uploaded_by')
    serializer_class = AssetImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['asset']
    ordering = ['-uploaded_at']
    
    def perform_create(self, serializer):
        """Set the uploaded_by field to current user"""
        serializer.save(uploaded_by=self.request.user)
