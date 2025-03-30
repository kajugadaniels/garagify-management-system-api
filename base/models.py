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