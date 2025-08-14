from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from datetime import date, timedelta

from .models import (
    MaintenanceType, MaintenanceSchedule, MaintenanceRecord,
    MaintenancePart, MaintenancePartUsage
)
from .serializers import (
    MaintenanceTypeSerializer, MaintenanceScheduleListSerializer,
    MaintenanceScheduleDetailSerializer, MaintenanceScheduleCreateUpdateSerializer,
    MaintenanceRecordListSerializer, MaintenanceRecordDetailSerializer,
    MaintenanceRecordCreateUpdateSerializer, MaintenancePartSerializer,
    MaintenancePartUsageSerializer
)


class MaintenanceTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for Maintenance Type management"""
    
    queryset = MaintenanceType.objects.all()
    serializer_class = MaintenanceTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'requires_technician', 'requires_parts', 'safety_critical']
    search_fields = ['name', 'description', 'instructions']
    ordering_fields = ['name', 'category', 'estimated_cost', 'created_at']
    ordering = ['category', 'name']


class MaintenanceScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for Maintenance Schedule management with comprehensive filtering"""
    
    queryset = MaintenanceSchedule.objects.select_related(
        'asset', 'maintenance_type', 'assigned_technician'
    ).prefetch_related('asset__department')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset', 'maintenance_type', 'interval_type', 'assigned_technician', 'is_active']
    search_fields = ['asset__asset_number', 'maintenance_type__name', 'vendor', 'notes']
    ordering_fields = ['asset__asset_number', 'maintenance_type__name', 'created_at']
    ordering = ['asset__asset_number']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return MaintenanceScheduleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return MaintenanceScheduleCreateUpdateSerializer
        return MaintenanceScheduleDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by due status
        if self.request.query_params.get('due_status'):
            status_filter = self.request.query_params.get('due_status')
            today = date.today()
            
            if status_filter == 'due':
                # Get schedules that are due today or overdue
                due_schedules = []
                for schedule in queryset:
                    if schedule.is_due:
                        due_schedules.append(schedule.schedule_id)
                queryset = queryset.filter(schedule_id__in=due_schedules)
                
            elif status_filter == 'overdue':
                # Get schedules that are overdue
                overdue_schedules = []
                for schedule in queryset:
                    if schedule.is_overdue:
                        overdue_schedules.append(schedule.schedule_id)
                queryset = queryset.filter(schedule_id__in=overdue_schedules)
                
            elif status_filter == 'upcoming':
                # Get schedules due within specified days
                days_ahead = int(self.request.query_params.get('days_ahead', 30))
                upcoming_schedules = []
                for schedule in queryset:
                    days_until_due = schedule.days_until_due
                    if days_until_due is not None and 0 < days_until_due <= days_ahead:
                        upcoming_schedules.append(schedule.schedule_id)
                queryset = queryset.filter(schedule_id__in=upcoming_schedules)
        
        # Filter by department
        if self.request.query_params.get('department'):
            department_id = self.request.query_params.get('department')
            queryset = queryset.filter(asset__department_id=department_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get maintenance schedule statistics"""
        queryset = self.get_queryset()
        
        # Calculate due/overdue counts
        due_count = 0
        overdue_count = 0
        upcoming_count = 0
        
        for schedule in queryset.filter(is_active=True):
            if schedule.is_overdue:
                overdue_count += 1
            elif schedule.is_due:
                due_count += 1
            else:
                days_until_due = schedule.days_until_due
                if days_until_due is not None and 0 < days_until_due <= 30:
                    upcoming_count += 1
        
        stats = {
            'total_schedules': queryset.count(),
            'active_schedules': queryset.filter(is_active=True).count(),
            'inactive_schedules': queryset.filter(is_active=False).count(),
            'due_today': due_count,
            'overdue': overdue_count,
            'upcoming_30_days': upcoming_count,
            'by_interval_type': list(queryset.values('interval_type').annotate(count=Count('interval_type'))),
            'by_maintenance_type': list(
                queryset.select_related('maintenance_type')
                .values('maintenance_type__name')
                .annotate(count=Count('maintenance_type__name'))[:10]
            ),
            'with_technician': queryset.filter(assigned_technician__isnull=False).count(),
            'without_technician': queryset.filter(assigned_technician__isnull=True).count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def due_maintenance(self, request):
        """Get maintenance schedules that are due or overdue"""
        days_ahead = int(request.query_params.get('days_ahead', 0))
        
        due_schedules = []
        overdue_schedules = []
        
        for schedule in self.get_queryset().filter(is_active=True):
            if schedule.is_overdue:
                overdue_schedules.append(schedule)
            elif schedule.is_due or (schedule.days_until_due is not None and schedule.days_until_due <= days_ahead):
                due_schedules.append(schedule)
        
        return Response({
            'due_schedules': MaintenanceScheduleListSerializer(due_schedules, many=True).data,
            'overdue_schedules': MaintenanceScheduleListSerializer(overdue_schedules, many=True).data,
        })


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for Maintenance Record management"""
    
    queryset = MaintenanceRecord.objects.select_related(
        'asset', 'maintenance_type', 'schedule', 'performed_by', 'work_order'
    ).prefetch_related('parts_used__part')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset', 'maintenance_type', 'status', 'performed_by', 'schedule']
    search_fields = ['asset__asset_number', 'maintenance_type__name', 'vendor', 'technician_notes']
    ordering_fields = ['service_date', 'completion_date', 'total_cost', 'created_at']
    ordering = ['-service_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return MaintenanceRecordListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return MaintenanceRecordCreateUpdateSerializer
        return MaintenanceRecordDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(service_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(service_date__lte=end_date)
        
        # Filter by cost range
        min_cost = self.request.query_params.get('min_cost')
        max_cost = self.request.query_params.get('max_cost')
        
        if min_cost:
            queryset = queryset.filter(
                labor_cost__gte=min_cost
            ) | queryset.filter(
                parts_cost__gte=min_cost
            ) | queryset.filter(
                external_cost__gte=min_cost
            )
        
        if max_cost:
            total_cost_filter = Q(labor_cost__lte=max_cost) & Q(parts_cost__lte=max_cost) & Q(external_cost__lte=max_cost)
            queryset = queryset.filter(total_cost_filter)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get maintenance record statistics"""
        queryset = self.get_queryset()
        
        # Date range for recent stats
        thirty_days_ago = date.today() - timedelta(days=30)
        year_ago = date.today() - timedelta(days=365)
        
        recent_records = queryset.filter(service_date__gte=thirty_days_ago)
        yearly_records = queryset.filter(service_date__gte=year_ago)
        
        stats = {
            'total_records': queryset.count(),
            'completed_records': queryset.filter(status='completed').count(),
            'in_progress_records': queryset.filter(status='in_progress').count(),
            'scheduled_records': queryset.filter(status='scheduled').count(),
            'records_last_30_days': recent_records.count(),
            'records_last_year': yearly_records.count(),
            'total_cost_30_days': recent_records.aggregate(
                total=Sum('labor_cost') + Sum('parts_cost') + Sum('external_cost')
            )['total'] or 0,
            'total_cost_year': yearly_records.aggregate(
                total=Sum('labor_cost') + Sum('parts_cost') + Sum('external_cost')
            )['total'] or 0,
            'average_cost': queryset.aggregate(
                avg_labor=Avg('labor_cost'),
                avg_parts=Avg('parts_cost'),
                avg_external=Avg('external_cost')
            ),
            'by_maintenance_type': list(
                queryset.select_related('maintenance_type')
                .values('maintenance_type__name')
                .annotate(count=Count('maintenance_type__name'))[:10]
            ),
            'by_status': list(queryset.values('status').annotate(count=Count('status'))),
            'average_rating': queryset.filter(quality_rating__isnull=False).aggregate(
                avg_rating=Avg('quality_rating')
            )['avg_rating'],
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def cost_analysis(self, request):
        """Get cost analysis for maintenance records"""
        queryset = self.get_queryset()
        
        # Monthly cost breakdown
        monthly_costs = {}
        for record in queryset.filter(service_date__gte=date.today() - timedelta(days=365)):
            month_key = record.service_date.strftime('%Y-%m')
            if month_key not in monthly_costs:
                monthly_costs[month_key] = {'labor': 0, 'parts': 0, 'external': 0, 'total': 0}
            
            monthly_costs[month_key]['labor'] += float(record.labor_cost)
            monthly_costs[month_key]['parts'] += float(record.parts_cost)
            monthly_costs[month_key]['external'] += float(record.external_cost)
            monthly_costs[month_key]['total'] += float(record.total_cost)
        
        return Response({
            'monthly_costs': monthly_costs,
            'cost_by_asset': list(
                queryset.select_related('asset')
                .values('asset__asset_number')
                .annotate(total_cost=Sum('labor_cost') + Sum('parts_cost') + Sum('external_cost'))
                .order_by('-total_cost')[:10]
            ),
            'cost_by_type': list(
                queryset.select_related('maintenance_type')
                .values('maintenance_type__name')
                .annotate(total_cost=Sum('labor_cost') + Sum('parts_cost') + Sum('external_cost'))
                .order_by('-total_cost')[:10]
            ),
        })


class MaintenancePartViewSet(viewsets.ModelViewSet):
    """ViewSet for Maintenance Part management"""
    
    queryset = MaintenancePart.objects.prefetch_related('compatible_assets')
    serializer_class = MaintenancePartSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'compatible_assets']
    search_fields = ['part_number', 'part_name', 'description', 'manufacturer']
    ordering_fields = ['part_number', 'part_name', 'unit_cost', 'stock_quantity', 'created_at']
    ordering = ['part_number']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by stock status
        if self.request.query_params.get('low_stock'):
            low_stock_ids = [part.id for part in queryset if part.is_low_stock]
            queryset = queryset.filter(id__in=low_stock_ids)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def low_stock_alerts(self, request):
        """Get parts with low stock levels"""
        low_stock_parts = [part for part in self.get_queryset() if part.is_low_stock]
        serializer = MaintenancePartSerializer(low_stock_parts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inventory_summary(self, request):
        """Get inventory summary statistics"""
        queryset = self.get_queryset()
        
        total_value = sum(part.unit_cost * part.stock_quantity for part in queryset)
        low_stock_count = sum(1 for part in queryset if part.is_low_stock)
        
        stats = {
            'total_parts': queryset.count(),
            'total_inventory_value': total_value,
            'low_stock_parts': low_stock_count,
            'out_of_stock_parts': queryset.filter(stock_quantity=0).count(),
            'by_manufacturer': list(
                queryset.values('manufacturer')
                .annotate(count=Count('manufacturer'))
                .order_by('-count')[:10]
            ),
            'highest_value_parts': list(
                queryset.order_by('-unit_cost')[:10]
                .values('part_number', 'part_name', 'unit_cost', 'stock_quantity')
            ),
        }
        
        return Response(stats)


class MaintenancePartUsageViewSet(viewsets.ModelViewSet):
    """ViewSet for Maintenance Part Usage tracking"""
    
    queryset = MaintenancePartUsage.objects.select_related('maintenance_record', 'part')
    serializer_class = MaintenancePartUsageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['maintenance_record', 'part']
    search_fields = ['part__part_number', 'part__part_name', 'notes']
    ordering = ['-created_at']
