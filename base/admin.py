from base.models import *
from django.contrib import admin

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('customer', 'make', 'model', 'year', 'license_plate', 'vin', 'created_at')
    search_fields = ('make', 'model', 'license_plate', 'vin')
    list_filter = ('make', 'year')
    ordering = ('-created_at',)