from base.models import *
from account.models import *
from account.serializers import *
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class InventorySerializer(serializers.ModelSerializer):
    created_by = UserSerializer()

    class Meta:
        model = Inventory
        fields = ('item_name', 'item_type', 'quantity', 'unit_price', 'created_by')