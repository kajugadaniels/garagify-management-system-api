import re
from account.models import *
from django.db.models import Q
from datetime import timedelta
from rest_framework import serializers
from django.contrib.auth.models import Permission

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

class UserSerializer(serializers.ModelSerializer):
    user_permissions = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'id', 'name', 'email', 'phone_number', 'role', 'image', 'password', 'user_permissions'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_user_permissions(self, obj):
        """Retrieve the user's direct permissions."""
        return obj.get_all_permissions()

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        """
        Update user details and hash the password if provided.
        """
        old_role = instance.role
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)

        # Handle image upload separately if provided
        if 'image' in validated_data:
            instance.image = validated_data.pop('image')

        # If a password is provided, hash it using set_password
        if password:
            instance.set_password(password)
            instance.save()

        # Update the remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance