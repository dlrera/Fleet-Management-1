from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Asset, AssetDocument
from .serializers import (
    AssetSerializer, 
    AssetListSerializer, 
    AssetCreateUpdateSerializer,
    AssetDocumentSerializer
)


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all().prefetch_related('documents')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehicle_type', 'status', 'department', 'year']
    search_fields = ['asset_id', 'make', 'model', 'vin', 'license_plate']
    ordering_fields = ['asset_id', 'make', 'model', 'year', 'current_odometer', 'created_at']
    ordering = ['asset_id']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AssetCreateUpdateSerializer
        return AssetSerializer
    
    def get_queryset(self):
        queryset = Asset.objects.all().prefetch_related('documents')
        
        # Custom filtering for advanced search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(asset_id__icontains=search) |
                Q(make__icontains=search) |
                Q(model__icontains=search) |
                Q(vin__icontains=search) |
                Q(license_plate__icontains=search) |
                Q(department__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get all documents for an asset"""
        asset = self.get_object()
        documents = asset.documents.all()
        serializer = AssetDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        """Upload a document for an asset"""
        asset = self.get_object()
        serializer = AssetDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(asset=asset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get basic statistics about assets"""
        total_assets = Asset.objects.count()
        active_assets = Asset.objects.filter(status='active').count()
        maintenance_assets = Asset.objects.filter(status='maintenance').count()
        retired_assets = Asset.objects.filter(status='retired').count()
        
        vehicle_types = {}
        for choice in Asset.VEHICLE_TYPE_CHOICES:
            count = Asset.objects.filter(vehicle_type=choice[0]).count()
            vehicle_types[choice[1]] = count
        
        return Response({
            'total_assets': total_assets,
            'active_assets': active_assets,
            'maintenance_assets': maintenance_assets,
            'retired_assets': retired_assets,
            'vehicle_types': vehicle_types
        })


class AssetDocumentViewSet(viewsets.ModelViewSet):
    queryset = AssetDocument.objects.all()
    serializer_class = AssetDocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['document_type', 'asset']
    search_fields = ['title', 'description', 'asset__asset_id']