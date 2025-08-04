import base64
import numpy as np
from django.utils.timezone import now, localtime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import EmployeeCredentials, EmployeeSalaryHistory, EmployeeSalaryDetails
from .serializers import (EmployeeCredentialsSerializer, EmployeeSalaryHistorySerializer, EmployeeSalaryDetailsSerializer,
                          EmployeeFinancialYearPayslipSerializer)
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
def get_month_and_ytd_salary_data(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    financial_year = request.query_params.get('financial_year')
    selected_month = request.query_params.get('month')

    if not financial_year or not selected_month:
        return Response({'error': 'financial_year and month are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        selected_month = int(selected_month)
    except ValueError:
        return Response({'error': 'Invalid month value'}, status=status.HTTP_400_BAD_REQUEST)

    # Valid months in FY up to selected month
    valid_months = get_valid_fy_months_upto(selected_month)

    salary_qs = EmployeeSalaryHistory.objects.filter(
        employee=employee.employee,
        financial_year=financial_year,
        month__in=valid_months
    ).order_by('month')

    if not salary_qs.exists():
        return Response({'message': 'No salary records found'}, status=status.HTTP_200_OK)

    earnings_fields = [
        "basic_salary", "hra", "conveyance_allowance", "travelling_allowance",
        "commission", "children_education_allowance", "overtime_allowance",
        "transport_allowance", "special_allowance", "bonus", "other_earnings"
    ]
    deduction_fields = [
        "epf", "esi", "pt", "tds", "loan_emi", "other_deductions"
    ]

    earnings_totals = defaultdict(float)
    deductions_totals = defaultdict(float)
    cumulative_other_earnings = defaultdict(float)
    cumulative_other_deductions = defaultdict(float)

    total_net_salary = 0.0
    total_gross_income = 0.0
    total_deduction_amount = 0.0

    month_data = None

    for record in salary_qs:
        # Capture selected month record
        if record.month == selected_month:
            earnings = {field: getattr(record, field, 0) or 0 for field in earnings_fields}
            deductions = {field: getattr(record, field, 0) or 0 for field in deduction_fields}

            for item in record.other_earnings_breakdown or []:
                for k, v in item.items():
                    earnings[k] = v or 0

            for item in record.other_deductions_breakdown or []:
                for k, v in item.items():
                    deductions[k] = v or 0

            month_data = {
                "data_for": month_name[record.month],
                "month": record.month,
                "is_total": False,
                "earnings": earnings,
                "deductions": deductions,
                "net_salary": record.net_salary,
                "gross_income": record.earned_salary,
                "net_pay_in_words": number_to_words_in_indian_format(record.net_salary).title() + " Rupees Only",
                "deduction_total": record.total_deductions
            }

        # YTD accumulation
        for field in earnings_fields:
            earnings_totals[field] += getattr(record, field, 0) or 0

        for field in deduction_fields:
            deductions_totals[field] += getattr(record, field, 0) or 0

        for item in record.other_earnings_breakdown or []:
            for k, v in item.items():
                cumulative_other_earnings[k] += v or 0

        for item in record.other_deductions_breakdown or []:
            for k, v in item.items():
                cumulative_other_deductions[k] += v or 0

        total_net_salary += record.net_salary or 0
        total_gross_income += record.earned_salary or 0
        total_deduction_amount += record.total_deductions or 0

    # Final YTD structured data
    ytd_earnings = {field: earnings_totals[field] for field in earnings_fields}
    ytd_earnings.update(cumulative_other_earnings)

    ytd_deductions = {field: deductions_totals[field] for field in deduction_fields}
    ytd_deductions.update(cumulative_other_deductions)

    ytd_data = {
        "data_for": "Cumulative Total",
        "month": None,
        "is_total": True,
        "earnings": ytd_earnings,
        "deductions": ytd_deductions,
        "net_salary": total_net_salary,
        "gross_income": total_gross_income,
        "net_pay_in_words": number_to_words_in_indian_format(int(total_net_salary)).title() + " Rupees Only",
        "deduction_total": total_deduction_amount
    }

    return Response({
        "month_data": month_data,
        "ytd_data": ytd_data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([EmployeeJWTAuthentication])
def get_employee_financial_year_payslip_details(request):
    employee = request.user

    if not isinstance(employee, EmployeeCredentials):
        return Response({'error': 'Invalid employee credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    financial_year = request.query_params.get('financial_year')
    if not financial_year:
        return Response({'error': 'financial_year is required'}, status=status.HTTP_400_BAD_REQUEST)

    salary_history = EmployeeSalaryHistory.objects.filter(
        employee=employee.employee,
        financial_year=financial_year
    ).order_by('-month')

    if not salary_history.exists():
        return Response([], status=status.HTTP_200_OK)

    serializer = EmployeeFinancialYearPayslipSerializer(salary_history, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


