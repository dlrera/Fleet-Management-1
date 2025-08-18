"""
Audit log views and API endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.http import HttpResponse
from .models import AuditLog
from .permissions import IsAdmin
import csv
from datetime import datetime, timedelta
from django.utils import timezone


class AuditLogSerializer:
    """Simple serializer for audit logs"""
    @staticmethod
    def serialize(audit_log):
        return {
            'id': str(audit_log.id),
            'timestamp': audit_log.timestamp.isoformat(),
            'actor_email': audit_log.actor_email,
            'actor_role': audit_log.actor_role,
            'action': audit_log.action,
            'action_display': audit_log.get_action_display(),
            'resource_type': audit_log.resource_type,
            'resource_id': audit_log.resource_id,
            'resource_name': audit_log.resource_name,
            'ip_address': audit_log.ip_address,
            'risk_score': audit_log.risk_score,
            'before_state': audit_log.before_state,
            'after_state': audit_log.after_state,
            'changes': audit_log.changes,
        }


class AuditLogViewSet(viewsets.ViewSet):
    """ViewSet for audit log management"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def list(self, request):
        """List audit logs with filtering"""
        queryset = AuditLog.objects.all()
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        # Filter by actor
        actor_email = request.query_params.get('actor')
        if actor_email:
            queryset = queryset.filter(actor_email__icontains=actor_email)
        
        # Filter by action
        action = request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by resource type
        resource_type = request.query_params.get('resource_type')
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        # Filter by risk score
        min_risk = request.query_params.get('min_risk')
        if min_risk:
            queryset = queryset.filter(risk_score__gte=int(min_risk))
        
        # Search across multiple fields
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(actor_email__icontains=search) |
                Q(resource_name__icontains=search) |
                Q(resource_type__icontains=search) |
                Q(action__icontains=search)
            )
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = queryset.count()
        logs = queryset[start:end]
        
        return Response({
            'results': [AuditLogSerializer.serialize(log) for log in logs],
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
    
    def retrieve(self, request, pk=None):
        """Get single audit log"""
        try:
            log = AuditLog.objects.get(id=pk)
            return Response(AuditLogSerializer.serialize(log))
        except AuditLog.DoesNotExist:
            return Response(
                {'error': 'Audit log not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export audit logs to CSV"""
        queryset = AuditLog.objects.all()
        
        # Apply same filters as list
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        actor_email = request.query_params.get('actor')
        if actor_email:
            queryset = queryset.filter(actor_email__icontains=actor_email)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Timestamp', 'Actor Email', 'Actor Role', 'Action', 
            'Resource Type', 'Resource ID', 'Resource Name',
            'IP Address', 'Risk Score'
        ])
        
        for log in queryset[:10000]:  # Limit to 10k records
            writer.writerow([
                log.timestamp.isoformat(),
                log.actor_email,
                log.actor_role,
                log.get_action_display(),
                log.resource_type,
                log.resource_id,
                log.resource_name,
                log.ip_address,
                log.risk_score
            ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get audit log statistics"""
        # Time range (last 30 days by default)
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = AuditLog.objects.filter(timestamp__gte=start_date)
        
        # Get action counts
        action_counts = {}
        for log in queryset.values('action').distinct():
            action = log['action']
            count = queryset.filter(action=action).count()
            action_counts[action] = count
        
        # Get top actors
        top_actors = []
        for actor in queryset.values('actor_email').distinct()[:10]:
            email = actor['actor_email']
            count = queryset.filter(actor_email=email).count()
            top_actors.append({'email': email, 'count': count})
        top_actors.sort(key=lambda x: x['count'], reverse=True)
        
        # Get risk distribution
        risk_distribution = {
            'low': queryset.filter(risk_score__lt=30).count(),
            'medium': queryset.filter(risk_score__gte=30, risk_score__lt=60).count(),
            'high': queryset.filter(risk_score__gte=60).count(),
        }
        
        # Get resource type counts
        resource_counts = {}
        for resource in queryset.values('resource_type').distinct():
            resource_type = resource['resource_type']
            count = queryset.filter(resource_type=resource_type).count()
            resource_counts[resource_type] = count
        
        return Response({
            'total_events': queryset.count(),
            'date_range': {
                'start': start_date.isoformat(),
                'end': timezone.now().isoformat(),
                'days': days
            },
            'action_counts': action_counts,
            'top_actors': top_actors[:5],
            'risk_distribution': risk_distribution,
            'resource_counts': resource_counts,
            'high_risk_events': queryset.filter(risk_score__gte=80).count(),
            'failed_permissions': queryset.filter(action='permission_denied').count(),
        })
    
    @action(detail=False, methods=['get'])
    def action_types(self, request):
        """Get available action types"""
        return Response({
            'actions': [
                {'value': choice[0], 'label': choice[1]}
                for choice in AuditLog.ACTION_CHOICES
            ]
        })