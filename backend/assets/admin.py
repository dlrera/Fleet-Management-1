from django.contrib import admin
from .models import Asset, AssetDocument


class AssetDocumentInline(admin.TabularInline):
    model = AssetDocument
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_id', 'vehicle_type', 'make', 'model', 'year', 'status', 'department', 'current_odometer']
    list_filter = ['vehicle_type', 'status', 'year', 'department']
    search_fields = ['asset_id', 'make', 'model', 'vin', 'license_plate']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [AssetDocumentInline]
    
    fieldsets = (
        ('Identification', {
            'fields': ('asset_id', 'vehicle_type', 'status')
        }),
        ('Vehicle Details', {
            'fields': ('make', 'model', 'year', 'vin', 'license_plate')
        }),
        ('Assignment & Financial', {
            'fields': ('department', 'purchase_date', 'purchase_cost')
        }),
        ('Operational', {
            'fields': ('current_odometer', 'notes')
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(AssetDocument)
class AssetDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'asset', 'document_type', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['title', 'asset__asset_id', 'description']
    readonly_fields = ['uploaded_at']