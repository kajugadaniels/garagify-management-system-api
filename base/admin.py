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

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'item_type', 'quantity', 'unit_price', 'created_by', 'created_at')
    search_fields = ('item_name',)
    list_filter = ('item_type',)
    ordering = ('-created_at',)

@admin.register(VehicleSolution)
class VehicleSolutionAdmin(admin.ModelAdmin):
    list_display = ('vehicle_issue', 'solution_date', 'total_cost')
    search_fields = ('vehicle_issue__reported_issue', 'solution_description')
    ordering = ('-solution_date',)

@admin.register(SolutionItem)
class SolutionItemAdmin(admin.ModelAdmin):
    list_display = ('vehicle_solution', 'inventory_item', 'quantity_used', 'item_cost')
    search_fields = ('inventory_item__item_name',)
    ordering = ('id',)

@admin.register(VehicleSolutionMechanic)
class VehicleSolutionMechanicAdmin(admin.ModelAdmin):
    list_display = ('vehicle_solution', 'mechanic')
    search_fields = ('mechanic__name', 'vehicle_solution__vehicle_issue__reported_issue')
    ordering = ('id',)

