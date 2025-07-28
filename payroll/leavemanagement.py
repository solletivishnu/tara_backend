from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from .models import LeaveApplication
from .serializers import LeaveApplicationSerializer
from .authentication import EmployeeJWTAuthentication
from django.utils import timezone
from datetime import datetime, timedelta
import calendar


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def apply_leave(request):
    if not hasattr(request.user, 'employeecredentials'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = LeaveApplicationSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        leave = serializer.save(employee=request.user.employeecredentials)
        return Response({
            'id': leave.id,
            'message': 'Leave application submitted successfully',
            'status': leave.status
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_leave_applications(request):
    if not hasattr(request.user, 'employeecredentials'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    leaves = LeaveApplication.objects.filter(employee=request.user.employeecredentials)
    serializer = LeaveApplicationSerializer(leaves, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def approve_leave(request, pk):
    if not hasattr(request.user, 'employeecredentials'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        leave = LeaveApplication.objects.get(pk=pk)
    except LeaveApplication.DoesNotExist:
        return Response({'error': 'Leave application not found'}, status=status.HTTP_404_NOT_FOUND)

    # Add permission check if needed
    # if not request.user.has_perm('can_approve_leave'):
    #     return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    leave.status = 'approved'
    leave.reviewer = request.user.employeecredentials
    leave.reviewed_on = timezone.now()
    leave.save()

    serializer = LeaveApplicationSerializer(leave)
    return Response({'message': 'Leave approved', 'data': serializer.data})


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def reject_leave(request, pk):
    if not hasattr(request.user, 'employeecredentials'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        leave = LeaveApplication.objects.get(pk=pk)
    except LeaveApplication.DoesNotExist:
        return Response({'error': 'Leave application not found'}, status=status.HTTP_404_NOT_FOUND)

    comment = request.data.get('reviewer_comment', '')
    if not comment:
        return Response({'error': 'Comment is required for rejection'}, status=status.HTTP_400_BAD_REQUEST)

    leave.status = 'rejected'
    leave.reviewer = request.user.employeecredentials
    leave.reviewed_on = timezone.now()
    leave.reviewer_comment = comment
    leave.save()

    serializer = LeaveApplicationSerializer(leave)
    return Response({'message': 'Leave rejected', 'data': serializer.data})


@api_view(['POST'])
@authentication_classes([EmployeeJWTAuthentication])
def cancel_leave(request, pk):
    if not hasattr(request.user, 'employeecredentials'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        leave = LeaveApplication.objects.get(pk=pk, employee=request.user.employeecredentials)
    except LeaveApplication.DoesNotExist:
        return Response({'error': 'Leave application not found'}, status=status.HTTP_404_NOT_FOUND)

    if leave.status != 'pending':
        return Response({'error': 'Only pending leaves can be cancelled'}, status=status.HTTP_400_BAD_REQUEST)

    leave.status = 'cancelled'
    leave.save()

    serializer = LeaveApplicationSerializer(leave)
    return Response({'message': 'Leave cancelled', 'data': serializer.data})


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_monthly_leaves(request, year, month):
    """Get leaves for specific month (format: YYYY/MM)"""
    if not hasattr(request.user, 'employeecredentials'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        # Validate month/year
        month_start = datetime(year=year, month=month, day=1).date()
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        month_end = datetime(year=next_year, month=next_month, day=1).date() - timedelta(days=1)
    except ValueError:
        return Response({'error': 'Invalid month/year'}, status=status.HTTP_400_BAD_REQUEST)

    leaves = LeaveApplication.objects.filter(
        employee=request.user.employeecredentials,
        start_date__lte=month_end,
        end_date__gte=month_start
    ).order_by('start_date')

    serializer = LeaveApplicationSerializer(leaves, many=True)
    return Response({
        'month': f"{year}-{month:02d}",
        'count': leaves.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_current_month_leaves(request):
    """Get leaves for current month"""
    today = timezone.now().date()
    return get_monthly_leaves(request._request, today.year, today.month)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_leave_summary(request, year=None):
    """Get monthly leave summary for a year"""
    if not hasattr(request.user, 'employeecredentials'):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    year = int(year or timezone.now().year)
    leaves = LeaveApplication.objects.filter(
        employee=request.user.employeecredentials,
        start_date__year=year
    )

    summary = []
    for month in range(1, 13):
        month_leaves = leaves.filter(start_date__month=month)
        approved = month_leaves.filter(status='approved')

        # Get the first and last date of the month
        start_of_month = datetime(year, month, 1).date()
        last_day = calendar.monthrange(year, month)[1]
        end_of_month = datetime(year, month, last_day).date()

        total_days = sum(
            (min(leave.end_date, end_of_month) - max(leave.start_date, start_of_month)).days + 1
            for leave in approved
            if leave.end_date >= start_of_month and leave.start_date <= end_of_month
        )

        summary.append({
            'month': f"{year}-{month:02d}",
            'total_leaves': month_leaves.count(),
            'approved_leaves': approved.count(),
            'pending_leaves': month_leaves.filter(status='pending').count(),
            'rejected_leaves': month_leaves.filter(status='rejected').count(),
            'total_days': total_days
        })

    return Response({
        'year': year,
        'summary': summary
    })