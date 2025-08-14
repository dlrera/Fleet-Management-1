from django.contrib import admin
from .models import Driver, DriverCertification, DriverIncident, DriverTraining

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'employment_status', 'license_number', 'license_expiry_date', 'safety_rating']
    list_filter = ['employment_status', 'license_class', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'license_number']
    ordering = ['-created_at']
    readonly_fields = ['driver_id', 'created_at', 'updated_at']

@admin.register(DriverCertification)
class DriverCertificationAdmin(admin.ModelAdmin):
    list_display = ['driver', 'certification_type', 'issuing_authority', 'expiry_date']
    list_filter = ['certification_type', 'expiry_date']
    search_fields = ['driver__user__first_name', 'driver__user__last_name', 'certification_type']

@admin.register(DriverIncident)
class DriverIncidentAdmin(admin.ModelAdmin):
    list_display = ['driver', 'incident_type', 'severity', 'incident_date', 'resolved']
    list_filter = ['severity', 'resolved', 'incident_date']
    search_fields = ['driver__user__first_name', 'driver__user__last_name', 'incident_type']

@admin.register(DriverTraining)
class DriverTrainingAdmin(admin.ModelAdmin):
    list_display = ['driver', 'training_type', 'completion_date', 'instructor']
    list_filter = ['training_type', 'completion_date']
    search_fields = ['driver__user__first_name', 'driver__user__last_name', 'training_type']
