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
