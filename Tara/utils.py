from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from user_management.models import User  # Assuming your user model is in user_management app
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email_or_username = attrs.get("username") or attrs.get("email")
        password = attrs.get("password")

        # Check if the user exists using email or username
        try:
            user = User.objects.get(email=email_or_username)  # First check email
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=email_or_username)  # Then check username
            except User.DoesNotExist:
                raise AuthenticationFailed("No user found with the provided email or username.")

        # Check if the password is correct
        if not user.check_password(password):  # Use built-in check_password
            raise AuthenticationFailed("Invalid password. Please try again.")

        # Check if the user is active
        if not user.is_active:
            raise AuthenticationFailed("User account is not active. Please verify your email.")

        # Generate tokens
        refresh = self.get_token(user)

        # Return the tokens and user info
        return {
            'id': user.id,
            'email': user.email,
            'refresh': str(refresh),
            'token': str(refresh.access_token),
        }


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            # Validate the request data
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        # Return the validated data
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
