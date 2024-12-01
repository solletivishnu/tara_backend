from rest_framework import serializers
from .models import User, UserDetails, FirmKYC, AddressModel

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Either email and password OR mobile number and password must be provided.
    """
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    email = serializers.EmailField(required=False, allow_null=True)
    mobile_number = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('email', 'mobile_number', 'password')

    def validate(self, attrs):
        email = attrs.get('email')
        mobile_number = attrs.get('mobile_number')

        # Ensure only one of email or mobile number is provided
        if email and mobile_number:
            raise serializers.ValidationError("Provide either email or mobile number, not both.")
        if not email and not mobile_number:
            raise serializers.ValidationError("At least one of email or mobile number must be provided.")

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})

            # Check if mobile number is already registered
        if mobile_number and User.objects.filter(mobile_number=mobile_number).exists():
            raise serializers.ValidationError({"mobile_number": "A user with this mobile number already exists."})

        return attrs

    def create(self, validated_data):
        # Pass default None for missing fields
        email = validated_data.get('email', None)
        mobile_number = validated_data.get('mobile_number', None)
        password = validated_data.get('password')

        # Use custom manager to create the user
        user = User.objects.create_user(
            email=email,
            password=password,
            mobile_number=mobile_number
        )
        return user


class UserActivationSerializer(serializers.Serializer):
    token = serializers.CharField()


class AddressSerializer(serializers.Serializer):
    address_line1 = serializers.CharField(max_length=255, required=False)
    address_line2 = serializers.CharField(max_length=255, required=False)
    address_line3 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    pinCode = serializers.IntegerField(required=False, allow_null=True)
    state = serializers.CharField(max_length=20, required=False)
    city = serializers.CharField(max_length=20, required=False)
    country = serializers.CharField(max_length=20, required=False)


class UserDetailsSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = UserDetails
        fields = [
            'user', 'pan_number', 'aadhaar_number', 'dob', 'icai_number', 'address', 'user_name',
        ]
        read_only_fields = ['user']

    def validate(self, data):
        """
        Validate data for specific cases.
        """
        user_type = data.get('user_type', 'individual')
        icai_number = data.get('icai_number')

        # Ensure `icai_number` is None for individuals
        if user_type == 'individual' and icai_number is not None:
            raise serializers.ValidationError({
                "icai_number": "ICAI Number must be None for individual user type."
            })

        # Ensure `icai_number` is provided for CA firms
        if user_type == 'cafirm' and not icai_number:
            raise serializers.ValidationError({
                "icai_number": "ICAI Number is required for Chartered Accountant Firm."
            })

        return data

    def create(self, validated_data):
        address_data = validated_data.pop('address', {})
        user_details = UserDetails.objects.create(**validated_data)
        user_details.address = address_data
        return user_details

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.address.update(address_data)
        instance.save()
        return instance


class FirmKYCSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = FirmKYC
        fields = [
            'user', 'firm_name', 'firm_registration_number', 'firm_email', 'firm_mobile_number',
            'number_of_firm_partners', 'address'
        ]
        read_only_fields = ['user']
