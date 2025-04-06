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
    list_display = ('vehicle', 'status', 'estimated_cost', 'created_at', 'view_actions')
    search_fields = ('vehicle__license_plate', 'reported_issue', 'diagnosed_issue')
    list_filter = ('status',)
    ordering = ('-created_at',)

    def view_actions(self, obj):
        edit_url = reverse('admin:base_vehicleissue_change', args=[obj.pk])
        delete_url = reverse('admin:base_vehicleissue_delete', args=[obj.pk])
        return format_html(f'<a class="button" href="{edit_url}">Edit</a> <a class="button" style="color:red;" href="{delete_url}">Delete</a>')
    view_actions.short_description = 'Actions'

