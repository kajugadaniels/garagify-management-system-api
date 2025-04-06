from base.models import *
from account.models import *
from rest_framework import serializers
from decimal import Decimal, InvalidOperation
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'phone_number', 'image', 'role')

class VehicleSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Vehicle
        fields = ('id', 'customer', 'customer_id', 'make', 'model', 'year', 'color', 'license_plate', 'vin', 'created_at', 'updated_at')

class VehicleSolutionMechanicSerializer(serializers.ModelSerializer):
    mechanic_id = serializers.IntegerField(write_only=True)
    mechanic = UserSerializer(read_only=True)

    class Meta:
        model = VehicleSolutionMechanic
        fields = ['id', 'mechanic', 'mechanic_id']

    def create(self, validated_data):
        # Directly create the mechanic assignment
        return VehicleSolutionMechanic.objects.create(**validated_data)

class SolutionItemSerializer(serializers.ModelSerializer):
    inventory_item = serializers.SerializerMethodField(read_only=True)
    inventory_item_id = serializers.IntegerField(write_only=True)
    item_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SolutionItem
        fields = ['id', 'inventory_item', 'inventory_item_id', 'quantity_used', 'item_cost', 'item_total']

    def get_inventory_item(self, obj):
        # Minimal representation of inventory item details
        return {
            "id": obj.inventory_item.id,
            "item_name": obj.inventory_item.item_name,
            "quantity": obj.inventory_item.quantity,
            "unit_price": obj.inventory_item.unit_price,
        }

    def get_item_total(self, obj):
        # Calculate total based on unit_price and quantity_used
        try:
            unit_price = float(obj.inventory_item.unit_price)
        except (ValueError, TypeError):
            unit_price = 0.0
        return unit_price * obj.quantity_used

    def validate_quantity_used(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity used must be a positive integer.")
        return value

    def create(self, validated_data):
        inventory_item_id = validated_data.pop('inventory_item_id')
        quantity_used = validated_data.get('quantity_used')
        try:
            inventory_item = Inventory.objects.get(id=inventory_item_id)
        except Inventory.DoesNotExist:
            raise serializers.ValidationError("Inventory item not found.")

        try:
            available_quantity = int(inventory_item.quantity)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Inventory quantity is invalid.")

        if quantity_used > available_quantity:
            raise serializers.ValidationError(f"Not enough quantity available. Only {available_quantity} left.")

        # Deduct the quantity used from the inventory
        inventory_item.quantity = str(available_quantity - quantity_used)
        inventory_item.save()

        validated_data['inventory_item'] = inventory_item
        return SolutionItem.objects.create(**validated_data)

    def update(self, instance, validated_data):
        new_quantity = validated_data.get('quantity_used', instance.quantity_used)
        inventory_item = instance.inventory_item
        try:
            available_quantity = int(inventory_item.quantity)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Inventory quantity is invalid.")

        # Restore the previous quantity before applying update
        available_quantity += instance.quantity_used
        delta = new_quantity - instance.quantity_used

        if delta > 0:
            # Check if additional quantity required is available
            if delta > available_quantity:
                raise serializers.ValidationError(f"Not enough quantity available. Only {available_quantity} left.")
            available_quantity -= delta
        else:
            # Negative delta means quantity reduced, so add back to inventory
            available_quantity -= delta  # subtracting a negative number

        inventory_item.quantity = str(available_quantity)
        inventory_item.save()

        instance.quantity_used = new_quantity
        instance.item_cost = validated_data.get('item_cost', instance.item_cost)
        instance.save()
        return instance

class VehicleSolutionSerializer(serializers.ModelSerializer):
    solution_items = SolutionItemSerializer(many=True, required=False)
    mechanic_assignments = VehicleSolutionMechanicSerializer(many=True, required=False)
    grand_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VehicleSolution
        fields = [
            'id',
            'vehicle_issue',
            'solution_description',
            'solution_date',
            'total_cost',
            'solution_items',
            'mechanic_assignments',
            'grand_total'
        ]

    def get_grand_total(self, obj):
        total = 0.0
        for item in obj.solution_items.all():
            try:
                unit_price = float(item.inventory_item.unit_price)
            except (ValueError, TypeError):
                unit_price = 0.0
            total += unit_price * item.quantity_used
        return total

    def create(self, validated_data):
        solution_items_data = validated_data.pop('solution_items', [])
        mechanics_data = validated_data.pop('mechanic_assignments', [])
        vehicle_solution = VehicleSolution.objects.create(**validated_data)

        # Create nested solution items
        for item_data in solution_items_data:
            serializer = SolutionItemSerializer(data=item_data, context=self.context)
            serializer.is_valid(raise_exception=True)
            serializer.save(vehicle_solution=vehicle_solution)

        # Create nested mechanic assignments
        for mech_data in mechanics_data:
            serializer = VehicleSolutionMechanicSerializer(data=mech_data, context=self.context)
            serializer.is_valid(raise_exception=True)
            serializer.save(vehicle_solution=vehicle_solution)

        return vehicle_solution

    def update(self, instance, validated_data):
        solution_items_data = validated_data.pop('solution_items', [])
        mechanics_data = validated_data.pop('mechanic_assignments', [])

        # Update basic fields of vehicle solution
        instance.solution_description = validated_data.get('solution_description', instance.solution_description)
        instance.solution_date = validated_data.get('solution_date', instance.solution_date)
        instance.total_cost = validated_data.get('total_cost', instance.total_cost)
        instance.save()

        # Restore inventory for existing solution items before update
        for item in instance.solution_items.all():
            inventory_item = item.inventory_item
            try:
                available_quantity = int(inventory_item.quantity)
            except (TypeError, ValueError):
                available_quantity = 0
            inventory_item.quantity = str(available_quantity + item.quantity_used)
            inventory_item.save()
        # Delete old solution items and recreate from new data
        instance.solution_items.all().delete()
        for item_data in solution_items_data:
            serializer = SolutionItemSerializer(data=item_data, context=self.context)
            serializer.is_valid(raise_exception=True)
            serializer.save(vehicle_solution=instance)

        # Update mechanic assignments: Clear and recreate
        instance.mechanic_assignments.all().delete()
        for mech_data in mechanics_data:
            serializer = VehicleSolutionMechanicSerializer(data=mech_data, context=self.context)
            serializer.is_valid(raise_exception=True)
            serializer.save(vehicle_solution=instance)

        return instance

class VehicleIssueSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True)
    solution = VehicleSolutionSerializer(read_only=True, required=False)

    class Meta:
        model = VehicleIssue
        fields = (
            'id',
            'vehicle',
            'vehicle_id',
            'reported_issue',
            'diagnosed_issue',
            'repair_notes',
            'status',
            'estimated_cost',
            'created_at',
            'updated_at',
            'solution'
        )
        read_only_fields = ('created_at', 'updated_at')

class VehicleSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    vehicle_issues = VehicleIssueSerializer(many=True, read_only=True, source='issues')

    class Meta:
        model = Vehicle
        fields = (
            'id', 
            'customer', 
            'customer_id', 
            'make', 
            'model', 
            'year', 
            'color', 
            'license_plate', 
            'vin', 
            'created_at', 
            'updated_at',
            'vehicle_issues'
        )

class UserSerializer(serializers.ModelSerializer):
    vehicles = VehicleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'phone_number', 'image', 'role', 'created_at', 'vehicles')

class CustomerSerializer(serializers.ModelSerializer):
    vehicles = VehicleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'phone_number', 'image', 'role', 'address', 'created_at', 'vehicles')

class InventorySerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    total = serializers.SerializerMethodField(read_only=True)
    # Retrieve related solution items using the default reverse accessor "solutionitem_set"
    solution_items = SolutionItemSerializer(many=True, read_only=True, source='solutionitem_set')

    class Meta:
        model = Inventory
        fields = ('id', 'item_name', 'item_type', 'quantity', 'unit_price', 'created_by', 'created_by_details', 'total', 'solution_items')

    def get_total(self, obj):
        try:
            qty = float(obj.quantity) if obj.quantity is not None else 0
        except (TypeError, ValueError):
            qty = 0
        try:
            price = float(obj.unit_price) if obj.unit_price is not None else 0
        except (TypeError, ValueError):
            price = 0
        return qty * price

class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = '__all__'

class QuotedItemSerializer(serializers.ModelSerializer):
    inventory_item = serializers.StringRelatedField()

    class Meta:
        model = QuotedItem
        fields = ['id', 'inventory_item', 'quantity_used', 'unit_price', 'item_total']


class QuotedMechanicSerializer(serializers.ModelSerializer):
    mechanic = UserSerializer(read_only=True)

    class Meta:
        model = QuotedMechanic
        fields = ['id', 'mechanic', 'labor_share']


class QuotationSerializer(serializers.ModelSerializer):
    vehicle_solution = serializers.PrimaryKeyRelatedField(read_only=True)
    quoted_items = QuotedItemSerializer(many=True, read_only=True)
    quoted_mechanics = QuotedMechanicSerializer(many=True, read_only=True)

    class Meta:
        model = Quotation
        fields = [
            'id',
            'vehicle_solution',
            'grand_total',
            'quoted_items',
            'quoted_mechanics',
            'created_at',
            'updated_at',
        ]