from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from cryptography.fernet import Fernet
from django.db import models
from djongo.models import ArrayField, EmbeddedField
from Tara.settings.default import *


KEY = b'zSwtDDLJp6Qkb9CMCJnVeOzAeSJv-bA3VYNCy5zM-b4='
class EncryptedField(models.Field):
    def __init__(self, *args, **kwargs):
        self.cipher = Fernet(KEY)
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """Override to encrypt data before saving to the database"""
        if value is None:
            return None
        return self.cipher.encrypt(value.encode()).decode()

    def from_db_value(self, value, expression, connection):
        """Override to decrypt data when retrieving from the database"""
        if value is None:
            return None
        return self.cipher.decrypt(value.encode()).decode()


class CustomAccountManager(BaseUserManager):
    def create_user(self, email=None, password=None, mobile_number=None, created_by=None, **extra_fields):
        # Normalize email if provided
        email = self.normalize_email(email) if email else None

        # Ensure at least one identifier is provided
        if not email and not mobile_number:
            raise ValueError("At least one of email or mobile number must be provided.")

        # Check for existing users
        if email and self.model.objects.filter(email=email).exists():
            raise ValueError("A user with this email already exists.")
        if mobile_number and self.model.objects.filter(mobile_number=mobile_number).exists():
            raise ValueError("A user with this mobile number already exists.")

        # Dynamically set email_or_mobile
        email_or_mobile = email or mobile_number

        # Create user instance
        user = self.model(
            email=email,
            mobile_number=mobile_number,
            email_or_mobile=email_or_mobile,
            created_by=created_by,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        # Set fields for superuser creation
        extra_fields.setdefault('user_type', 'superuser')
        return self.create_user(email=email, password=password, **extra_fields)


class AddressModel(models.Model):
    address_line1 = models.TextField(null=True, blank=False)
    address_line2 = models.TextField(null=True, blank=False)
    address_line3 = models.CharField(max_length=255, blank=True, null=True)
    pinCode = models.IntegerField(max_length=6, blank=True, null=True)
    state = models.CharField(max_length=20, null=True, blank=False)
    city = models.CharField(max_length=20, null=True, blank=False)
    country = models.CharField(max_length=20, null=True, blank=False)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('cafirm', 'Chartered Accountant Firm'),
        ('business_or_corporate', 'Business/Corporate'),
        ('superuser', 'Superuser')
    ]

    email_or_mobile = models.CharField(max_length=120, unique=True, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    otp = models.IntegerField(null=True)
    user_type = models.CharField(
        max_length=40,
        choices=USER_TYPE_CHOICES,
        default='individual'  # Default value set to 'individual'
    )
    created_by = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users'
    )

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email_or_mobile'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email_or_mobile or "User"


class UserKYC(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # ForeignKey to User
    # Encrypted Fields for sensitive data
    name = models.CharField(max_length=40, blank=False, null=False)
    pan_number = EncryptedField(max_length=20, blank=True, null=True)  # Encrypted PAN
    aadhaar_number = EncryptedField(max_length=20, blank=True, null=True)  # Encrypted Aadhaar
    date = models.DateField(null=True, blank=True)
    # Fields specific to CA Firm
    icai_number = models.CharField(max_length=15, blank=True, null=True)  # Only for CA Firm
    address = EmbeddedField(model_container=AddressModel, default={})

    def __str__(self):
        return f"{self.user.email} - {self.user.user_type}"


class FirmKYC(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firm_name = models.CharField(max_length=255, blank=True, null=True)
    firm_registration_number = models.CharField(max_length=40, blank=True, null=True)
    firm_email = models.EmailField(unique=True, null=True, blank=True)
    firm_mobile_number = models.IntegerField()
    number_of_firm_partners = models.IntegerField()
    address = EmbeddedField(model_container=AddressModel, default={})

    def __str__(self):
        return f"{self.user.email} - {self.firm_registration_number}"





