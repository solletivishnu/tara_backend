from django.db import models
from Tara.settings.default import *
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField
from .helpers import *
from usermanagement.models import Users, ServiceRequest
from servicetasks.models import ServiceTask
from django.db.models.signals import post_save
from django.dispatch import receiver
from docwallet.models import PrivateS3Storage


STATUS_CHOICES = [
    ('in progress', 'In Progress'),
    ('completed', 'Completed'),
    ('sent for approval', 'Sent for Approval'),
    ('revoked', 'Revoked')
]

DESIGNATION_CHOICES = [
    ('partner', 'Partner'),
    ('director', 'Director'),
    ('owner', 'Owner'),
    ('other', 'Other'),
]


class BusinessIdentity(models.Model):
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE, related_name='business_identity_task')
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='business_identity')
    type_of_business = models.CharField(max_length=50, blank=False, null=False)
    legal_name_of_business = models.CharField(max_length=255, blank=False, null=False)
    business_pan = models.FileField(upload_to=business_identity_structure_pan, blank=True,
                                    null=True, storage=PrivateS3Storage())
    nature_of_business = models.CharField(max_length=255, blank=False, null=False)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='in progress')

    service_type = models.CharField(max_length=100, default='Trade License', editable=False)

    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_business')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_business')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super(BusinessIdentity, self).save(*args, **kwargs)

    def __str__(self):
        return self.legal_name_of_business


class ApplicantDetails(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='applicant_details')
    name = models.CharField(max_length=255, blank=False, null=False)
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES, blank=False, null=False)
    aadhaar_image = models.FileField(upload_to=signatory_details_aadhar_image,
                                     blank=True, null=True, storage=PrivateS3Storage())
    pan_image = models.FileField(upload_to=signatory_details_pan_image,
                                 blank=True, null=True, storage=PrivateS3Storage())
    passport_photo = models.FileField(upload_to=signatory_details_passport,
                                      blank=True, null=True, storage=PrivateS3Storage())
    residential_address = models.BooleanField(default=False,
                                              help_text='Is the residential address same as Aadhaar address?')
    address = models.TextField(blank=True, null=True)
    mobile_number = models.BigIntegerField(blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    service_type = models.CharField(max_length=100, default='Trade License', editable=False)
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_applicant')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_applicant')
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='applicant_task', null=False, blank=False)

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super(ApplicantDetails, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class SignatoryDetails(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                        related_name='promoter_or_directors_details')
    service_type = models.CharField(max_length=100, default='Trade License', editable=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_signatory_detail')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_signatory_detail')
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE, related_name='signatory_task',
                                     null=False, blank=False)

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super(SignatoryDetails, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class SignatoryInfo(models.Model):
    signatory_details = models.ForeignKey(SignatoryDetails, on_delete=models.CASCADE, related_name='signatory_info')
    name = models.CharField(max_length=255, blank=False, null=False)
    aadhar_image = models.FileField(upload_to=promoter_or_directors_aadhaar,
                                    blank=True, null=True, storage=PrivateS3Storage())
    pan_image = models.FileField(upload_to=promoter_or_directors_pan,
                                 blank=True, null=True, storage=PrivateS3Storage())
    passport_photo = models.FileField(upload_to=promoter_or_directors_passport_photo,
                                      blank=True, null=True, storage=PrivateS3Storage())
    mobile_number = models.BigIntegerField(blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    residential_address = models.BooleanField(default=False,
                                              help_text='Is the residential address same as Aadhaar address?')
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class BusinessLocation(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='business_locations')
    trade_premises = models.CharField(max_length=100, blank=False, null=False)
    trade_description = models.TextField(blank=False, null=False)
    address = models.JSONField(default=dict, blank=False, null=False)
    nature_of_possession = models.CharField(max_length=100, blank=False, null=False)
    trade_area = models.CharField(max_length=100, blank=False, null=False)
    road_type = models.CharField(max_length=100, blank=False, null=False)
    address_proof = models.FileField(upload_to=business_location_address_proof,
                                     blank=False, null=False, storage=PrivateS3Storage())
    rental_agreement = models.FileField(upload_to=business_location_rental_agreement,
                                        blank=False, null=False, storage=PrivateS3Storage())
    bank_statement = models.FileField(upload_to=business_location_bank_statement,
                                      blank=True, null=True, storage=PrivateS3Storage())
    additional_space = models.BooleanField(default=False,
                                           help_text='Is there an additional space for business?')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    service_type = models.CharField(max_length=100, default='Trade License', editable=False)
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='business_location_task', null=False, blank=False)

    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_businesses_location')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_businesses_location')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super(BusinessLocation, self).save(*args, **kwargs)

    def __str__(self):
        return self.location_name


class AdditionalSpaceBusiness(models.Model):
    business_locations = models.ForeignKey(BusinessLocation, on_delete=models.CASCADE,
                                           related_name='additional_address_details')
    address = models.JSONField(default=dict, blank=False, null=False)
    nature_of_possession = models.CharField(max_length=100, blank=False, null=False)
    address_proof = models.FileField(upload_to=additional_business_space_address_proof, blank=False,
                                     null=False, storage=PrivateS3Storage())
    rental_agreement = models.FileField(upload_to=additional_business_space_rental_agreement,
                                        blank=False, null=False, storage=PrivateS3Storage())

    def __str__(self):
        return str(self.address)


