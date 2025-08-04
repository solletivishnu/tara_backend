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

    valid_months = get_valid_fy_months_upto(selected_month)

    salaries = EmployeeSalaryHistory.objects.filter(
        employee=employee.employee,
        financial_year=financial_year,
        month__in=valid_months
    ).order_by('month')

    if not salaries.exists():
        return Response({'message': 'No salary records found'}, status=status.HTTP_200_OK)

    earnings_fields = [
        "basic_salary", "hra", "conveyance_allowance", "travelling_allowance",
        "commission", "children_education_allowance", "overtime_allowance",
        "transport_allowance", "special_allowance", "bonus"
    ]
    deduction_fields = ["epf", "esi", "pt", "tds", "loan_emi"]

    def accumulate_values(records, selected_month):
        month_vals, ytd_vals = defaultdict(float), defaultdict(float)
        for rec in records:
            is_selected = rec.month == selected_month

            for field in earnings_fields:
                val = getattr(rec, field, 0) or 0
                ytd_vals[field] += val
                if is_selected:
                    month_vals[field] = val

            for item in rec.other_earnings_breakdown or []:
                for k, v in item.items():
                    ytd_vals[k] += v or 0
                    if is_selected:
                        month_vals[k] = v or 0

            for field in deduction_fields:
                val = getattr(rec, field, 0) or 0
                ytd_vals[field] += val
                if is_selected:
                    month_vals[field] = val

            for item in rec.other_deductions_breakdown or []:
                for k, v in item.items():
                    ytd_vals[k] += v or 0
                    if is_selected:
                        month_vals[k] = v or 0

        return month_vals, ytd_vals

    def format_components(ordered_fields, month_data, ytd_data):
        result = []
        all_keys = ordered_fields + [k for k in month_data.keys() if k not in ordered_fields]
        for key in all_keys:
            month_val = round(month_data.get(key, 0), 2)
            ytd_val = round(ytd_data.get(key, 0), 2)
            if month_val > 0 or ytd_val > 0:
                result.append({
                    "component_name": key.replace("_", " ").title(),
                    "month_data": month_val,
                    "ytd": ytd_val
                })
        return result

    # Accumulate earnings and deductions
    month_earnings, ytd_earnings = accumulate_values(salaries, selected_month)
    month_deductions = {k: v for k, v in month_earnings.items() if k in deduction_fields}
    ytd_deductions = {k: v for k, v in ytd_earnings.items() if k in deduction_fields}
    month_earnings = {k: v for k, v in month_earnings.items() if k not in deduction_fields}
    ytd_earnings = {k: v for k, v in ytd_earnings.items() if k not in deduction_fields}

    # Calculate totals
    last_month = salaries.filter(month=selected_month).first()
    total_net_salary_month = last_month.net_salary if last_month else 0
    total_gross_income_month = last_month.earned_salary if last_month else 0
    total_deduction_month = last_month.total_deductions if last_month else 0

    total_net_salary_ytd = sum((rec.net_salary or 0) for rec in salaries)
    total_gross_income_ytd = sum((rec.earned_salary or 0) for rec in salaries)
    total_deduction_ytd = sum((rec.total_deductions or 0) for rec in salaries)

    response_data = {
        "earnings": format_components(earnings_fields, month_earnings, ytd_earnings),
        "deductions": format_components(deduction_fields, month_deductions, ytd_deductions),
        "gross_income": {
            "month_data": round(total_gross_income_month, 2),
            "ytd": round(total_gross_income_ytd, 2)
        },
        "net_salary": {
            "month_data": round(total_net_salary_month, 2),
            "ytd": round(total_net_salary_ytd, 2)
        },
        "deduction_total": {
            "month_data": round(total_deduction_month, 2),
            "ytd": round(total_deduction_ytd, 2)
        }
    }

    return Response(response_data, status=status.HTTP_200_OK)


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


