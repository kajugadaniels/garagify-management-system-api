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
    color = models.PositiveIntegerField(max_length=255, null=True, blank=True)
    plate_number = models.PositiveIntegerField(unique=True)
    created_at = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Vehicle({self.model}) by ({self.customer.name}) on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"