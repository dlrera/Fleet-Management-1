from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.conf import settings
from .models import (
    CapitalPlan, CapitalPlanItem, CapitalPlanScenario, CapitalPlanApproval,
    AssetLifecycle, CapitalProject, ProjectAssetLink
)
from .serializers import (
    CapitalPlanSerializer, CapitalPlanListSerializer,
    CapitalPlanItemSerializer, CapitalPlanScenarioSerializer,
    CapitalPlanApprovalSerializer, AssetLifecycleSerializer,
    AssetLifecycleListSerializer, CapitalProjectSerializer,
    CapitalProjectListSerializer, ProjectAssetLinkSerializer,
    AssetConditionUpdateSerializer
)


def check_capital_planning_enabled():
    """Check if capital planning feature is enabled."""
    return getattr(settings, 'CAPITAL_PLANNING_ENABLED', False)


class CapitalPlanningEnabledMixin:
    """Mixin to check if capital planning is enabled."""
    
    def initial(self, request, *args, **kwargs):
        if not check_capital_planning_enabled():
            self.permission_denied(
                request,
                message='Capital Planning feature is not enabled'
            )
        super().initial(request, *args, **kwargs)


class CapitalPlanViewSet(CapitalPlanningEnabledMixin, viewsets.ModelViewSet):
    """ViewSet for capital plans."""
    
    queryset = CapitalPlan.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'fiscal_year']
    search_fields = ['name', 'description']
    ordering_fields = ['fiscal_year', 'created_at', 'total_budget']
    ordering = ['-fiscal_year', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CapitalPlanListSerializer
        return CapitalPlanSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Check user permissions
        user = self.request.user
        if not user.has_perm('capital_planning.view_plan'):
            # If user doesn't have view permission, only show their own plans
            queryset = queryset.filter(created_by=user)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by fiscal year
        fiscal_year = self.request.query_params.get('fiscal_year')
        if fiscal_year:
            queryset = queryset.filter(fiscal_year=fiscal_year)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get capital planning statistics."""
        if not check_capital_planning_enabled():
            return Response({'error': 'Feature not enabled'}, status=403)
        
        plans = self.get_queryset()
        
        stats = {
            'total_plans': plans.count(),
            'active_plans': plans.filter(status='active').count(),
            'draft_plans': plans.filter(status='draft').count(),
            'approved_plans': plans.filter(status='approved').count(),
            'total_budget': plans.filter(status__in=['active', 'approved']).aggregate(
                total=Sum('total_budget')
            )['total'] or 0,
            'total_allocated': plans.filter(status__in=['active', 'approved']).aggregate(
                total=Sum('allocated_budget')
            )['total'] or 0,
            'current_fy_plans': plans.filter(fiscal_year=timezone.now().year).count(),
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """Submit a plan for review."""
        plan = self.get_object()
        
        if plan.status != 'draft':
            return Response(
                {'error': 'Only draft plans can be submitted for review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan.status = 'review'
        plan.save()
        
        return Response({'status': 'Plan submitted for review'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a capital plan."""
        plan = self.get_object()
        
        if not request.user.has_perm('capital_planning.approve_plan'):
            return Response(
                {'error': 'You do not have permission to approve plans'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if plan.status != 'review':
            return Response(
                {'error': 'Only plans under review can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan.status = 'approved'
        plan.approved_by = request.user
        plan.approved_at = timezone.now()
        plan.save()
        
        # Create approval record
        CapitalPlanApproval.objects.create(
            plan=plan,
            level='executive',  # Could be dynamic based on user role
            approver=request.user,
            action='approve',
            comments=request.data.get('comments', '')
        )
        
        return Response({'status': 'Plan approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a capital plan."""
        plan = self.get_object()
        
        if not request.user.has_perm('capital_planning.approve_plan'):
            return Response(
                {'error': 'You do not have permission to reject plans'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if plan.status != 'review':
            return Response(
                {'error': 'Only plans under review can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan.status = 'rejected'
        plan.save()
        
        # Create rejection record
        CapitalPlanApproval.objects.create(
            plan=plan,
            level='executive',
            approver=request.user,
            action='reject',
            comments=request.data.get('comments', '')
        )
        
        return Response({'status': 'Plan rejected'})


class CapitalPlanItemViewSet(CapitalPlanningEnabledMixin, viewsets.ModelViewSet):
    """ViewSet for capital plan items."""
    
    queryset = CapitalPlanItem.objects.all()
    serializer_class = CapitalPlanItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['plan', 'item_type', 'priority', 'is_approved']
    search_fields = ['description', 'make', 'model']
    ordering_fields = ['priority', 'total_cost', 'created_at']
    ordering = ['priority', '-total_cost']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by plan if provided
        plan_id = self.request.query_params.get('plan')
        if plan_id:
            queryset = queryset.filter(plan_id=plan_id)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def bulk_approve(self, request):
        """Bulk approve multiple items."""
        item_ids = request.data.get('item_ids', [])
        
        if not request.user.has_perm('capital_planning.approve_plan'):
            return Response(
                {'error': 'You do not have permission to approve items'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        items = CapitalPlanItem.objects.filter(id__in=item_ids)
        items.update(
            is_approved=True,
            approval_notes=request.data.get('notes', 'Bulk approved')
        )
        
        # Update plan allocated budget
        for item in items:
            plan = item.plan
            plan.allocated_budget = plan.items.filter(is_approved=True).aggregate(
                total=Sum('total_cost')
            )['total'] or 0
            plan.save()
        
        return Response({'status': f'{items.count()} items approved'})
    
    @action(detail=False, methods=['get'])
    def fleet_assets_for_replacement(self, request):
        """Get fleet assets that might need replacement."""
        try:
            from assets.models import Asset
            
            # Get assets that are good candidates for replacement
            assets = Asset.objects.filter(
                Q(status='maintenance') | Q(year__lt=timezone.now().year - 7)
            ).values('id', 'asset_id', 'make', 'model', 'year', 'status', 'mileage')
            
            return Response(list(assets))
        except:
            return Response([])


class CapitalPlanScenarioViewSet(CapitalPlanningEnabledMixin, viewsets.ModelViewSet):
    """ViewSet for capital plan scenarios."""
    
    queryset = CapitalPlanScenario.objects.all()
    serializer_class = CapitalPlanScenarioSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['plan', 'is_primary']
    ordering = ['-is_primary', 'name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by plan if provided
        plan_id = self.request.query_params.get('plan')
        if plan_id:
            queryset = queryset.filter(plan_id=plan_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_as_primary(self, request, pk=None):
        """Set a scenario as the primary one for its plan."""
        scenario = self.get_object()
        
        # Unset other scenarios as primary
        CapitalPlanScenario.objects.filter(
            plan=scenario.plan
        ).update(is_primary=False)
        
        # Set this one as primary
        scenario.is_primary = True
        scenario.save()
        
        return Response({'status': 'Scenario set as primary'})
    
    @action(detail=True, methods=['post'])
    def calculate(self, request, pk=None):
        """Calculate scenario results based on modifications."""
        scenario = self.get_object()
        plan = scenario.plan
        
        # Get base items
        items = plan.items.all()
        
        # Apply modifications from scenario
        modifications = scenario.item_modifications
        adjusted_budget = plan.total_budget + scenario.budget_adjustment
        
        total_cost = 0
        items_included = 0
        items_deferred = 0
        
        # Simple calculation logic (can be expanded)
        for item in items:
            item_id = str(item.id)
            if item_id in modifications:
                # Apply modifications
                if modifications[item_id].get('exclude', False):
                    items_deferred += 1
                    continue
                
                # Adjust quantity if specified
                quantity = modifications[item_id].get('quantity', item.quantity)
                cost = item.unit_cost * quantity
            else:
                cost = item.total_cost
            
            if total_cost + cost <= adjusted_budget:
                total_cost += cost
                items_included += 1
            else:
                items_deferred += 1
        
        # Update scenario with results
        scenario.total_cost = total_cost
        scenario.items_included = items_included
        scenario.items_deferred = items_deferred
        scenario.save()
        
        return Response({
            'total_cost': total_cost,
            'items_included': items_included,
            'items_deferred': items_deferred,
            'budget_remaining': adjusted_budget - total_cost
        })


class AssetLifecycleViewSet(CapitalPlanningEnabledMixin, viewsets.ModelViewSet):
    """ViewSet for asset lifecycle tracking (Feature 1)."""
    
    queryset = AssetLifecycle.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['asset_category', 'current_condition', 'location', 'department']
    search_fields = ['asset_name', 'asset_code', 'location', 'manufacturer']
    ordering_fields = ['asset_name', 'installation_date', 'replacement_cost', 'lifecycle_percentage']
    ordering = ['asset_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AssetLifecycleListSerializer
        return AssetLifecycleSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by condition
        condition = self.request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(current_condition=condition)
        
        # Filter by replacement needed (assets near end of life)
        needs_replacement = self.request.query_params.get('needs_replacement')
        if needs_replacement == 'true':
            from datetime import date, timedelta
            threshold_date = date.today() + timedelta(days=365)  # Within 1 year
            queryset = [
                asset for asset in queryset
                if asset.estimated_replacement_date and asset.estimated_replacement_date <= threshold_date
            ]
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_condition(self, request, pk=None):
        """Update asset condition assessment."""
        asset = self.get_object()
        serializer = AssetConditionUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            asset.current_condition = serializer.validated_data['condition']
            asset.last_condition_assessment = serializer.validated_data['assessment_date']
            asset.condition_notes = serializer.validated_data.get('notes', '')
            asset.save()
            
            return Response(AssetLifecycleSerializer(asset).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def replacement_schedule(self, request):
        """Get assets grouped by replacement year."""
        from datetime import date
        from collections import defaultdict
        
        assets = self.get_queryset()
        schedule = defaultdict(list)
        
        for asset in assets:
            if asset.estimated_replacement_date:
                year = asset.estimated_replacement_date.year
                schedule[year].append({
                    'id': asset.id,
                    'asset_name': asset.asset_name,
                    'asset_code': asset.asset_code,
                    'replacement_cost': asset.replacement_cost,
                    'condition': asset.current_condition,
                    'estimated_date': asset.estimated_replacement_date
                })
        
        # Sort by year and calculate totals
        result = []
        for year in sorted(schedule.keys()):
            assets_in_year = schedule[year]
            total_cost = sum(a['replacement_cost'] for a in assets_in_year)
            result.append({
                'year': year,
                'asset_count': len(assets_in_year),
                'total_cost': total_cost,
                'assets': assets_in_year
            })
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def maintenance_analysis(self, request):
        """Analyze maintenance costs vs replacement costs."""
        assets = self.get_queryset()
        
        high_maintenance = []
        for asset in assets:
            if asset.maintenance_cost_ratio > 50:  # Maintenance cost > 50% of replacement
                high_maintenance.append({
                    'id': asset.id,
                    'asset_name': asset.asset_name,
                    'maintenance_cost': asset.total_maintenance_cost,
                    'replacement_cost': asset.replacement_cost,
                    'ratio': asset.maintenance_cost_ratio,
                    'age_years': asset.age_years,
                    'condition': asset.current_condition
                })
        
        # Sort by ratio descending
        high_maintenance.sort(key=lambda x: x['ratio'], reverse=True)
        
        return Response({
            'high_maintenance_assets': high_maintenance,
            'total_assets': assets.count(),
            'assets_needing_review': len(high_maintenance)
        })


class CapitalProjectViewSet(CapitalPlanningEnabledMixin, viewsets.ModelViewSet):
    """ViewSet for capital projects (Feature 2)."""
    
    queryset = CapitalProject.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'priority', 'category', 'scheduled_year', 'department']
    search_fields = ['project_code', 'title', 'description', 'department']
    ordering_fields = ['priority', 'scheduled_year', 'estimated_cost', 'title']
    ordering = ['priority', 'scheduled_year']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CapitalProjectListSerializer
        return CapitalProjectSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by year range
        year_from = self.request.query_params.get('year_from')
        year_to = self.request.query_params.get('year_to')
        if year_from:
            queryset = queryset.filter(scheduled_year__gte=year_from)
        if year_to:
            queryset = queryset.filter(scheduled_year__lte=year_to)
        
        # Filter by budget range
        min_cost = self.request.query_params.get('min_cost')
        max_cost = self.request.query_params.get('max_cost')
        if min_cost:
            queryset = queryset.filter(estimated_cost__gte=min_cost)
        if max_cost:
            queryset = queryset.filter(estimated_cost__lte=max_cost)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def link_assets(self, request, pk=None):
        """Link assets to a project with proper authorization checks."""
        from django.db import transaction
        
        # Check user has permission to modify projects
        if not request.user.has_perm('capital_planning.change_capitalproject'):
            return Response(
                {'error': 'You do not have permission to link assets to projects'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        project = self.get_object()
        asset_links = request.data.get('assets', [])
        
        if not asset_links:
            return Response(
                {'error': 'No assets provided for linking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_links = []
        errors = []
        
        with transaction.atomic():
            for link_data in asset_links:
                asset_id = link_data.get('asset_lifecycle_id')
                relationship = link_data.get('relationship_type', 'replace')
                notes = link_data.get('notes', '')
                
                # Validate relationship type
                valid_relationships = ['replace', 'upgrade', 'new', 'related']
                if relationship not in valid_relationships:
                    errors.append(f"Invalid relationship type: {relationship}")
                    continue
                
                try:
                    # Verify asset exists and user has access
                    asset = AssetLifecycle.objects.select_for_update().get(id=asset_id)
                    
                    # Additional permission check - ensure user can access this asset
                    # In a real system, you might check department or location access
                    if hasattr(asset, 'department') and asset.department:
                        if not request.user.groups.filter(name=asset.department).exists():
                            if not request.user.is_superuser:
                                errors.append(f"No access to asset {asset_id}")
                                continue
                    
                    # Check if link already exists
                    link, created = ProjectAssetLink.objects.get_or_create(
                        project=project,
                        asset_lifecycle=asset,
                        defaults={
                            'relationship_type': relationship,
                            'notes': notes[:500] if notes else ''  # Limit notes length
                        }
                    )
                    
                    if created:
                        created_links.append(link)
                    else:
                        errors.append(f"Asset {asset_id} already linked to project")
                        
                except AssetLifecycle.DoesNotExist:
                    errors.append(f"Asset {asset_id} not found")
                except Exception as e:
                    errors.append(f"Error linking asset {asset_id}: {str(e)}")
        
        response_data = {
            'created': ProjectAssetLinkSerializer(created_links, many=True).data,
            'errors': errors if errors else None
        }
        
        status_code = status.HTTP_201_CREATED if created_links else status.HTTP_400_BAD_REQUEST
        return Response(response_data, status=status_code)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a capital project."""
        from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
        from django.core.exceptions import ValidationError
        
        project = self.get_object()
        
        if not request.user.has_perm('capital_planning.approve_plan'):
            return Response(
                {'error': 'You do not have permission to approve projects'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate and sanitize budget input
        try:
            budget = request.data.get('budget', project.estimated_cost)
            if budget is not None:
                # Convert to Decimal safely
                budget_decimal = Decimal(str(budget))
                
                # Validate budget is within reasonable range
                if budget_decimal < 0:
                    return Response(
                        {'error': 'Budget cannot be negative'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if budget_decimal > Decimal('999999999.99'):
                    return Response(
                        {'error': 'Budget exceeds maximum allowed value'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Round to 2 decimal places for currency
                project.approved_budget = budget_decimal.quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
            else:
                project.approved_budget = project.estimated_cost
                
            project.status = 'approved'
            project.approval_date = timezone.now().date()
            project.approved_by = request.user
            project.save()
            
            return Response(CapitalProjectSerializer(project).data)
            
        except (InvalidOperation, ValueError) as e:
            return Response(
                {'error': 'Invalid budget format. Please provide a valid number.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def yearly_summary(self, request):
        """Get projects summarized by year."""
        projects = self.get_queryset()
        
        summary = projects.values('scheduled_year').annotate(
            total_projects=Count('id'),
            total_estimated_cost=Sum('estimated_cost'),
            total_approved_budget=Sum('approved_budget'),
            approved_count=Count('id', filter=Q(status='approved')),
            in_progress_count=Count('id', filter=Q(status='in_progress')),
            completed_count=Count('id', filter=Q(status='completed'))
        ).order_by('scheduled_year')
        
        return Response(list(summary))
    
    @action(detail=False, methods=['get'])
    def priority_matrix(self, request):
        """Get projects organized by priority and status."""
        projects = self.get_queryset()
        
        matrix = {}
        for priority in ['critical', 'high', 'medium', 'low']:
            matrix[priority] = {
                'proposed': [],
                'approved': [],
                'in_progress': [],
                'completed': []
            }
        
        for project in projects:
            if project.priority in matrix and project.status in matrix[project.priority]:
                matrix[project.priority][project.status].append({
                    'id': project.id,
                    'project_code': project.project_code,
                    'title': project.title,
                    'estimated_cost': project.estimated_cost,
                    'scheduled_year': project.scheduled_year
                })
        
        return Response(matrix)
