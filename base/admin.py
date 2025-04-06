from base.models import *
from django.contrib import admin

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('customer', 'make', 'model', 'year', 'license_plate', 'vin', 'created_at')
    search_fields = ('make', 'model', 'license_plate', 'vin')
    list_filter = ('make', 'year')
    ordering = ('-created_at',)

@admin.register(VehicleIssue)
class VehicleIssueAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'status', 'estimated_cost', 'created_at')
    search_fields = ('vehicle__license_plate', 'reported_issue', 'diagnosed_issue')
    list_filter = ('status',)
    ordering = ('-created_at',)

