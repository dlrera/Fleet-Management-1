from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import date, timedelta

from .models import (
    WorkOrder, WorkOrderPhoto, WorkOrderDocument, WorkOrderComment,
    WorkOrderStatusHistory, WorkOrderChecklist, WorkOrderChecklistItem
)
from .serializers import (
    WorkOrderListSerializer, WorkOrderDetailSerializer, WorkOrderCreateUpdateSerializer,
    WorkOrderStatusUpdateSerializer, WorkOrderPhotoSerializer, WorkOrderDocumentSerializer,
    WorkOrderCommentSerializer, WorkOrderChecklistSerializer, WorkOrderChecklistItemSerializer
)


class WorkOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Work Order management with comprehensive functionality"""
    
    queryset = WorkOrder.objects.select_related(
        'asset', 'created_by', 'assigned_to', 'department', 'maintenance_record'
    ).prefetch_related(
        'photos', 'documents', 'comments', 'status_history', 'checklists__items'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'work_type', 'asset', 'assigned_to', 'department']
    search_fields = ['work_order_number', 'title', 'description', 'asset__asset_number']
    ordering_fields = ['work_order_number', 'created_at', 'requested_completion_date', 
                      'priority', 'status', 'progress_percentage']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return WorkOrderListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return WorkOrderCreateUpdateSerializer
        elif self.action == 'update_status':
            return WorkOrderStatusUpdateSerializer
        return WorkOrderDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by due status
        if self.request.query_params.get('due_status'):
            status_filter = self.request.query_params.get('due_status')
            today = date.today()
            
            if status_filter == 'overdue':
                queryset = queryset.filter(
                    requested_completion_date__lt=today,
                    status__in=['open', 'assigned', 'in_progress', 'on_hold']
                )
            elif status_filter == 'due_today':
                queryset = queryset.filter(
                    requested_completion_date=today,
                    status__in=['open', 'assigned', 'in_progress', 'on_hold']
                )
            elif status_filter == 'due_this_week':
                week_end = today + timedelta(days=7)
                queryset = queryset.filter(
                    requested_completion_date__gte=today,
                    requested_completion_date__lte=week_end,
                    status__in=['open', 'assigned', 'in_progress', 'on_hold']
                )
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        # Filter by cost range
        min_cost = self.request.query_params.get('min_cost')
        max_cost = self.request.query_params.get('max_cost')
        
        if min_cost:
            queryset = queryset.filter(
                Q(labor_cost__gte=min_cost) |
                Q(parts_cost__gte=min_cost) |
                Q(external_cost__gte=min_cost)
            )
        
        if max_cost:
            # Filter where total cost is less than max_cost
            total_cost_subquery = queryset.extra(
                select={
                    'total_calculated': 'labor_cost + parts_cost + external_cost'
                }
            ).filter(total_calculated__lte=max_cost)
            queryset = total_cost_subquery
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get work order statistics and metrics"""
        queryset = self.get_queryset()
        
        # Status counts
        status_counts = {}
        for status_choice in WorkOrder.STATUS_CHOICES:
            status_counts[status_choice[0]] = queryset.filter(status=status_choice[0]).count()
        
        # Priority counts
        priority_counts = {}
        for priority_choice in WorkOrder.PRIORITY_CHOICES:
            priority_counts[priority_choice[0]] = queryset.filter(priority=priority_choice[0]).count()
        
        # Due date statistics
        today = date.today()
        overdue_count = queryset.filter(
            requested_completion_date__lt=today,
            status__in=['open', 'assigned', 'in_progress', 'on_hold']
        ).count()
        
        due_today_count = queryset.filter(
            requested_completion_date=today,
            status__in=['open', 'assigned', 'in_progress', 'on_hold']
        ).count()
        
        due_this_week = queryset.filter(
            requested_completion_date__gte=today,
            requested_completion_date__lte=today + timedelta(days=7),
            status__in=['open', 'assigned', 'in_progress', 'on_hold']
        ).count()
        
        # Cost statistics
        cost_stats = queryset.aggregate(
            total_labor_cost=Sum('labor_cost'),
            total_parts_cost=Sum('parts_cost'),
            total_external_cost=Sum('external_cost'),
            avg_labor_cost=Avg('labor_cost'),
            avg_parts_cost=Avg('parts_cost'),
            avg_external_cost=Avg('external_cost'),
            avg_progress=Avg('progress_percentage')
        )
        
        stats = {
            'total_work_orders': queryset.count(),
            'status_counts': status_counts,
            'priority_counts': priority_counts,
            'overdue_count': overdue_count,
            'due_today_count': due_today_count,
            'due_this_week_count': due_this_week,
            'cost_statistics': cost_stats,
            'by_work_type': list(queryset.values('work_type').annotate(count=Count('work_type'))),
            'by_department': list(
                queryset.select_related('department')
                .values('department__name')
                .annotate(count=Count('department__name'))[:10]
            ),
            'assigned_vs_unassigned': {
                'assigned': queryset.filter(assigned_to__isnull=False).count(),
                'unassigned': queryset.filter(assigned_to__isnull=True).count()
            }
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard data for work orders"""
        queryset = self.get_queryset()
        today = date.today()
        
        # Recent work orders
        recent_orders = queryset.order_by('-created_at')[:10]
        
        # High priority overdue orders
        high_priority_overdue = queryset.filter(
            priority__in=['high', 'critical', 'emergency'],
            requested_completion_date__lt=today,
            status__in=['open', 'assigned', 'in_progress', 'on_hold']
        ).order_by('requested_completion_date')[:5]
        
        # Work orders by status for current user
        user_orders = queryset.filter(assigned_to=request.user)
        user_status_counts = {}
        for status_choice in WorkOrder.STATUS_CHOICES:
            user_status_counts[status_choice[0]] = user_orders.filter(status=status_choice[0]).count()
        
        return Response({
            'recent_orders': WorkOrderListSerializer(recent_orders, many=True).data,
            'high_priority_overdue': WorkOrderListSerializer(high_priority_overdue, many=True).data,
            'user_assigned_counts': user_status_counts,
            'quick_stats': {
                'total_open': queryset.filter(status='open').count(),
                'assigned_to_me': user_orders.count(),
                'overdue': queryset.filter(
                    requested_completion_date__lt=today,
                    status__in=['open', 'assigned', 'in_progress', 'on_hold']
                ).count(),
                'completed_this_month': queryset.filter(
                    completed_at__month=today.month,
                    completed_at__year=today.year
                ).count()
            }
        })
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update work order status with history tracking"""
        work_order = self.get_object()
        serializer = WorkOrderStatusUpdateSerializer(
            data=request.data, 
            context={'work_order': work_order}
        )
        
        if serializer.is_valid():
            old_status = work_order.status
            new_status = serializer.validated_data['new_status']
            reason = serializer.validated_data.get('reason', '')
            assigned_to = serializer.validated_data.get('assigned_to')
            
            # Update work order
            work_order.status = new_status
            
            # Set timestamps based on status
            now = timezone.now()
            if new_status == 'assigned' and not work_order.assigned_at:
                work_order.assigned_at = now
                if assigned_to:
                    work_order.assigned_to = assigned_to
            elif new_status == 'in_progress' and not work_order.started_at:
                work_order.started_at = now
            elif new_status == 'completed' and not work_order.completed_at:
                work_order.completed_at = now
                work_order.progress_percentage = 100
            elif new_status == 'closed' and not work_order.closed_at:
                work_order.closed_at = now
            
            work_order.save()
            
            # Create status history entry
            WorkOrderStatusHistory.objects.create(
                work_order=work_order,
                old_status=old_status,
                new_status=new_status,
                changed_by=request.user,
                reason=reason
            )
            
            return Response({
                'message': f'Status updated from {old_status} to {new_status}',
                'work_order': WorkOrderDetailSerializer(work_order).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_photo(self, request, pk=None):
        """Upload a photo for a work order"""
        work_order = self.get_object()
        serializer = WorkOrderPhotoSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(work_order=work_order, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_document(self, request, pk=None):
        """Upload a document for a work order"""
        work_order = self.get_object()
        serializer = WorkOrderDocumentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(work_order=work_order, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add a comment to a work order"""
        work_order = self.get_object()
        serializer = WorkOrderCommentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(work_order=work_order, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_progress(self, request, pk=None):
        """Update work order progress percentage"""
        work_order = self.get_object()
        progress = request.data.get('progress_percentage')
        
        if progress is None:
            return Response({'error': 'progress_percentage is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            progress = int(progress)
            if progress < 0 or progress > 100:
                return Response({'error': 'Progress must be between 0 and 100'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            work_order.progress_percentage = progress
            
            # Auto-update status based on progress
            if progress == 100 and work_order.status not in ['completed', 'closed']:
                work_order.status = 'completed'
                work_order.completed_at = timezone.now()
            elif progress > 0 and work_order.status == 'open':
                work_order.status = 'in_progress'
                work_order.started_at = timezone.now()
            
            work_order.save()
            
            return Response({
                'message': 'Progress updated successfully',
                'progress_percentage': work_order.progress_percentage,
                'status': work_order.status
            })
        
        except ValueError:
            return Response({'error': 'Invalid progress percentage'}, 
                          status=status.HTTP_400_BAD_REQUEST)


class WorkOrderPhotoViewSet(viewsets.ModelViewSet):
    """ViewSet for Work Order Photo management"""
    
    queryset = WorkOrderPhoto.objects.select_related('work_order', 'uploaded_by')
    serializer_class = WorkOrderPhotoSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['work_order', 'photo_type']
    ordering = ['-uploaded_at']


class WorkOrderDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for Work Order Document management"""
    
    queryset = WorkOrderDocument.objects.select_related('work_order', 'uploaded_by')
    serializer_class = WorkOrderDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['work_order', 'document_type']
    search_fields = ['title', 'description']
    ordering = ['-uploaded_at']


class WorkOrderCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Work Order Comment management"""
    
    queryset = WorkOrderComment.objects.select_related('work_order', 'created_by')
    serializer_class = WorkOrderCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['work_order', 'is_internal']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)


class WorkOrderChecklistViewSet(viewsets.ModelViewSet):
    """ViewSet for Work Order Checklist management"""
    
    queryset = WorkOrderChecklist.objects.select_related('work_order', 'created_by').prefetch_related('items')
    serializer_class = WorkOrderChecklistSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['work_order', 'is_required']
    ordering = ['order', 'title']
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)


class WorkOrderChecklistItemViewSet(viewsets.ModelViewSet):
    """ViewSet for Work Order Checklist Item management"""
    
    queryset = WorkOrderChecklistItem.objects.select_related('checklist', 'completed_by')
    serializer_class = WorkOrderChecklistItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['checklist', 'is_completed']
    ordering = ['order', 'description']
    
    def perform_update(self, serializer):
        """Set completed_by when marking item as completed"""
        if serializer.validated_data.get('is_completed') and not serializer.instance.completed_by:
            serializer.save(completed_by=self.request.user)
        else:
            serializer.save()
