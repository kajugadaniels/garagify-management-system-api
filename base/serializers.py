from base.models import *
from account.models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ('item_name', 'item_type', 'quantity', 'unit_price')