class TradeLicenseDetails(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE,
                                           related_name='trade_license_details')
    apply_new_license = models.BooleanField(default=True, help_text='Is this a new trade license application?')
    trade_license_number = models.CharField(max_length=100, blank=True, null=True)
    trade_license_file = models.FileField(upload_to=trade_license_document,
                                          blank=True, null=True, storage=PrivateS3Storage())

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='trade_license_task', null=False, blank=False)
    service_type = models.CharField(max_length=100, default='Trade License', editable=False)
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_tradelicense')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_tradelicense')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super(TradeLicenseDetails, self).save(*args, **kwargs)

    def __str__(self):
        return self.trade_license_number


class BusinessDocumentDetails(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='business_documents')
    incorporation_certificate = models.FileField(upload_to=business_registration_documents_certificate_of_incorporation,
                                                 blank=False, null=False, storage=PrivateS3Storage())
    photo_of_premises = models.FileField(upload_to=business_registration_documents_photo_of_premises,
                                         blank=False, null=False, storage=PrivateS3Storage())
    property_tax_receipt = models.FileField(upload_to=business_registration_documents_property_tax_receipt,
                                            blank=False, null=False, storage=PrivateS3Storage())
    rental_agreement = models.FileField(upload_to=business_registration_documents_rental_agreement,
                                        blank=False, null=False, storage=PrivateS3Storage())
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    service_type = models.CharField(max_length=100, default='Trade License', editable=False)
    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='business_registration_task', null=False, blank=False)

    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_business_registration_docs')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_business_registration_docs')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super(BusinessDocumentDetails, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.incorporation_certificate)


class ReviewFilingCertificate(models.Model):
    REVIEW_STATUS_CHOICES = [
        ('in progress', 'In Progress'),
        ('completed', 'Completed'),
        ('sent for approval', 'Sent for Approval'),
        ('revoked', 'Revoked')
    ]

    FILING_STATUS_CHOICES = [
        ('in progress', 'In Progress'),
        ('filed', 'Filed'),
        ('sent for approval', 'Sent for Approval'),
        ('resubmitted', 'Resubmitted'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resubmission', 'Resubmission'),
        ('sent for approval', 'Sent for Approval'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
    ]

    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='review_certificate')

    service_type = models.CharField(
        max_length=20,
        default="Trade License",
        editable=False
    )

    service_task = models.OneToOneField(ServiceTask, on_delete=models.CASCADE,
                                        related_name='review_certificate_task', null=False, blank=False)

    review_certificate = models.FileField(upload_to=review_filing_certificate,
                                          null=True, blank=True, storage=PrivateS3Storage())

    draft_filing_certificate = models.FileField(upload_to=draft_filing_certificate,
                                                null=True, blank=True, storage=PrivateS3Storage())
    review_certificate_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        null=True,
        blank=True,
        default=None
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        null=True,
        blank=True,
    )

    filing_status = models.CharField(
        max_length=20,
        choices=FILING_STATUS_CHOICES,
        null=True,
        blank=True,
        default=None
    )

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        null=True,
        blank=True,
        default=None
    )
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_business_review_filing_certificate')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_business_review_filing_certificate')

    def save(self, *args, **kwargs):
        # Default to service_request values if not set
        if not self.assignee and self.service_task.assignee:
            self.assignee = self.service_task.assignee
        if not self.reviewer and self.service_task.reviewer:
            self.reviewer = self.service_task.reviewer
        super(ReviewFilingCertificate, self).save(*args, **kwargs)

    def __str__(self):
        return self.review_certificate_status or "No Review Status"


def calculate_completion_percentage(instance, exclude_fields=None):
    exclude_fields = exclude_fields or ['id', 'created_at', 'updated_at', 'service_request', 'service_task']
    total_fields = 0
    filled_fields = 0

    for field in instance._meta.fields:
        if field.name in exclude_fields:
            continue
        total_fields += 1
        value = getattr(instance, field.name)
        if value not in [None, '', []]:
            filled_fields += 1

    if total_fields == 0:
        return 0
    return round((filled_fields / total_fields) * 100)


@receiver(post_save, sender=BusinessIdentity)
def sync_service_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()


@receiver(post_save, sender=ApplicantDetails)
def sync_applicant_service_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()


@receiver(post_save, sender=SignatoryDetails)
def sync_signatory_service_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()


@receiver(post_save, sender=BusinessLocation)
def sync_business_location_service_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()


@receiver(post_save, sender=TradeLicenseDetails)
def sync_trade_license_service_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()


@receiver(post_save, sender=BusinessDocumentDetails)
def sync_business_document_service_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()


@receiver(post_save, sender=ReviewFilingCertificate)
def sync_review_filing_certificate_service_task_status(sender, instance, **kwargs):
    task = instance.service_task

    # Sync status
    if task.status != instance.status:
        task.status = instance.status

    # Sync completion %
    task.completion_percentage = calculate_completion_percentage(instance)

    task.save()


@receiver(post_save, sender=AdditionalSpaceBusiness)
def sync_business_location_status(sender, instance, **kwargs):
    instance.business_locations.status = "in progress"
    instance.business_locations.save()


@receiver(post_save, sender=SignatoryInfo)
def sync_signatory_info_status(sender, instance, **kwargs):
    instance.signatory_details.status = "in progress"
    instance.signatory_details.save()