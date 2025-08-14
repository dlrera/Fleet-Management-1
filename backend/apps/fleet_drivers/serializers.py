from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import date
from .models import Driver, DriverCertification, DriverIncident, DriverTraining


class UserSerializer(serializers.ModelSerializer):
    """Basic User serializer for driver profiles"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id', 'username']


class DriverCertificationSerializer(serializers.ModelSerializer):
    """Serializer for Driver Certifications"""
    
    is_expired = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = DriverCertification
        fields = ['certification_id', 'certification_name', 'issuing_authority', 
                 'issue_date', 'expiry_date', 'certification_number', 'is_expired', 
                 'days_until_expiry', 'notes', 'created_at']
        read_only_fields = ['certification_id', 'created_at', 'is_expired', 'days_until_expiry']
    
    def get_is_expired(self, obj):
        return obj.is_expired
    
    def get_days_until_expiry(self, obj):
        return obj.days_until_expiry


class DriverIncidentSerializer(serializers.ModelSerializer):
    """Serializer for Driver Incidents"""
    
    class Meta:
        model = DriverIncident
        fields = ['incident_id', 'incident_date', 'incident_type', 'severity', 
                 'location', 'description', 'police_report_number', 'fault_determination',
                 'insurance_claim_number', 'cost_estimate', 'was_citation_issued',
                 'citation_details', 'created_at', 'updated_at']
        read_only_fields = ['incident_id', 'created_at', 'updated_at']


class DriverTrainingSerializer(serializers.ModelSerializer):
    """Serializer for Driver Training"""
    
    is_expired = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = DriverTraining
        fields = ['training_id', 'training_name', 'training_type', 'provider',
                 'completion_date', 'expiry_date', 'certificate_number', 'hours',
                 'cost', 'is_expired', 'days_until_expiry', 'notes', 'created_at']
        read_only_fields = ['training_id', 'created_at', 'is_expired', 'days_until_expiry']
    
    def get_is_expired(self, obj):
        return obj.is_expired
    
    def get_days_until_expiry(self, obj):
        return obj.days_until_expiry


class DriverListSerializer(serializers.ModelSerializer):
    """Simplified Driver serializer for list views"""
    
    user = UserSerializer(read_only=True)
    license_status = serializers.SerializerMethodField()
    assigned_vehicle_count = serializers.SerializerMethodField()
    safety_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = ['driver_id', 'user', 'license_number', 'license_class',
                 'license_expiry_date', 'phone_number', 'employment_status', 'hire_date',
                 'license_status', 'assigned_vehicle_count', 'safety_score', 'created_at']
        read_only_fields = ['driver_id', 'created_at', 'license_status', 
                          'assigned_vehicle_count', 'safety_score']
    
    def get_license_status(self, obj):
        if obj.license_expiry_date < date.today():
            return 'expired'
        elif obj.days_until_license_expiry <= 30:
            return 'expiring_soon'
        return 'valid'
    
    def get_assigned_vehicle_count(self, obj):
        return obj.assigned_vehicles.count()
    
    def get_safety_score(self, obj):
        return obj.safety_rating


class DriverDetailSerializer(serializers.ModelSerializer):
    """Detailed Driver serializer for detail views"""
    
    user = UserSerializer(read_only=True)
    certifications = DriverCertificationSerializer(many=True, read_only=True)
    incidents = DriverIncidentSerializer(many=True, read_only=True, source='driver_incidents')
    training = DriverTrainingSerializer(many=True, read_only=True, source='driver_training')
    assigned_vehicles = serializers.SerializerMethodField()
    
    license_status = serializers.SerializerMethodField()
    days_until_license_expiry = serializers.SerializerMethodField()
    total_incidents = serializers.SerializerMethodField()
    recent_incidents = serializers.SerializerMethodField()
    expiring_certifications = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = ['driver_id', 'user', 'license_number', 'license_class', 
                 'license_expiry_date', 'phone_number', 'emergency_contact_name',
                 'emergency_contact_phone', 'address', 'date_of_birth', 'hire_date',
                 'termination_date', 'employment_status', 'medical_exam_date', 'medical_exam_expiry',
                 'background_check_date', 'drug_test_date', 'notes',
                 'certifications', 'incidents', 'training', 'assigned_vehicles',
                 'license_status', 'days_until_license_expiry', 'total_incidents',
                 'recent_incidents', 'expiring_certifications', 'safety_rating',
                 'created_at', 'updated_at']
        read_only_fields = ['driver_id', 'created_at', 'updated_at', 'assigned_vehicles',
                          'license_status', 'days_until_license_expiry', 'total_incidents',
                          'recent_incidents', 'expiring_certifications', 'safety_rating']
    
    def get_assigned_vehicles(self, obj):
        return [{'asset_id': str(vehicle.asset_id),
                'asset_number': vehicle.asset_number,
                'make_model': f"{vehicle.make} {vehicle.model}",
                'license_plate': vehicle.license_plate}
                for vehicle in obj.assigned_vehicles.all()]
    
    def get_license_status(self, obj):
        if obj.license_expiry_date < date.today():
            return 'expired'
        elif obj.days_until_license_expiry <= 30:
            return 'expiring_soon'
        return 'valid'
    
    def get_days_until_license_expiry(self, obj):
        return obj.days_until_license_expiry
    
    def get_total_incidents(self, obj):
        return obj.driver_incidents.count()
    
    def get_recent_incidents(self, obj):
        from datetime import timedelta
        recent_date = date.today() - timedelta(days=365)
        return obj.driver_incidents.filter(incident_date__gte=recent_date).count()
    
    def get_expiring_certifications(self, obj):
        from datetime import timedelta
        future_date = date.today() + timedelta(days=30)
        return obj.certifications.filter(
            expiry_date__lte=future_date,
            expiry_date__gte=date.today()
        ).count()


class DriverCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating drivers"""
    
    user_data = UserSerializer(required=False)
    
    class Meta:
        model = Driver
        fields = ['license_number', 'license_class', 'license_expiry_date',
                 'phone_number', 'emergency_contact_name', 'emergency_contact_phone',
                 'address', 'date_of_birth', 'hire_date', 'termination_date', 'employment_status',
                 'medical_exam_date', 'medical_exam_expiry', 'background_check_date',
                 'drug_test_date', 'notes', 'user_data', 'assigned_vehicles']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user_data', {})
        assigned_vehicles = validated_data.pop('assigned_vehicles', [])
        
        # Create or get user if provided
        user = None
        if user_data:
            user_serializer = UserSerializer(data=user_data)
            if user_serializer.is_valid():
                user = user_serializer.save()
        
        # Create driver
        driver = Driver.objects.create(user=user, **validated_data)
        
        # Assign vehicles
        if assigned_vehicles:
            driver.assigned_vehicles.set(assigned_vehicles)
        
        return driver
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user_data', {})
        assigned_vehicles = validated_data.pop('assigned_vehicles', None)
        
        # Update user data if provided
        if user_data and instance.user:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
        
        # Update driver
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update assigned vehicles
        if assigned_vehicles is not None:
            instance.assigned_vehicles.set(assigned_vehicles)
        
        return instance
    
    def validate_license_expiry_date(self, value):
        """Validate license expiry date is not in the past"""
        if value < date.today():
            raise serializers.ValidationError("License expiry date cannot be in the past")
        return value
    
    def validate_license_number(self, value):
        """Validate license number uniqueness"""
        instance = getattr(self, 'instance', None)
        if Driver.objects.filter(license_number=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("License number must be unique")
        return value