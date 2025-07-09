from rest_framework import serializers
from .models import *
import json


class EventsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Events
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    events = EventsSerializer(many=True, read_only=True)


    class Meta:
        model = Category
        fields = "__all__"





class DocumentFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFields
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    event = EventsSerializer(read_only=True)

    class Meta:
        model = Document
        fields = '__all__'


class UserDocumentDraftSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDocumentDraft
        fields = '__all__'


class UserFavouriteDocumentSerializer(serializers.ModelSerializer):
    document = serializers.SerializerMethodField()

    class Meta:
        model = UserFavouriteDocument
        fields = '__all__'

    def get_document(self, obj):
        if obj.document:
            return {
                'id': obj.document.id,
                'document_name': obj.document.document_name,
                'description': obj.document.description,
                'template': obj.document.template,
            }
        return None


class EventInstanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventInstance
        fields = '__all__'


class ContextWiseEventAndDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContextWiseEventAndDocument
        fields = '__all__'


class DocumentDraftDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentDraftDetail
        fields = '__all__'


from rest_framework import serializers
from .models import ContextWiseEventAndDocument

class ContextWiseEventAndDocumentStatusSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(source='created_at', format="%d/%m/%y")
    last_edited = serializers.DateTimeField(source='updated_at', format="%d/%m/%y")
    category = serializers.SerializerMethodField()
    event = serializers.CharField(source='event_instance.event.event_name')
    creator = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = ContextWiseEventAndDocument
        fields = ['created_date', 'category', 'event', 'status', 'last_edited', 'creator']

    def get_category(self, obj):
        return obj.category.category_name if obj.category else ""

    def get_creator(self, obj):
        user = obj.created_by
        if not user:
            return ""

        first = user.first_name if user.first_name else ""
        middle = user.middle_name if hasattr(user, 'middle_name') and user.middle_name else ""
        last = user.last_name if user.last_name else ""

        full_name = " ".join(part for part in [first, middle, last] if part)
        return full_name or ""

    def get_status(self, obj):
        status_map = {
            'completed': 'Completed',
            'in_progress': 'Processed',
            'draft': 'Declined',
            'yet_to_start': 'Yet to Start',
        }
        return status_map.get(obj.status, obj.status.title())

