import base64
import numpy as np
from datetime import datetime
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import AttendanceLog, EmployeeManagement
from .serializers import AttendanceLogSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manual_check_in(request):
    user = request.user
    try:
        employee = EmployeeManagement.objects.get(user=user)
    except EmployeeManagement.DoesNotExist:
        return Response({'error': 'Employee profile not found'}, status=404)

    today = now().date()
    attendance, created = AttendanceLog.objects.get_or_create(employee=employee, date=today)

    if attendance.check_in:
        return Response({'message': 'Already checked in'}, status=400)

    attendance.check_in = now()
    attendance.check_in_type = 'manual'
    attendance.save()

    serializer = AttendanceLogSerializer(attendance)
    return Response({'message': 'Check-in successful', 'data': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manual_check_out(request):
    user = request.user
    try:
        employee = EmployeeManagement.objects.get(user=user)
    except EmployeeManagement.DoesNotExist:
        return Response({'error': 'Employee profile not found'}, status=404)

    today = now().date()
    try:
        attendance = AttendanceLog.objects.get(employee=employee, date=today)
    except AttendanceLog.DoesNotExist:
        return Response({'error': 'No check-in record found for today'}, status=404)

    if attendance.check_out:
        return Response({'message': 'Already checked out'}, status=400)

    attendance.check_out = now()
    attendance.save()

    serializer = AttendanceLogSerializer(attendance)
    return Response({'message': 'Check-out successful', 'data': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def today_attendance_status(request):
    user = request.user
    try:
        employee = EmployeeManagement.objects.get(user=user)
    except EmployeeManagement.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=404)

    today = now().date()
    try:
        attendance = AttendanceLog.objects.get(employee=employee, date=today)
        serializer = AttendanceLogSerializer(attendance)
        return Response(serializer.data)
    except AttendanceLog.DoesNotExist:
        return Response({'message': 'No attendance record for today'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_attendance_report(request):
    user = request.user
    month = int(request.query_params.get('month', now().month))
    year = int(request.query_params.get('year', now().year))

    try:
        employee = EmployeeManagement.objects.get(user=user)
    except EmployeeManagement.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=404)

    logs = AttendanceLog.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    ).order_by('date')

    serializer = AttendanceLogSerializer(logs, many=True)
    return Response({
        'month': month,
        'year': year,
        'records': serializer.data
    })

