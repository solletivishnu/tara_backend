from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import AgricultureIncome, AgricultureIncomeDocument
from .serializers import (
    AgricultureIncomeSerializer,
    AgricultureIncomeDocumentSerializer,
)


# AgricultureIncome APIs

@api_view(['POST'])
def upsert_agriculture_income(request):
    service_request_id = request.data.get('service_request')
    if not service_request_id:
        return Response(
            {"error": "Missing service_request"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        income = AgricultureIncome.objects.get(service_request_id=service_request_id)
        serializer = AgricultureIncomeSerializer(income, data=request.data, partial=True)
    except AgricultureIncome.DoesNotExist:
        serializer = AgricultureIncomeSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_agriculture_income(request):
    service_request_id = request.query_params.get('service_request')
    if not service_request_id:
        return Response(
            {"error": "Missing service_request"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        income = AgricultureIncome.objects.get(service_request_id=service_request_id)
    except AgricultureIncome.DoesNotExist:
        return Response(
            {"error": "No Agriculture Income found for given service_request"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = AgricultureIncomeSerializer(income)
    return Response(serializer.data, status=status.HTTP_200_OK)


# AgricultureIncomeDocument APIs

@api_view(['POST'])
def add_agriculture_income_document(request):
    serializer = AgricultureIncomeDocumentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Agriculture Income Document added successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_agriculture_income_document(request, document_id):
    try:
        doc = AgricultureIncomeDocument.objects.get(pk=document_id)
    except AgricultureIncomeDocument.DoesNotExist:
        return Response(
            {"error": "Document not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = AgricultureIncomeDocumentSerializer(doc, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Agriculture Income Document updated successfully"},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_agriculture_income_document(request, document_id):
    try:
        doc = AgricultureIncomeDocument.objects.get(pk=document_id)
        doc.delete()
        return Response(
            {"message": "Agriculture Income Document deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    except AgricultureIncomeDocument.DoesNotExist:
        return Response(
            {"error": "Document not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def get_agriculture_income_documents(request):
    agriculture_income_id = request.query_params.get('agriculture_income_id')
    if not agriculture_income_id:
        return Response(
            {"error": "Missing agriculture_income_id"},
            status=status.HTTP_400_BAD_REQUEST
        )
    documents = AgricultureIncomeDocument.objects.filter(winning_income_id=agriculture_income_id)
    serializer = AgricultureIncomeDocumentSerializer(documents, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
