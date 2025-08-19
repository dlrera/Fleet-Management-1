from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from authentication.permissions import AssetPermission, GranularAssetPermission
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponse
import csv
import io
from datetime import datetime
from .models import Asset, AssetDocument
from .serializers import (
    AssetSerializer, 
    AssetListSerializer, 
    AssetCreateUpdateSerializer,
    AssetDocumentSerializer
)


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all().prefetch_related('documents')
    # Use granular permissions if available, fallback to role-based
    permission_classes = [GranularAssetPermission]
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
    
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload an image for an asset"""
        asset = self.get_object()
        
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if image_file.content_type not in allowed_types:
            return Response(
                {'error': 'Invalid image type. Only JPEG, PNG, and WebP are allowed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 5MB)
        if image_file.size > 5242880:
            return Response(
                {'error': 'Image file size must be less than 5MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete old image files if they exist
        if asset.image:
            asset.image.delete(save=False)
        if asset.thumbnail:
            asset.thumbnail.delete(save=False)
        
        # Set new image and save (this will trigger image processing)
        asset.image = image_file
        asset.save()
        
        # Return success response with image URLs
        return Response({
            'message': 'Image uploaded successfully',
            'image': request.build_absolute_uri(asset.image.url) if asset.image else None,
            'thumbnail': request.build_absolute_uri(asset.thumbnail.url) if asset.thumbnail else None
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'])
    def delete_image(self, request, pk=None):
        """Delete the image and thumbnail for an asset"""
        asset = self.get_object()
        
        # Check if asset has an image
        if not asset.image and not asset.thumbnail:
            return Response(
                {'error': 'Asset has no image to delete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete image files
        if asset.image:
            asset.image.delete(save=False)
            asset.image = None
        if asset.thumbnail:
            asset.thumbnail.delete(save=False)
            asset.thumbnail = None
        
        # Save the asset
        asset.save()
        
        return Response({
            'message': 'Image deleted successfully'
        }, status=status.HTTP_200_OK)
    
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
    
    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """Import multiple assets from CSV file"""
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        csv_file = request.FILES['file']
        
        # Check file type
        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'File must be CSV format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check file size (limit to 5MB)
        if csv_file.size > 5242880:
            return Response(
                {'error': 'File size must be less than 5MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse CSV
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            # Validate required columns
            required_columns = ['asset_id', 'vehicle_type', 'make', 'model', 'year']
            if not all(col in reader.fieldnames for col in required_columns):
                missing = [col for col in required_columns if col not in reader.fieldnames]
                return Response(
                    {'error': f'Missing required columns: {", ".join(missing)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process rows
            success_count = 0
            error_rows = []
            created_assets = []
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        # Clean and validate data
                        asset_data = {
                            'asset_id': row.get('asset_id', '').strip(),
                            'vehicle_type': row.get('vehicle_type', '').strip().lower(),
                            'make': row.get('make', '').strip(),
                            'model': row.get('model', '').strip(),
                            'year': int(row.get('year', 0)),
                        }
                        
                        # Optional fields
                        if row.get('vin'):
                            asset_data['vin'] = row['vin'].strip()
                        if row.get('license_plate'):
                            asset_data['license_plate'] = row['license_plate'].strip()
                        if row.get('department'):
                            asset_data['department'] = row['department'].strip()
                        if row.get('status'):
                            asset_data['status'] = row['status'].strip().lower()
                        if row.get('current_odometer'):
                            asset_data['current_odometer'] = int(row['current_odometer'])
                        if row.get('purchase_date'):
                            asset_data['purchase_date'] = datetime.strptime(
                                row['purchase_date'], '%Y-%m-%d'
                            ).date()
                        if row.get('purchase_cost'):
                            asset_data['purchase_cost'] = float(row['purchase_cost'])
                        if row.get('notes'):
                            asset_data['notes'] = row['notes'].strip()
                        
                        # Validate vehicle type
                        valid_types = [choice[0] for choice in Asset.VEHICLE_TYPE_CHOICES]
                        if asset_data['vehicle_type'] not in valid_types:
                            raise ValueError(f"Invalid vehicle type: {asset_data['vehicle_type']}")
                        
                        # Validate status if provided
                        if 'status' in asset_data:
                            valid_statuses = [choice[0] for choice in Asset.STATUS_CHOICES]
                            if asset_data['status'] not in valid_statuses:
                                raise ValueError(f"Invalid status: {asset_data['status']}")
                        
                        # Check for duplicate asset_id
                        if Asset.objects.filter(asset_id=asset_data['asset_id']).exists():
                            raise ValueError(f"Asset ID '{asset_data['asset_id']}' already exists")
                        
                        # Create asset
                        serializer = AssetCreateUpdateSerializer(data=asset_data)
                        if serializer.is_valid():
                            asset = serializer.save()
                            created_assets.append(asset)
                            success_count += 1
                        else:
                            raise ValueError(str(serializer.errors))
                        
                    except Exception as e:
                        error_rows.append({
                            'row': row_num,
                            'asset_id': row.get('asset_id', 'N/A'),
                            'error': str(e)
                        })
            
            # Prepare response
            response_data = {
                'success_count': success_count,
                'error_count': len(error_rows),
                'total_rows': success_count + len(error_rows),
            }
            
            if error_rows:
                response_data['errors'] = error_rows
                
            # If all failed, return error status
            if success_count == 0 and error_rows:
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to process CSV file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def download_template(self, request):
        """Download CSV template for bulk import"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="assets_import_template.csv"'
        
        writer = csv.writer(response)
        
        # Write header with all available fields
        writer.writerow([
            'asset_id',
            'vehicle_type',
            'make',
            'model',
            'year',
            'vin',
            'license_plate',
            'department',
            'status',
            'current_odometer',
            'purchase_date',
            'purchase_cost',
            'notes'
        ])
        
        # Write sample data
        writer.writerow([
            'BUS-001',
            'bus',
            'Blue Bird',
            'Vision',
            '2022',
            '1BAKBCKA4NF123456',
            'ABC-1234',
            'Transportation',
            'active',
            '15000',
            '2022-01-15',
            '85000.00',
            'School bus for route A'
        ])
        
        writer.writerow([
            'TRK-001',
            'truck',
            'Ford',
            'F-150',
            '2021',
            '1FTFW1ET5MFC12345',
            'XYZ-5678',
            'Maintenance',
            'active',
            '25000',
            '2021-06-01',
            '45000.00',
            'Maintenance department truck'
        ])
        
        return response


class AssetDocumentViewSet(viewsets.ModelViewSet):
    queryset = AssetDocument.objects.all()
    serializer_class = AssetDocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['document_type', 'asset']
    search_fields = ['title', 'description', 'asset__asset_id']