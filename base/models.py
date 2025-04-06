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
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    created_at = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Quotation of Item"

    def __str__(self):
        return f"Inventory ({self.item_name}) on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

class VehicleSolution(models.Model):
    """
    Model representing the repair solution provided for a specific vehicle issue.
    
    This model captures the details of the repair solution, including a detailed 
    description of the work performed, the date the solution was provided, and the 
    total cost of the repair. Multiple mechanics responsible for the repair are 
    associated via the VehicleSolutionMechanic model.
    """
    vehicle_issue = models.OneToOneField(VehicleIssue, on_delete=models.CASCADE, related_name='solution', help_text="The vehicle issue for which this solution is provided.")
    solution_description = models.TextField(help_text="Detailed description of the repair solution provided.")
    solution_date = models.DateTimeField(default=timezone.now, help_text="The date and time when the solution was provided.")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="The total cost incurred for the repair solution.")

    class Meta:
        ordering = ['-solution_date']
        verbose_name = "Vehicle Solution"
        verbose_name_plural = "Vehicle Solutions"

    def __str__(self):
        return f"Solution for {self.vehicle_issue} on {self.solution_date.strftime('%Y-%m-%d')}"

class SolutionItem(models.Model):
    """
    Intermediary model representing the inventory items (such as spare parts) 
    used in a vehicle solution.
    
    This model stores the inventory item used, the quantity consumed during the repair,
    and the cost per unit at the time of usage.
    """
    vehicle_solution = models.ForeignKey(VehicleSolution, on_delete=models.CASCADE, related_name='solution_items', help_text="The vehicle solution in which the inventory item was used.")
    inventory_item = models.ForeignKey(Inventory, on_delete=models.PROTECT, help_text="The inventory item used in the repair.")
    quantity_used = models.PositiveIntegerField(help_text="The quantity of the inventory item used for the repair.")
    item_cost = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, help_text="Cost per unit of the inventory item at the time of usage.")

    class Meta:
        ordering = ['id']
        verbose_name = "Solution Item"
        verbose_name_plural = "Solution Items"

    def __str__(self):
        return f"{self.quantity_used} x {self.inventory_item.item_name} for {self.vehicle_solution}"


class VehicleSolutionMechanic(models.Model):
    """
    Model representing the association between a vehicle solution and a mechanic.
    
    This intermediary model allows associating one or more mechanics (users with a role
    of 'Mechanic') with a given vehicle solution.
    """
    vehicle_solution = models.ForeignKey(VehicleSolution, on_delete=models.CASCADE, related_name='mechanic_assignments', help_text="The vehicle solution to which this mechanic is assigned.")
    mechanic = models.ForeignKey(User, on_delete=models.PROTECT, help_text="The mechanic assigned to the vehicle solution. The user should have a role of 'Mechanic'.")

    class Meta:
        ordering = ['id']
        verbose_name = "Vehicle Solution Mechanic"
        verbose_name_plural = "Vehicle Solution Mechanics"
        unique_together = ('vehicle_solution', 'mechanic')

    def __str__(self):
        return f"Mechanic {self.mechanic.name} assigned to solution for {self.vehicle_solution.vehicle_issue}"

class Settings(models.Model):
    """
    Singleton model to store global application settings such as contact info,
    branding, business hours, tax, and labor rates.
    
    Only one instance of this model should exist.
    """
    name = models.CharField(max_length=255, null=True, blank=True, help_text="Name of the business or workshop.")
    logo = models.ImageField(upload_to='settings/logos/', null=True, blank=True, help_text="Logo image of the business.")
    phone_number = models.CharField(max_length=20, null=True, blank=True, help_text="Primary contact phone number.")
    email = models.EmailField(null=True, blank=True, help_text="Primary contact email address.")
    address = models.TextField(null=True, blank=True, help_text="Physical address of the business.")
    opening_time = models.TimeField(null=True, blank=True, help_text="Business opening time.")
    closing_time = models.TimeField(null=True, blank=True, help_text="Business closing time.")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Applicable tax rate in percentage.")
    labor_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Labor rate per hour.")

    class Meta:
        verbose_name = "Application Settings"
        verbose_name_plural = "Application Settings"

    def save(self, *args, **kwargs):
        if not self.pk and Settings.objects.exists():
            raise ValueError("Only one instance of Settings is allowed.")
        super().save(*args, **kwargs)

    def __str__(self):
        return "Application Settings"

class Quotation(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    vehicle_solution = models.OneToOneField(
        VehicleSolution, 
        on_delete=models.CASCADE,
        related_name="quotation",
        help_text="Vehicle solution this quotation is based on."
    )
    grand_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        help_text="Total cost of the quotation including parts and labor."
    )
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending',
        help_text="Payment status for this quotation."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Quotation generation time.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last updated time.")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Quotation"
        verbose_name_plural = "Quotations"

    def __str__(self):
        return f"Quotation for {self.vehicle_solution.vehicle_issue} - Total: {self.grand_total}"

class QuotedItem(models.Model):
    """
    Represents an inventory item included in the quotation.
    """
    quotation = models.ForeignKey(
        Quotation, 
        on_delete=models.CASCADE, 
        related_name='quoted_items',
        help_text="Quotation this item is part of."
    )
    inventory_item = models.ForeignKey(
        Inventory, 
        on_delete=models.PROTECT, 
        help_text="Inventory item used."
    )
    quantity_used = models.PositiveIntegerField(help_text="Quantity of item used in the solution.")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Unit price at time of quotation.")
    item_total = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total cost (quantity * unit price).")

    class Meta:
        ordering = ['id']
        verbose_name = "Quoted Item"
        verbose_name_plural = "Quoted Items"

    def __str__(self):
        return f"{self.quantity_used} x {self.inventory_item.item_name}"

class QuotedMechanic(models.Model):
    """
    Represents a mechanic's contribution and share of labor in the quotation.
    """
    quotation = models.ForeignKey(
        Quotation, 
        on_delete=models.CASCADE, 
        related_name='quoted_mechanics',
        help_text="Quotation this mechanic is part of."
    )
    mechanic = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        limit_choices_to={'role': 'Mechanic'},
        help_text="Mechanic assigned to the solution."
    )
    labor_share = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Calculated labor compensation for this mechanic."
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Quoted Mechanic"
        verbose_name_plural = "Quoted Mechanics"
        unique_together = ('quotation', 'mechanic')

    def __str__(self):
        return f"{self.mechanic.name} - Labor: {self.labor_share}"