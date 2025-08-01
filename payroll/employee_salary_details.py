import base64
import numpy as np
from django.utils.timezone import now, localtime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import EmployeeCredentials, EmployeeSalaryHistory, EmployeeSalaryDetails
from .serializers import EmployeeCredentialsSerializer, EmployeeSalaryHistorySerializer, EmployeeSalaryDetailsSerializer
from payroll.authentication import EmployeeJWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from datetime import datetime, timedelta, date
from calendar import monthrange, month_name
from rest_framework import status
from collections import defaultdict
from .views import number_to_words_in_indian_format
from django.db.models import Sum


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def employee_payslip_details(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    month = request.query_params.get('month', now().month)
    financial_year = request.query_params.get('financial_year')


    try:
        salary_details = EmployeeSalaryHistory.objects.filter(employee=employee.employee,
                                month=month, financial_year=financial_year).first()
        if not salary_details:
            return Response({'error': 'Salary details not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeSalaryHistorySerializer(salary_details)
        data = serializer.data.copy()
        data['bank_name'] = employee.employee.employee_bank_details.bank_name if (
            employee.employee.employee_bank_details.bank_name) else None
        data['bank_account_number'] = employee.employee.employee_bank_details.account_number if (
            employee.employee.employee_bank_details.account_number) else None
        data['pf_account_number'] = employee.employee.statutory_components.get('employee_provident_fund',
                        {}).get('pf_account_number') if (employee.employee.statutory_components.get('epf_enabled') is
                                                         True) else None
        data['net_pay_in_words'] = number_to_words_in_indian_format(data['net_salary']).title() + " Rupees Only"

        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_valid_fy_months_upto(month_limit):
    """
    Returns a list of fiscal year months from April (4) up to the given month (inclusive),
    wrapping correctly through Jan/Feb/Mar if needed.
    """
    fiscal_months = list(range(4, 13)) + list(range(1, 4))  # [4,5,6,...12,1,2,3]
    result = []

    for m in fiscal_months:
        result.append(m)
        if m == month_limit:
            break

    return result


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_cumulative_salary_data(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    financial_year = request.query_params.get('financial_year')
    max_month = int(request.query_params.get('month', datetime.today().month))

    if not financial_year:
        return Response({'error': 'financial_year is required'}, status=status.HTTP_400_BAD_REQUEST)


    # Valid financial year months: April (4) to March (3 next year)
    valid_months = get_valid_fy_months_upto(max_month)

    salary_history = EmployeeSalaryHistory.objects.filter(
        employee=employee.employee,
        financial_year=financial_year,
        month__in=valid_months
    ).order_by('month')

    if not salary_history.exists():
        return Response([], status=status.HTTP_200_OK)

    cumulative_totals = defaultdict(float)
    cumulative_other_earnings = defaultdict(float)
    cumulative_other_deductions = defaultdict(float)

    fields_to_sum = [
        "basic_salary", "hra", "conveyance_allowance", "travelling_allowance",
        "commission", "children_education_allowance", "overtime_allowance",
        "transport_allowance", "special_allowance", "bonus", "other_earnings",
        "benefits_total", "epf", "esi", "pt", "tds", "loan_emi",
        "other_deductions", "total_deductions", "net_salary"
    ]

    monthly_data = []

    for record in salary_history:
        month_data = {
            "data_for": month_name[record.month],
            "month": record.month,
            "is_total": False,
        }

        for field in fields_to_sum:
            value = getattr(record, field, 0) or 0
            cumulative_totals[field] += value
            month_data[field] = cumulative_totals[field]

        earnings_breakdown = record.other_earnings_breakdown or []
        for item in earnings_breakdown:
            for key, val in item.items():
                cumulative_other_earnings[key] += val or 0

        month_data["other_earnings_breakdown"] = [
            {k: cumulative_other_earnings[k]} for k in cumulative_other_earnings
        ] if cumulative_other_earnings else []

        deductions_breakdown = record.other_deductions_breakdown or []
        for item in deductions_breakdown:
            for key, val in item.items():
                cumulative_other_deductions[key] += val or 0

        month_data["other_deductions_breakdown"] = [
            {k: cumulative_other_deductions[k]} for k in cumulative_other_deductions
        ] if cumulative_other_deductions else []

        monthly_data.append(month_data)

    # Add "Total" row
    total_row = {
        "data_for": "Cumulative Total",
        "month": None,
        "is_total": True,
    }

    for field in fields_to_sum:
        total_row[field] = cumulative_totals[field]

    total_row["other_earnings_breakdown"] = [
        {k: cumulative_other_earnings[k]} for k in cumulative_other_earnings
    ] if cumulative_other_earnings else []

    total_row["other_deductions_breakdown"] = [
        {k: cumulative_other_deductions[k]} for k in cumulative_other_deductions
    ] if cumulative_other_deductions else []

    monthly_data.append(total_row)

    return Response(monthly_data, status=status.HTTP_200_OK)


