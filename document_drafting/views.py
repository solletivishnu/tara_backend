from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import *
from .models import *

@api_view(['GET', 'POST'])
def category_list_create(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def events_list_create(request):
    if request.method == 'GET':
        events = Events.objects.all()
        serializer = EventsSerializer(events, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = EventsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def events_detail(request, pk):
    try:
        event = Events.objects.get(pk=pk)
    except Events.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EventsSerializer(event)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = EventsSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def document_list_create(request):
    if request.method == 'GET':
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def document_detail(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DocumentSerializer(document)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DocumentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def document_fields_list_create(request):
    if request.method == 'GET':
        fields = DocumentFields.objects.all()
        serializer = DocumentFieldsSerializer(fields, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = DocumentFieldsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def document_fields_detail(request, pk):
    try:
        field = DocumentFields.objects.get(pk=pk)
    except DocumentFields.DoesNotExist:
        return Response({'error': 'Document field not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DocumentFieldsSerializer(field)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DocumentFieldsSerializer(field, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        field.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def document_fields_by_document(request, document_id):
    try:
        document = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    fields = document.fields.all()
    serializer = DocumentFieldsSerializer(fields, many=True)
    return Response({'fields':serializer.data, 'template': document.template})


@api_view(['GET'])
def document_template_and_fields(request, id):
    try:
        context = ContextWiseEventAndDocument.objects.get(pk=id)
    except ContextWiseEventAndDocument.DoesNotExist:
        return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

    fields = context.document.fields.all()
    serializer = DocumentFieldsSerializer(fields, many=True)
    return Response({
        'template': context.document.template,
        'fields': serializer.data
    })


@api_view(['GET', 'POST'])
def user_document_draft_list_create(request):
    if request.method == 'GET':
        drafts = UserDocumentDraft.objects.all()
        serializer = UserDocumentDraftSerializer(drafts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':

        try:
            context = UserDocumentDraft.objects.get(context=request.data.get('context'))
        except:
            serializer = UserDocumentDraftSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def user_document_draft_detail(request, pk):
    try:
        draft = UserDocumentDraft.objects.get(pk=pk)
    except UserDocumentDraft.DoesNotExist:
        return Response({'error': 'User document draft not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserDocumentDraftSerializer(draft)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserDocumentDraftSerializer(draft, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        draft.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def context_wise_event_and_document(request, context_id):
    try:
        draft = UserDocumentDraft.objects.get(context=context_id)
        context = draft.context
    except UserDocumentDraft.DoesNotExist:
        return Response({'error': 'Context not found'}, status=status.HTTP_404_NOT_FOUND)

    # Get all distinct event instances linked to this context via ContextWiseEventAndDocument
    event_instances = EventInstance.objects.filter(
        documents__context=context  # related_name='documents' in ContextWiseEventAndDocument
    ).distinct()

    response_data = []

    for instance in event_instances:
        # Get all documents for this event instance and context
        linked_documents = instance.documents.filter(context=context)

        documents_data = []
        for doc_map in linked_documents:
            documents_data.append({
                'document_id': doc_map.document.id,
                'document_name': doc_map.document.document_name,
                'category': doc_map.category.category_name if doc_map.category else None,
                'status': doc_map.status,
                'created_at': doc_map.created_at,
                'updated_at': doc_map.updated_at
            })

        response_data.append({
            'event_instance_id': instance.id,
            'event_name': instance.event.event_name,
            'custom_title': instance.title,
            'description': instance.description,
            'status': instance.status,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
            'documents': documents_data
        })

    return Response(response_data, status=status.HTTP_200_OK)