from account.models import *
from django.db import models
from django.utils import timezone

class Vehicle(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    model = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    color = models.PositiveIntegerField(null=True, blank=True)
    plate_number = models.PositiveIntegerField(unique=True)
    created_at = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Vehicles"

    def __str__(self):
        return f"Vehicle({self.model}) by ({self.customer.name}) on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

class VehicleCheckIn(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
    )
    received_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    arrival_date = models.DateField(default=timezone.now)
    created_at = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Vehicles Issues"

    def __str__(self):
        return f"Vehicle ({self.vehicle.model}) on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

class VehicleNoteProperty(models.Model):
    vehicle_check_in = models.ForeignKey(
        VehicleCheckIn,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Vehicle Note Properties"

    def __str__(self):
        return self.name

class VehicleIssue(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
    )
    issue_reported = models.CharField(max_length=255, null=True, blank=True)
    issue_diagnosed = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    created_at = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Vehicles Issues"

    def __str__(self):
        return f"Vehicle ({self.vehicle.model}) on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class Quotation(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
    )
    mechanic = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quotations_by_mechanic"
    )
    total_cost = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Pending", null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quotations_created_by"
    )
    created_at = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Quotations"

    def __str__(self):
        return f"Vehicle ({self.vehicle.model}) on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

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

class QuotationItem(models.Model):
    ITEM_TYPES = (
        ('Spare Part', 'Spare Part'),
        ('Tools', 'Tools'),
        ('Materials', 'Materials'),
    )

    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
    )

    item = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
    )
    quantity = models.CharField(max_length=255, null=True, blank=True)
    unit_price = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    created_at = models.DateField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Quotation of Item"

    def __str__(self):
        return f"Quotation item ({self.item.item_name}) on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"