from rest_framework import serializers
from .models import User, UserKYC, FirmKYC, AddressModel

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Either email and password OR mobile number and password must be provided.
    """
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    email = serializers.EmailField(required=False, allow_null=True)
    mobile_number = serializers.CharField(required=False, allow_null=True)
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('email', 'mobile_number', 'password', 'created_by')

    def validate(self, attrs):
        email = attrs.get('email')
        mobile_number = attrs.get('mobile_number')

        # Ensure only one of email or mobile number is provided
        if email and mobile_number:
            raise serializers.ValidationError("Provide either email or mobile number, not both.")
        if not email and not mobile_number:
            raise serializers.ValidationError("At least one of email or mobile number must be provided.")

        # Check if email is already registered
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})

        # Check if mobile number is already registered
        if mobile_number and User.objects.filter(mobile_number=mobile_number).exists():
            raise serializers.ValidationError({"mobile_number": "A user with this mobile number already exists."})

        return attrs

    def create(self, validated_data):
        # Extract created_by if present; default to None
        created_by = validated_data.pop('created_by', None)
        email = validated_data.get('email', None)
        mobile_number = validated_data.get('mobile_number', None)
        password = validated_data.get('password')

        # Create the user with the provided data
        user = User.objects.create_user(
            email=email,
            password=password,
            mobile_number=mobile_number,
        )

        # Assign created_by to the user
        if created_by:
            user.created_by = created_by
            user.save()

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


class UsersKYCSerializer(serializers.ModelSerializer):
    address = AddressSerializer(default={}, required=False)  # Nested serializer for address

    class Meta:
        model = UserKYC
        fields = [
            'user', 'pan_number', 'aadhaar_number', 'date', 'icai_number', 'address', 'name', 'have_firm'
        ]
        read_only_fields = ['user']  # Prevent modification of `user` field

    def validate(self, data):
        """
        Validate data based on the user type.
        """
        user = self.context['request'].user  # Accessing the user from the request context

        # Ensure user_type exists in the user model
        if not hasattr(user, 'user_type'):
            raise serializers.ValidationError("User type is missing.")

        user_type = user.user_type
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
        """
        Create a new `UserKYC` instance.
        """
        # Check if 'address' is present in validated_data
        if 'address' not in validated_data:
            # If not present, set default address values
            validated_data['address'] = {
                "address_line1": None,
                "address_line2": None,
                "address_line3": None,
                "pinCode": None,
                "state": None,
                "city": None,
                "country": None
            }

        # Create and save the UserKYC instance
        user_details = UserKYC.objects.create(**validated_data)
        return user_details

    def update(self, instance, validated_data):
        """
        Update an existing `UserDetails` instance.
        """
        # Extract and handle address data
        address_data = validated_data.pop('address', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update the embedded address data if provided
        if address_data:
            instance.address.update(address_data)

        instance.save()
        return instance


class FirmKYCSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)

    class Meta:
        model = FirmKYC
        fields = [
            'user', 'firm_name', 'firm_registration_number', 'firm_email', 'firm_mobile_number',
            'number_of_firm_partners', 'address'
        ]
        read_only_fields = ['user']

    def create(self, validated_data):
        """
        Create a new `UserKYC` instance.
        """
        # Check if 'address' is present in validated_data
        if 'address' not in validated_data:
            # If not present, set default address values
            validated_data['address'] = {
                "address_line1": None,
                "address_line2": None,
                "address_line3": None,
                "pinCode": None,
                "state": None,
                "city": None,
                "country": None
            }

        # Create and save the UserKYC instance
        user_details = FirmKYC.objects.create(**validated_data)

        return user_details


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email_or_mobile', 'email', 'mobile_number', 'user_type']
        # You can modify this list based on the fields you want to allow updating

    def update(self, instance, validated_data):
        # Perform the actual update for the instance
        return super().update(instance, validated_data)
