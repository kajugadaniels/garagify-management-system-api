import random
from account.serializers import *
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny

class LoginView(APIView):
    """
    Handle login using an identifier (email, phone number, or username) and password.
    Before validating the full login data, this view checks the user's role.
    Only users with roles "Admin", "Mechanic", "Storekeeper", or "Cashier" are allowed.
    If a user with a "Customer" role attempts to login, an error is returned.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # First, ensure that the identifier is provided
        identifier = request.data.get('identifier', '').strip()
        if not identifier:
            return Response({"error": "Identifier (email, phone number, or username) is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        user = None

        # Try to locate the user by email (case-insensitive)
        if "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).first()

        # If not found by email, try phone number
        if not user:
            user = User.objects.filter(phone_number=identifier).first()

        # If still not found, try username (case-insensitive)
        if not user:
            user = User.objects.filter(username__iexact=identifier).first()

        if not user:
            return Response({"error": "No user found with the provided identifier."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Role check: only allow specified roles
        allowed_roles = ["Admin", "Mechanic", "Storekeeper", "Cashier"]
        if user.role not in allowed_roles:
            return Response(
                {"error": "Users with the role 'Customer' are not allowed to login."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Now proceed with full validation using the serializer
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Validation error", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # After validation, check if the provided password is correct
        password = serializer.validated_data['password']
        if not user.check_password(password):
            return Response(
                {"error": "Incorrect password. Please check your credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Successful authentication: Invalidate any existing token and generate a new one
        Token.objects.filter(user=user).delete()
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'Login successful.'
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
            return Response({
                "message": "Logout successful."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"An error occurred during logout: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateUserView(generics.UpdateAPIView):
    """
    API view to update user profile details.
    - Automatically hashes the password if updated.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """
        Retrieve the current user instance.
        """
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Update user details, including password, if provided.
        """
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "user": serializer.data,
            "message": "Account updated successfully."
        }, status=status.HTTP_200_OK)

class UpdatePasswordView(APIView):
    """
    This view handles password change for the logged-in user.
    After successfully changing the password, the user will be logged out (token invalidated).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user  # Get the currently authenticated user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_new_password = request.data.get("confirm_new_password")

        if not old_password or not new_password or not confirm_new_password:
            return Response({"detail": "Old password, new password, and confirmation are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if old password is correct
        if not user.check_password(old_password):
            return Response({"detail": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure new password and confirmation match
        if new_password != confirm_new_password:
            return Response({"detail": "New password and confirm new password do not match."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the password
        user.set_password(new_password)
        user.save()

        # Invalidate the current token by deleting it
        Token.objects.filter(user=user).delete()

        return Response({"detail": "Password updated successfully. You have been logged out."}, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    """
    Initiate the password reset process by sending a 5-digit OTP to the user's email address.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            User = get_user_model()
            user = User.objects.get(email=email)
            # Generate a 5-digit OTP
            otp = str(random.randint(10000, 99999))
            user.reset_otp = otp
            user.otp_created_at = timezone.now()
            user.save()

            subject = "Password Reset OTP"
            message = f"Your OTP for password reset is: {otp}"
            from_email = None
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list)

            return Response({"detail": "OTP sent to your email address."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    """
    Confirm the password reset by validating the OTP and setting the new password.
    After successfully resetting the password, sends a confirmation email to the user.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Send confirmation email after successful password reset.
            subject = "Password Changed Successfully"
            message = f"Hi {user.name or 'there'}, your password has been changed successfully. If you did not perform this action, please contact support immediately."
            from_email = None
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list)
            return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)