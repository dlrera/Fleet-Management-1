from django.contrib import admin
from .models import Driver, DriverCertification, DriverAssetAssignment, DriverViolation


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['driver_id', 'first_name', 'last_name', 'employment_status', 'license_expiration', 'created_at']
    list_filter = ['employment_status', 'license_type', 'department']
    search_fields = ['driver_id', 'first_name', 'last_name', 'email', 'license_number']
    readonly_fields = ['id', 'driver_id', 'full_name', 'age', 'license_expires_soon', 'license_is_expired', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('driver_id', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'date_of_birth', 'age')
        }),
        ('Employment', {
            'fields': ('hire_date', 'employment_status', 'department', 'position', 'employee_number')
        }),
        ('License Information', {
            'fields': ('license_number', 'license_type', 'license_expiration', 'license_state', 'license_expires_soon', 'license_is_expired')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'zip_code')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Additional', {
            'fields': ('profile_photo', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(DriverCertification)
class DriverCertificationAdmin(admin.ModelAdmin):
    list_display = ['driver', 'certification_type', 'certification_number', 'expiration_date', 'status', 'expires_soon']
    list_filter = ['certification_type', 'status']
    search_fields = ['driver__driver_id', 'driver__first_name', 'driver__last_name', 'certification_name', 'certification_number']
    readonly_fields = ['expires_soon', 'is_expired', 'created_at', 'updated_at']


@admin.register(DriverAssetAssignment)
class DriverAssetAssignmentAdmin(admin.ModelAdmin):
    list_display = ['driver', 'asset', 'assignment_type', 'status', 'assigned_date', 'is_current']
    list_filter = ['assignment_type', 'status']
    search_fields = ['driver__driver_id', 'driver__first_name', 'driver__last_name', 'asset__asset_id']
    readonly_fields = ['is_current', 'duration_days', 'created_at', 'updated_at']


@admin.register(DriverViolation)
class DriverViolationAdmin(admin.ModelAdmin):
    list_display = ['driver', 'violation_type', 'severity', 'violation_date', 'resolved', 'fine_amount']
    list_filter = ['violation_type', 'severity', 'resolved']
    search_fields = ['driver__driver_id', 'driver__first_name', 'driver__last_name', 'description', 'citation_number']
    readonly_fields = ['created_at', 'updated_at']
