from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Sum, Count, Q, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import io
from decimal import Decimal

from .models import FuelTransaction, FuelSite, FuelCard, FuelAlert, UnitsPolicy
from .serializers import (
    FuelTransactionListSerializer, FuelTransactionDetailSerializer,
    FuelTransactionCreateUpdateSerializer, FuelSiteSerializer, FuelCardSerializer,
    FuelAlertSerializer, UnitsPolicySerializer, FuelStatsSerializer,
    FuelImportPreviewSerializer
)
from assets.models import Asset


class FuelTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for fuel transactions with full CRUD operations"""
    
    queryset = FuelTransaction.objects.select_related(
        'asset', 'fuel_site', 'created_by'
    ).prefetch_related('alerts')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtering
    filterset_fields = {
        'asset': ['exact'],
        'product_type': ['exact', 'in'],
        'entry_source': ['exact', 'in'],
        'timestamp': ['gte', 'lte', 'date'],
        'total_cost': ['gte', 'lte'],
        'mpg': ['gte', 'lte'],
        'created_at': ['gte', 'lte', 'date'],
    }
    
    # Searching
    search_fields = [
        'asset__asset_id', 'vendor', 'location_label', 'payment_ref', 'notes'
    ]
    
    # Ordering
    ordering_fields = [
        'timestamp', 'total_cost', 'volume', 'mpg', 'cost_per_mile', 'created_at'
    ]
    ordering = ['-timestamp']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return FuelTransactionListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return FuelTransactionCreateUpdateSerializer
        else:
            return FuelTransactionDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions and query params"""
        queryset = self.queryset
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__lte=end_date)
            except ValueError:
                pass
        
        # Filter by anomalies if requested
        anomalies_only = self.request.query_params.get('anomalies_only')
        if anomalies_only and anomalies_only.lower() == 'true':
            # This would need to be optimized with database-level filtering
            # For now, we'll return all and filter in the serializer
            pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get fuel consumption statistics"""
        # Get date range for stats
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Filter by asset if specified
        asset_id = request.query_params.get('asset_id')
        queryset = self.get_queryset().filter(timestamp__date__gte=start_date)
        
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
        
        # Calculate statistics
        stats = queryset.aggregate(
            total_transactions=Count('id'),
            total_volume=Sum('volume'),
            total_cost=Sum('total_cost'),
            average_mpg=Avg('mpg'),
            average_cost_per_mile=Avg('cost_per_mile'),
        )
        
        # Product breakdown
        product_breakdown = {}
        for product in queryset.values('product_type').annotate(
            count=Count('id'),
            volume=Sum('volume'),
            cost=Sum('total_cost')
        ):
            product_breakdown[product['product_type']] = {
                'count': product['count'],
                'volume': product['volume'] or 0,
                'cost': product['cost'] or 0
            }
        
        # Monthly trends (last 12 months)
        monthly_trends = []
        for i in range(12):
            month_start = (timezone.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_data = queryset.filter(
                timestamp__date__gte=month_start,
                timestamp__date__lte=month_end
            ).aggregate(
                volume=Sum('volume'),
                cost=Sum('total_cost'),
                transactions=Count('id')
            )
            
            monthly_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'volume': month_data['volume'] or 0,
                'cost': month_data['cost'] or 0,
                'transactions': month_data['transactions'] or 0
            })
        
        # Alert counts
        alert_counts = FuelAlert.objects.filter(
            transaction__in=queryset,
            status='open'
        ).aggregate(
            open_alerts=Count('id'),
            critical_alerts=Count('id', filter=Q(severity='critical'))
        )
        
        # Most/least efficient assets
        asset_efficiency = queryset.filter(mpg__isnull=False).values(
            'asset_id', 'asset__asset_id'
        ).annotate(
            avg_mpg=Avg('mpg'),
            transaction_count=Count('id')
        ).filter(transaction_count__gte=3).order_by('-avg_mpg')
        
        stats_data = {
            **stats,
            'product_breakdown': product_breakdown,
            'monthly_trends': monthly_trends,
            'open_alerts': alert_counts['open_alerts'] or 0,
            'critical_alerts': alert_counts['critical_alerts'] or 0,
            'most_efficient_assets': list(asset_efficiency[:5]),
            'least_efficient_assets': list(asset_efficiency.reverse()[:5])
        }
        
        serializer = FuelStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create fuel transactions"""
        if not isinstance(request.data, list):
            return Response(
                {'error': 'Expected a list of fuel transactions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = FuelTransactionCreateUpdateSerializer(
            data=request.data, many=True, context={'request': request}
        )
        
        if serializer.is_valid():
            transactions = serializer.save()
            response_serializer = FuelTransactionListSerializer(transactions, many=True)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """Import fuel transactions from CSV file"""
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response(
                {'error': 'No CSV file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Read and parse CSV
        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            
            preview_only = request.data.get('preview_only', 'false').lower() == 'true'
            
            valid_rows = []
            invalid_rows = []
            errors = {}
            
            for row_num, row in enumerate(csv_data, 1):
                try:
                    # Map CSV columns to model fields
                    # This is a basic mapping - could be made configurable
                    transaction_data = {
                        'asset': Asset.objects.get(asset_id=row.get('Asset ID')).id,
                        'timestamp': datetime.strptime(row.get('Date'), '%Y-%m-%d'),
                        'product_type': row.get('Product Type', '').lower(),
                        'volume': Decimal(row.get('Volume', '0')),
                        'unit': row.get('Unit', 'gal').lower(),
                        'total_cost': Decimal(row.get('Total Cost', '0')),
                        'odometer': Decimal(row.get('Odometer', '0')) if row.get('Odometer') else None,
                        'vendor': row.get('Vendor', ''),
                        'location_label': row.get('Location', ''),
                        'entry_source': 'csv_import'
                    }
                    
                    if preview_only:
                        valid_rows.append(transaction_data)
                    else:
                        serializer = FuelTransactionCreateUpdateSerializer(
                            data=transaction_data, context={'request': request}
                        )
                        if serializer.is_valid():
                            serializer.save()
                            valid_rows.append(transaction_data)
                        else:
                            invalid_rows.append(row)
                            errors[row_num] = serializer.errors
                
                except Exception as e:
                    invalid_rows.append(row)
                    errors[row_num] = str(e)
            
            if preview_only:
                preview_data = {
                    'total_rows': len(valid_rows) + len(invalid_rows),
                    'valid_rows': len(valid_rows),
                    'invalid_rows': len(invalid_rows),
                    'duplicates': 0,  # Would need dedup logic
                    'sample_valid': valid_rows[:5],
                    'sample_invalid': invalid_rows[:5],
                    'errors': errors,
                    'warnings': {},
                    'column_mapping': {
                        'Asset ID': 'asset',
                        'Date': 'timestamp',
                        'Product Type': 'product_type',
                        'Volume': 'volume',
                        'Unit': 'unit',
                        'Total Cost': 'total_cost',
                        'Odometer': 'odometer',
                        'Vendor': 'vendor',
                        'Location': 'location_label'
                    },
                    'required_columns': ['Asset ID', 'Date', 'Product Type', 'Volume'],
                    'optional_columns': ['Unit', 'Total Cost', 'Odometer', 'Vendor', 'Location']
                }
                
                serializer = FuelImportPreviewSerializer(preview_data)
                return Response(serializer.data)
            
            else:
                return Response({
                    'message': f'Imported {len(valid_rows)} transactions successfully',
                    'valid_rows': len(valid_rows),
                    'invalid_rows': len(invalid_rows),
                    'errors': errors
                }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': f'Failed to process CSV: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class FuelSiteViewSet(viewsets.ModelViewSet):
    """ViewSet for fuel sites"""
    
    queryset = FuelSite.objects.all()
    serializer_class = FuelSiteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['site_type', 'controller_type']
    search_fields = ['name', 'address', 'external_id']
    ordering_fields = ['name', 'site_type', 'created_at']
    ordering = ['name']


class FuelCardViewSet(viewsets.ModelViewSet):
    """ViewSet for fuel cards"""
    
    queryset = FuelCard.objects.select_related('assigned_asset')
    serializer_class = FuelCardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['provider', 'status', 'assigned_asset']
    search_fields = ['card_last4', 'external_id']
    ordering_fields = ['provider', 'card_last4', 'status', 'created_at']
    ordering = ['provider', 'card_last4']


class FuelAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for fuel alerts"""
    
    queryset = FuelAlert.objects.select_related(
        'asset', 'transaction', 'resolved_by'
    )
    serializer_class = FuelAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = {
        'alert_type': ['exact', 'in'],
        'severity': ['exact', 'in'],
        'status': ['exact', 'in'],
        'asset': ['exact'],
        'created_at': ['gte', 'lte', 'date'],
    }
    search_fields = ['title', 'description', 'asset__asset_id']
    ordering_fields = ['created_at', 'severity', 'status', 'alert_type']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        
        if alert.status == 'resolved':
            return Response(
                {'error': 'Alert is already resolved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resolution_notes = request.data.get('resolution_notes', '')
        mark_as = request.data.get('status', 'resolved')  # resolved or false_positive
        
        if mark_as not in ['resolved', 'false_positive']:
            return Response(
                {'error': 'Status must be "resolved" or "false_positive"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.status = mark_as
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.resolution_notes = resolution_notes
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        
        if alert.status != 'open':
            return Response(
                {'error': 'Can only acknowledge open alerts'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.status = 'acknowledged'
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)


class UnitsPolicyViewSet(viewsets.ModelViewSet):
    """ViewSet for units policy"""
    
    queryset = UnitsPolicy.objects.all()
    serializer_class = UnitsPolicySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current units policy (singleton)"""
        policy, created = UnitsPolicy.objects.get_or_create(
            defaults={
                'distance_unit': 'mi',
                'volume_unit': 'gal',
                'currency': 'USD'
            }
        )
        
        serializer = self.get_serializer(policy)
        return Response(serializer.data)