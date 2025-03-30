from base.models import *
from account.models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'phone_number', 'image', 'role')

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'phone_number', 'image', 'role')

class VehicleSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Vehicle
        fields = ('id', 'customer', 'customer_id', 'make', 'model', 'year', 'color', 'license_plate', 'vin', 'created_at', 'updated_at')

class VehicleIssueSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = VehicleIssue
        fields = ('id', 'vehicle', 'vehicle_id', 'reported_issue', 'diagnosed_issue', 'repair_notes', 'status', 'estimated_cost', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class InventorySerializer(serializers.ModelSerializer):
    created_by = UserSerializer()

    class Meta:
        model = Inventory
        fields = ('item_name', 'item_type', 'quantity', 'unit_price', 'created_by')

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

    class Meta:
        model = SolutionItem
        fields = ['id', 'inventory_item', 'inventory_item_id', 'quantity_used', 'item_cost']

    def get_inventory_item(self, obj):
        # Minimal representation of inventory item details
        return {
            "id": obj.inventory_item.id,
            "item_name": obj.inventory_item.item_name,
            "quantity": obj.inventory_item.quantity,
            "unit_price": obj.inventory_item.unit_price,
        }

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
            available_quantity -= delta  # (subtracting a negative adds to available_quantity)

        inventory_item.quantity = str(available_quantity)
        inventory_item.save()

        instance.quantity_used = new_quantity
        instance.item_cost = validated_data.get('item_cost', instance.item_cost)
        instance.save()
        return instance

class VehicleSolutionSerializer(serializers.ModelSerializer):
    solution_items = SolutionItemSerializer(many=True, required=False)
    mechanic_assignments = VehicleSolutionMechanicSerializer(many=True, required=False)

    class Meta:
        model = VehicleSolution
        fields = [
            'id',
            'vehicle_issue',
            'solution_description',
            'solution_date',
            'total_cost',
            'solution_items',
            'mechanic_assignments'
        ]

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