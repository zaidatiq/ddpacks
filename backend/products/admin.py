from django.contrib import admin

# Register your models here.
from .models import SUKMaster, Inventory

@admin.register(SUKMaster)
class SUKMasterAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'unit_of_measurement', 'units_per_packet', 'is_active']
    search_fields = ['code', 'name']
    list_filter = ['is_active']

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['suk', 'quantity', 'available', 'reserved']
    search_fields = ['suk__code']
