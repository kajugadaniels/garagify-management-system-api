from account.models import *
from django.db import models
from django.conf import settings
from django.utils import timezone

class Vehicle(models.Model):
    """
    Model representing a customer's vehicle brought in for repairs.
    
    Stores detailed information about the vehicle including manufacturer,
    model, year, license details, VIN, mileage, and timestamps.
    """
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vehicles", help_text="The customer who owns the vehicle.")
    make = models.CharField(max_length=100, null=True, blank=True, help_text="Manufacturer of the vehicle (e.g., Toyota, Ford, etc.).")
    model = models.CharField(max_length=100, null=True, blank=True, help_text="Model of the vehicle (e.g., Camry, F-150, etc.).")
    year = models.PositiveIntegerField(null=True, blank=True, help_text="Year the vehicle was manufactured.")
    color = models.CharField(max_length=50, null=True, blank=True, help_text="Color of the vehicle.")
    license_plate = models.CharField(max_length=20, unique=True, null=True, blank=True, help_text="Unique license plate number of the vehicle.")
    vin = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Vehicle Identification Number (VIN).")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="Timestamp when the vehicle record was created.")
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="Timestamp when the vehicle record was last updated.")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"

    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"

class VehicleIssue(models.Model):
    """
    Model representing an issue reported for a specific vehicle.
    
    Contains details of the issue as reported by the customer, diagnosis,
    repair notes, repair status, and estimated repair cost.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, blank=True, null=True, on_delete=models.CASCADE, related_name="issues", help_text="The vehicle that has the reported issue.")
    reported_issue = models.TextField(blank=True, null=True, help_text="Description of the issue as reported by the customer.")
    diagnosed_issue = models.TextField(blank=True, null=True, help_text="Diagnosis details provided by a mechanic.")
    repair_notes = models.TextField(blank=True, null=True, help_text="Notes regarding repair work performed on the vehicle.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending", help_text="Current status of the vehicle issue.")
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Estimated cost for the repair work.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the issue was reported.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the issue details were last updated.")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Vehicle Issue"
        verbose_name_plural = "Vehicle Issues"

    def __str__(self):
        return f"Issue for {self.vehicle} - Status: {self.status}"

class Inventory(models.Model):
    ITEM_TYPES = (
        ('Spare Part', 'Spare Part'),
        ('Tools', 'Tools'),
        ('Materials', 'Materials'),
    )
    item_name = models.CharField(max_length=255, null=True, blank=True)
    item_type = models.CharField(max_length=30, choices=ITEM_TYPES, null=True, blank=True)
    quantity = models.CharField(max_length=255, null=True, blank=True)
    unit_price = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    created_at = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Quotation of Item"

    def __str__(self):
        return f"Inventory ({self.item_name}) on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"