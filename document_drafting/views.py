import json
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
@parser_classes([MultiPartParser, FormParser, JSONParser])
def document_list_create(request):
    if request.method == 'GET':
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        try:
            serializer = DocumentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
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
        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        fields = document.fields.all()
        document = DocumentSerializer(document)
        serializer = DocumentFieldsSerializer(fields, many=True)
        return Response({'fields':serializer.data, 'template': document.data})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
        return Response({'message': 'User document draft already exists for this context'})

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


@api_view(['GET', 'POST'])
def draft_document_create(request):
    if request.method == 'GET':
        drafts = DocumentDraftDetail.objects.all()
        serializer = ContextWiseEventAndDocumentSerializer(drafts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ContextWiseEventAndDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def draft_document_detail(request, pk):
    try:
        draft = DocumentDraftDetail.objects.get(pk=pk)
    except DocumentDraftDetail.DoesNotExist:
        return Response({'error': 'Draft document not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ContextWiseEventAndDocumentSerializer(draft)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ContextWiseEventAndDocumentSerializer(draft, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        draft.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def draft_document_by_event(request, event_instance_id):
    if request.method == 'GET':
        event_instance = get_object_or_404(EventInstance, pk=event_instance_id)
        documents = ContextWiseEventAndDocument.objects.filter(event_instance=event_instance)
        serializer = ContextWiseEventAndDocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        event_id = request.data.get('event_id')
        if not event_id:
            return Response({'error': 'Event ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the event instance
        try:
            event = get_object_or_404(Events, pk=event_id)
            event_instance = EventInstance.objects.create(
                event=event,
                title=request.data.get('title', ''),
                description=request.data.get('description', ''),
                status='yet_to_start',
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['event_instance'] = event_instance.id
        documents = json.dumps(json.loads(data.pop('documents', [])))

        if not documents:
            return Response({'error': 'At least one document is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(documents, list):
            documents = [documents]

        created = []
        errors = []

        for doc_id in documents:
            try:
                document = Document.objects.get(pk=doc_id)
                record_data = data.copy()
                record_data['document'] = document.id
                serializer = ContextWiseEventAndDocumentSerializer(data=record_data)
                if serializer.is_valid():
                    serializer.save()
                    created.append(serializer.data)
                else:
                    errors.append({f'document_id_{doc_id}': serializer.errors})
            except Document.DoesNotExist:
                errors.append({f'document_id_{doc_id}': 'Document does not exist'})

        response_payload = {
            'event_instance_id': event_instance.id,
            'created': created
        }

        if errors:
            response_payload['errors'] = errors
            return Response(response_payload, status=status.HTTP_207_MULTI_STATUS)

        return Response(response_payload, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def draft_document_details_create(request):
    if request.method == 'GET':
        drafts = DocumentDraftDetail.objects.all()
        serializer = DocumentDraftDetailSerializer(drafts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()


        serializer = DocumentDraftDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def draft_document_details_create(request):
    if request.method == 'GET':
        drafts = DocumentDraftDetail.objects.all()
        serializer = DocumentDraftDetailSerializer(drafts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data.copy()

        # Ensure 'draft_data' is a proper Python dict (in case it's sent as a JSON string)
        draft_data = data.get('draft_data')
        if isinstance(draft_data, str):
            try:
                data['draft_data'] = json.dumps(json.loads(draft_data))
            except json.JSONDecodeError:
                return Response({'error': 'Invalid JSON for draft_data'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DocumentDraftDetailSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def draft_document_details_detail(request, pk):
    try:
        draft = DocumentDraftDetail.objects.get(pk=pk)
    except DocumentDraftDetail.DoesNotExist:
        return Response({'error': 'Draft document detail not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DocumentDraftDetailSerializer(draft)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DocumentDraftDetailSerializer(draft, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        draft.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def event_and_category_list(request):
    """
    Returns a list of all events with their categories.
    """
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def user_document_draft_is_exist(request, context_id):
    """
    Check if a user document draft exists for the given context.
    """
    try:
        draft = UserDocumentDraft.objects.get(context=context_id)
        serializer = UserDocumentDraftSerializer(draft)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserDocumentDraft.DoesNotExist:
        return Response({'error': 'User document draft not found'}, status=status.HTTP_404_NOT_FOUND)


