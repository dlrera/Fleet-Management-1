from django.contrib import admin
from .models import Department, Asset, AssetDocument, AssetImage

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_number', 'make', 'model', 'year', 'status', 'department', 'created_at']
    list_filter = ['status', 'vehicle_type', 'department', 'created_at']
    search_fields = ['asset_number', 'make', 'model', 'vin_number', 'license_plate']
    ordering = ['-created_at']
    readonly_fields = ['asset_id', 'created_at', 'updated_at']

@admin.register(AssetDocument)
class AssetDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'asset', 'document_type', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['title', 'asset__asset_number']

@admin.register(AssetImage)
class AssetImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'asset', 'uploaded_at']
    search_fields = ['title', 'asset__asset_number']
