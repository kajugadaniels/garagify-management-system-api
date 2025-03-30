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

class InventorySerializer(serializers.ModelSerializer):
    created_by = UserSerializer()

    class Meta:
        model = Inventory
        fields = ('item_name', 'item_type', 'quantity', 'unit_price', 'created_by')