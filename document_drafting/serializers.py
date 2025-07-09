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
    event = EventsSerializer(read_only=True)
    document = DocumentSerializer(read_only=True)

    class Meta:
        model = ContextWiseEventAndDocument
        fields = '__all__'


class DocumentDraftDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentDraftDetail
        fields = '__all__'

