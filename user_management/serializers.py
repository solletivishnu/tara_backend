from rest_framework import serializers
from .models import User  # Ensure your custom User model is imported


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # Ensures password isn’t sent back in responses

    def validate_email(self, value):
        print("validate_email called with:", value)  # Debug line
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserActivationSerializer(serializers.Serializer):
    token = serializers.CharField()