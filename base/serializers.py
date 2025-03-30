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