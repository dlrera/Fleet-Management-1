from rest_framework import serializers
from .models import Driver, DriverCertification, DriverAssetAssignment, DriverViolation
from assets.serializers import AssetListSerializer
from datetime import date, timedelta


class DriverCertificationSerializer(serializers.ModelSerializer):
    expires_soon = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    certification_type_display = serializers.CharField(source='get_certification_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DriverCertification
        fields = [
            'id', 'certification_type', 'certification_type_display', 'certification_number',
            'certification_name', 'issued_date', 'expiration_date', 'issuing_authority',
            'status', 'status_display', 'notes', 'certificate_document',
            'expires_soon', 'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DriverAssetAssignmentSerializer(serializers.ModelSerializer):
    asset_details = AssetListSerializer(source='asset', read_only=True)
    assignment_type_display = serializers.CharField(source='get_assignment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_current = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()
    
    class Meta:
        model = DriverAssetAssignment
        fields = [
            'id', 'asset', 'asset_details', 'assignment_type', 'assignment_type_display',
            'status', 'status_display', 'assigned_date', 'unassigned_date',
            'assigned_by', 'notes', 'is_current', 'duration_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DriverViolationSerializer(serializers.ModelSerializer):
    violation_type_display = serializers.CharField(source='get_violation_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    asset_details = AssetListSerializer(source='asset', read_only=True)
    
    class Meta:
        model = DriverViolation
        fields = [
            'id', 'violation_type', 'violation_type_display', 'severity', 'severity_display',
            'description', 'violation_date', 'citation_number', 'fine_amount',
            'asset', 'asset_details', 'resolved', 'resolution_date', 'resolution_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DriverSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    license_expires_soon = serializers.ReadOnlyField()
    license_is_expired = serializers.ReadOnlyField()
    employment_status_display = serializers.CharField(source='get_employment_status_display', read_only=True)
    license_type_display = serializers.CharField(source='get_license_type_display', read_only=True)
    
    # Nested relationships
    certifications = DriverCertificationSerializer(many=True, read_only=True)
    asset_assignments = serializers.SerializerMethodField()
    violations = DriverViolationSerializer(many=True, read_only=True)
    
    # Computed fields
    certifications_count = serializers.SerializerMethodField()
    active_assignments_count = serializers.SerializerMethodField()
    violations_count = serializers.SerializerMethodField()
    expiring_items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = [
            'id', 'driver_id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'date_of_birth', 'age', 'hire_date', 'employment_status', 'employment_status_display',
            'department', 'position', 'employee_number', 'license_number', 'license_type',
            'license_type_display', 'license_expiration', 'license_state', 'license_expires_soon',
            'license_is_expired', 'address_line1', 'address_line2', 'city', 'state', 'zip_code',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'profile_photo', 'notes', 'certifications', 'asset_assignments', 'violations',
            'certifications_count', 'active_assignments_count', 'violations_count',
            'expiring_items_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_certifications_count(self, obj):
        return obj.certifications.count()
    
    def get_asset_assignments(self, obj):
        # Get active asset assignments for this driver
        assignments = obj.asset_assignments.filter(
            status='active',
            unassigned_date__isnull=True
        ).select_related('asset').order_by('priority', '-assigned_date')
        
        return DriverAssetAssignmentSerializer(assignments, many=True).data
    
    def get_active_assignments_count(self, obj):
        return obj.asset_assignments.filter(status='active', unassigned_date__isnull=True).count()
    
    def get_violations_count(self, obj):
        return obj.violations.count()
    
    def get_expiring_items_count(self, obj):
        count = 0
        # Check license expiration
        if obj.license_expires_soon:
            count += 1
        # Check certification expirations
        thirty_days_from_now = date.today() + timedelta(days=30)
        expiring_certs = obj.certifications.filter(
            expiration_date__lte=thirty_days_from_now,
            expiration_date__gte=date.today()
        ).count()
        count += expiring_certs
        return count
    
    def validate_email(self, value):
        """Validate unique email excluding current instance"""
        instance = self.instance
        if instance and Driver.objects.filter(email=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("A driver with this email already exists.")
        elif not instance and Driver.objects.filter(email=value).exists():
            raise serializers.ValidationError("A driver with this email already exists.")
        return value
    
    def validate_license_number(self, value):
        """Validate unique license number excluding current instance"""
        instance = self.instance
        if instance and Driver.objects.filter(license_number=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("A driver with this license number already exists.")
        elif not instance and Driver.objects.filter(license_number=value).exists():
            raise serializers.ValidationError("A driver with this license number already exists.")
        return value
    
    def validate_date_of_birth(self, value):
        """Validate driver is at least 16 years old"""
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 16:
            raise serializers.ValidationError("Driver must be at least 16 years old.")
        return value
    


class DriverListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    license_expires_soon = serializers.ReadOnlyField()
    license_is_expired = serializers.ReadOnlyField()
    employment_status_display = serializers.CharField(source='get_employment_status_display', read_only=True)
    license_type_display = serializers.CharField(source='get_license_type_display', read_only=True)
    
    # Computed fields
    certifications_count = serializers.SerializerMethodField()
    active_assignments_count = serializers.SerializerMethodField()
    violations_count = serializers.SerializerMethodField()
    expiring_items_count = serializers.SerializerMethodField()
    alert_details = serializers.SerializerMethodField()
    has_critical_alert = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = [
            'id', 'driver_id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'employment_status', 'employment_status_display', 'department', 'position',
            'license_number', 'license_type', 'license_type_display', 'license_expiration', 
            'license_expires_soon', 'license_is_expired', 'age', 'profile_photo', 'certifications_count',
            'active_assignments_count', 'violations_count', 'expiring_items_count', 'alert_details',
            'has_critical_alert', 'created_at'
        ]
    
    def get_certifications_count(self, obj):
        return obj.certifications.count()
    
    def get_active_assignments_count(self, obj):
        return obj.asset_assignments.filter(status='active', unassigned_date__isnull=True).count()
    
    def get_violations_count(self, obj):
        return obj.violations.count()
    
    def get_expiring_items_count(self, obj):
        count = 0
        # Check license expiration
        if obj.license_expires_soon:
            count += 1
        # Check certification expirations
        thirty_days_from_now = date.today() + timedelta(days=30)
        expiring_certs = obj.certifications.filter(
            expiration_date__lte=thirty_days_from_now,
            expiration_date__gte=date.today()
        ).count()
        count += expiring_certs
        return count
    
    def get_alert_details(self, obj):
        """Get alert details only if driver has assignments but can't drive"""
        alerts = []
        active_assignments = obj.asset_assignments.filter(status='active', unassigned_date__isnull=True)
        
        # Only generate alerts if driver has active assignments
        if active_assignments.exists():
            # Check if driver is suspended or terminated
            if obj.employment_status in ['suspended', 'terminated']:
                alerts.append({
                    'type': 'employment_status',
                    'severity': 'critical',
                    'message': f'Driver is {obj.get_employment_status_display()} but has {active_assignments.count()} active vehicle assignment(s)',
                    'affected_vehicles': list(active_assignments.values_list('asset__asset_id', flat=True))
                })
            
            # Check if license is expired
            if obj.license_is_expired:
                alerts.append({
                    'type': 'license_expired',
                    'severity': 'critical',
                    'message': f'License expired on {obj.license_expiration} but driver has {active_assignments.count()} active vehicle assignment(s)',
                    'affected_vehicles': list(active_assignments.values_list('asset__asset_id', flat=True))
                })
        
        return alerts
    
    def get_has_critical_alert(self, obj):
        """Check if driver has any critical alerts"""
        active_assignments = obj.asset_assignments.filter(status='active', unassigned_date__isnull=True)
        
        if active_assignments.exists():
            # Has critical alert if driver can't drive but has assignments
            return (obj.employment_status in ['suspended', 'terminated']) or obj.license_is_expired
        
        return False


class DriverCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for create/update operations without nested relationships"""
    
    driver_id = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Driver
        fields = [
            'id', 'driver_id', 'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'hire_date', 'employment_status', 'department', 'position',
            'employee_number', 'license_number', 'license_type', 'license_expiration',
            'license_state', 'address_line1', 'address_line2', 'city', 'state', 'zip_code',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'profile_photo', 'notes'
        ]
        read_only_fields = ['id']
    
    def validate_email(self, value):
        """Validate unique email excluding current instance"""
        instance = self.instance
        if instance and Driver.objects.filter(email=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("A driver with this email already exists.")
        elif not instance and Driver.objects.filter(email=value).exists():
            raise serializers.ValidationError("A driver with this email already exists.")
        return value
    
    def validate_license_number(self, value):
        """Validate unique license number excluding current instance"""
        instance = self.instance
        if instance and Driver.objects.filter(license_number=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("A driver with this license number already exists.")
        elif not instance and Driver.objects.filter(license_number=value).exists():
            raise serializers.ValidationError("A driver with this license number already exists.")
        return value
    
    def validate_date_of_birth(self, value):
        """Validate driver is at least 16 years old"""
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 16:
            raise serializers.ValidationError("Driver must be at least 16 years old.")
        return value
    


class DriverCertificationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for certification create/update operations"""
    
    class Meta:
        model = DriverCertification
        fields = [
            'id', 'certification_type', 'certification_number', 'certification_name',
            'issued_date', 'expiration_date', 'issuing_authority', 'status',
            'notes', 'certificate_document'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate certification data"""
        # If certification_type is 'other', certification_name is required
        if data.get('certification_type') == 'other' and not data.get('certification_name'):
            raise serializers.ValidationError({
                'certification_name': 'Certification name is required when type is "other".'
            })
        
        # Validate dates
        if data.get('expiration_date') and data.get('issued_date'):
            if data['expiration_date'] <= data['issued_date']:
                raise serializers.ValidationError({
                    'expiration_date': 'Expiration date must be after issued date.'
                })
        
        return data


class DriverAssetAssignmentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for assignment create/update operations"""
    
    class Meta:
        model = DriverAssetAssignment
        fields = [
            'id', 'driver', 'asset', 'assignment_type', 'status',
            'assigned_date', 'unassigned_date', 'assigned_by', 'notes'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate assignment data"""
        # Validate dates
        if data.get('unassigned_date') and data.get('assigned_date'):
            if data['unassigned_date'] <= data['assigned_date']:
                raise serializers.ValidationError({
                    'unassigned_date': 'Unassigned date must be after assigned date.'
                })
        
        # Check for overlapping primary assignments
        if data.get('assignment_type') == 'primary' and data.get('status') == 'active':
            driver = data.get('driver')
            asset = data.get('asset')
            assigned_date = data.get('assigned_date')
            unassigned_date = data.get('unassigned_date')
            
            # Check if driver already has an active primary assignment
            existing_assignments = DriverAssetAssignment.objects.filter(
                driver=driver,
                assignment_type='primary',
                status='active',
                unassigned_date__isnull=True
            )
            
            # Exclude current instance if updating
            if self.instance:
                existing_assignments = existing_assignments.exclude(pk=self.instance.pk)
            
            if existing_assignments.exists():
                raise serializers.ValidationError({
                    'assignment_type': 'Driver already has an active primary assignment.'
                })
            
            # Check if asset already has an active primary driver
            existing_asset_assignments = DriverAssetAssignment.objects.filter(
                asset=asset,
                assignment_type='primary',
                status='active',
                unassigned_date__isnull=True
            )
            
            # Exclude current instance if updating
            if self.instance:
                existing_asset_assignments = existing_asset_assignments.exclude(pk=self.instance.pk)
            
            if existing_asset_assignments.exists():
                raise serializers.ValidationError({
                    'asset': 'Asset already has an active primary driver.'
                })
        
        return data