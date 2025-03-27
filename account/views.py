import random
from account.serializers import *
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny

class LoginView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  # Use get_serializer method
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(username=email, password=password)

        if user:
            # Delete old token and generate a new one
            Token.objects.filter(user=user).delete()
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,  # Use your user serializer if needed
                'message': 'Login successful.'
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_400_BAD_REQUEST)

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

class PasswordResetRequestView(APIView):
    """
    Initiate the password reset process by sending a 5-digit OTP to the user's email address.
    """
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