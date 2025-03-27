import re
from account.models import *
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

def validatePasswordComplexity(password):
    """
    Validates that the password meets the complexity requirements:
    - At least 8 characters long.
    - Contains at least one capital letter.
    - Contains at least one number.
    - Contains at least one special character.
    """
    if len(password) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise serializers.ValidationError("Password must contain at least one capital letter.")
    if not re.search(r"\d", password):
        raise serializers.ValidationError("Password must contain at least one number.")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        raise serializers.ValidationError("Password must contain at least one special character.")
    return password

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        if not identifier:
            raise serializers.ValidationError("Login (email, phone_number, or username) is required.")
        
        # Try to find the user by email, phone_number, or username
        User = get_user_model()
        user = None

        # Check if the login is a valid email
        if "@" in identifier:
            user = User.objects.filter(email=identifier).first()
        
        # Check if the login is a valid phone number
        if not user:
            user = User.objects.filter(phone_number=identifier).first()
        
        # Check if the login is a valid username
        if not user:
            user = User.objects.filter(username=identifier).first()

        if not user:
            raise serializers.ValidationError("User with the provided identifier does not exist.")

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password.")

        attrs['user'] = user
        return attrs

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

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text="Enter the email address associated with your account."
    )

    def validate_email(self, value):
        User = get_user_model()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text="Enter your email address."
    )
    otp = serializers.CharField(
        max_length=5,
        help_text="Enter the 5-digit OTP sent to your email."
    )
    new_password = serializers.CharField(
        write_only=True,
        help_text="Enter your new password."
    )
    confirm_new_password = serializers.CharField(
        write_only=True,
        help_text="Confirm your new password."
    )

    def validate(self, attrs):
        """
        Validates OTP, new password match, and ensures the new password meets complexity requirements.
        """
        email = attrs.get('email')
        otp = attrs.get('otp')
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')

        if new_password != confirm_new_password:
            raise serializers.ValidationError("New password and confirm password do not match.")

        # Validate new password complexity
        validatePasswordComplexity(new_password)

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")

        if user.reset_otp != otp:
            raise serializers.ValidationError("Invalid OTP provided.")

        if user.otp_created_at:
            if timezone.now() - user.otp_created_at > timedelta(minutes=10):
                raise serializers.ValidationError("OTP has expired. Please request a new one.")
        else:
            raise serializers.ValidationError("OTP was not generated. Please request a new one.")

        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.reset_otp = ""
        user.otp_created_at = None
        user.save()
        return user