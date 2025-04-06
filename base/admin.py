from base.models import *
from django.urls import reverse
from django.contrib import admin
from django.utils.html import format_html

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('customer', 'make', 'model', 'year', 'license_plate', 'vin', 'created_at', 'view_actions')
    search_fields = ('make', 'model', 'license_plate', 'vin')
    list_filter = ('make', 'year')
    ordering = ('-created_at',)

    def view_actions(self, obj):
        edit_url = reverse('admin:base_vehicle_change', args=[obj.pk])
        delete_url = reverse('admin:base_vehicle_delete', args=[obj.pk])
        return format_html(f'<a class="button" href="{edit_url}">Edit</a> <a class="button" style="color:red;" href="{delete_url}">Delete</a>')
    view_actions.short_description = 'Actions'
    view_actions.allow_tags = True

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

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Prevent adding more than one Settings instance
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton Settings instance
        return False

    list_display = ('name', 'phone_number', 'email', 'tax_rate', 'labor_rate')
