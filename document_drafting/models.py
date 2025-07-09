from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from usermanagement.models import Context
from .helpers import draft_document_file
from docwallet.models import PrivateS3Storage


class Category(models.Model):
    """
    Model to store category details.
    """
    category_name = models.CharField(max_length=255, help_text="Name of the category")
    description = models.TextField(blank=True, null=True, help_text="Description of the category")
    metadata = JSONField(blank=True, null=True, help_text="Additional metadata related to the category")
    created_at = models.DateField(auto_now_add=True, help_text="Timestamp when the category was created")
    updated_at = models.DateField(auto_now=True, help_text="Timestamp when the category was last updated")

    def __str__(self):
        return self.category_name


class Events(models.Model):
    """
    Model to store event details.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events',
                                help_text="Category associated with the event", null=True, blank=True)
    event_name = models.CharField(max_length=255, help_text="Name of the event")
    description = models.TextField(blank=True, null=True, help_text="Description of the event")
    metadata = JSONField(blank=True, null=True, help_text="Additional metadata related to the event")
    created_at = models.DateField(auto_now_add=True, help_text="Timestamp when the event was created")
    updated_at = models.DateField(auto_now=True, help_text="Timestamp when the event was last updated")

    def __str__(self):
        return self.event_name


class Document(models.Model):
    """
    Model to store document details.
    """
    document_name = models.CharField(max_length=255, help_text="Name of the document")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='documents',
                                help_text="Category associated with the document", null=True, blank=True)
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name='documents',
                             help_text="Event associated with the document", null=True, blank=True)
    description = models.TextField(blank=True, null=True, help_text="Description of the document")
    template = models.TextField(blank=True, null=True, help_text="Template for the document")
    metadata = JSONField(blank=True, null=True, help_text="Additional metadata related to the document")
    created_at = models.DateField(auto_now_add=True, help_text="Timestamp when the document was created")
    updated_at = models.DateField(auto_now=True, help_text="Timestamp when the document was last updated")

    def __str__(self):
        return self.document_name


class DocumentFields(models.Model):
    """
    Model to store document field details.
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='fields',
                                help_text="Document associated with the field")
    field_name = models.CharField(max_length=255, help_text="Name of the field")
    label = models.CharField(max_length=255, help_text="Label for the field")
    field_type = models.CharField(max_length=50, help_text="Type of the field (e.g., text, number, date)")
    is_required = models.BooleanField(default=False, help_text="Indicates if the field is required")
    created_at = models.DateField(auto_now_add=True, help_text="Timestamp when the field was created")
    updated_at = models.DateField(auto_now=True, help_text="Timestamp when the field was last updated")

    def __str__(self):
        return self.field_name


class UserDocumentDraft(models.Model):
    context = models.OneToOneField(Context, on_delete=models.CASCADE, related_name='document_draft',
                                  help_text="Context for the document draft (e.g., personal, business)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Wallet for {}".format(self.context)


class UserFavouriteDocument(models.Model):
    """
    Model to store user's favourite documents.
    """
    draft = models.ForeignKey(
        UserDocumentDraft,
        on_delete=models.CASCADE,
        related_name='favourite_documents',
        help_text="Draft associated with the favourite document",
        null=True,
        blank=True
    )
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name='favourited_by',
        help_text="Document that is favourited"
    )
    created_at = models.DateField(
        auto_now_add=True,
        help_text="Timestamp when the document was favourited"
    )

    def __str__(self):
        return "{}".format(self.document.document_name)


class EventInstance(models.Model):
    """
    Model to represent a unique instance of an event for a specific context.
    This allows the same event to be raised multiple times with different documents.
    """
    event = models.ForeignKey(
        Events,
        on_delete=models.CASCADE,
        related_name='instances',
        help_text="The base event template"
    )
    title = models.CharField(
        max_length=255,
        help_text="Custom title for this event instance",
        blank=True,
        null=True
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Custom description for this event instance"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('draft', 'Draft'),
            ('yet_to_start', 'Yet to be Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        default='yet_to_start',
        help_text="Current status of the event instance."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event.event_name} - {self.context.name} ({self.pk})"


class ContextWiseEventAndDocument(models.Model):
    """
    Model to link documents to specific event instances.
    """
    context = models.ForeignKey(
        UserDocumentDraft,
        on_delete=models.CASCADE,
        related_name='context_event_documents',
        help_text="Context for this event instance"
    )
    event_instance = models.ForeignKey(
        EventInstance,
        on_delete=models.CASCADE,
        related_name='documents',
        help_text="Event instance this document belongs to"
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='event_documents',
        help_text="Document template being used"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='event_documents',
        help_text="Category associated with this document",
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('yet_to_start', 'Yet to be Started'),
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        default='yet_to_start',
        help_text="Current status of this document"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event_instance', 'document')

    def __str__(self):
        return f"{self.document.document_name} for {self.event_instance}"


class DocumentDraftDetail(models.Model):
    """
    Model to store document draft details for a specific event-document combination.
    """
    draft = models.OneToOneField(
        ContextWiseEventAndDocument,
        on_delete=models.CASCADE,
        related_name='draft_details',
        help_text="Event document this draft belongs to"
    )
    draft_data = JSONField(blank=True, null=True, help_text="JSON field to store draft data", default=dict)
    file = models.FileField(
        upload_to=draft_document_file,
        blank=True,
        null=True,
        help_text="File associated with the draft (optional)",
        storage=PrivateS3Storage()
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Draft for {self.draft}"


@receiver(post_save, sender=DocumentDraftDetail)
def update_document_status(sender, instance, created, **kwargs):
    """
    Signal to update the document status when a draft is created or updated.
    """
    # Update the EventDocument status based on draft changes
    if instance.event_document.status != 'draft':
        instance.event_document.status = 'draft'
        instance.event_document.save()