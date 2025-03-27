from base.models import *
from account.models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'phone_number', 'image', 'role', 'password', 'confirm_password')

    def validate(self, data):
        """
        Ensure that the password and confirm_password fields match.
        """
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        
        if password != confirm_password:
            raise serializers.ValidationError({"detail": "Passwords do not match."})
        
        return data

class InventorySerializer(serializers.ModelSerializer):
    created_by = UserSerializer()

    class Meta:
        model = Inventory
        fields = ('item_name', 'item_type', 'quantity', 'unit_price', 'created_by')