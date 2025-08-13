from celery import shared_task
from .services.salary_processor import EmployeeSalaryProcessor, AllOrgPayrollProcessor
from payroll.models import PayrollOrg
from .models import EmployeeSalaryHistory
from datetime import date
import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError
from django.core.cache import cache
from .views import generate_payslip_from_history
from Tara.settings.default import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_PRIVATE_BUCKET_NAME


@shared_task
def process_all_orgs_salary_task():
    today = date.today()

    # Financial year format: "2024-2025"
    fy_start = today.year if today.month >= 4 else today.year - 1
    financial_year = f"{fy_start}-{fy_start + 1}"
    month = today.month

    print(f"[INFO] Running salary processing for all orgs: FY={financial_year}, Month={month}")
    AllOrgPayrollProcessor(financial_year, month).run()
    print("[INFO] Payroll processing completed.")


@shared_task
def generate_and_upload_all_payslips(payroll_id, month, financial_year):
    """
    Generates and uploads payslips for all employees in a payroll to S3.
    Triggered when lock_payroll changes from False → True.
    """
    s3 = boto3.client(
        's3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    bucket_name = AWS_PRIVATE_BUCKET_NAME

    salary_histories = EmployeeSalaryHistory.objects.filter(
        payroll=payroll_id,
        month=month,
        financial_year=financial_year
    )

    if not salary_histories:
        print(f"[WARNING] No salary histories found for payroll={payroll_id}, month={month}, FY={financial_year}")
        return

    print(f"[INFO] Generating payslips for payroll={payroll_id}, month={month}, FY={financial_year}")
    year = int(financial_year.split("-")[0]) if month >= 4 else int(financial_year.split("-")[1])

    for history in salary_histories:
        pdf_bytes = generate_payslip_from_history(
            history,
            month,
            year,
            financial_year
        )

        if not pdf_bytes:
            print(f"[ERROR] No PDF generated for employee {history.employee_id}")
            continue

        object_key = f"salary_slips/{history.employee_id}/{financial_year}/{month}_{year}.pdf"
        print(f"[DEBUG] Uploading to S3 key={object_key}, size={len(pdf_bytes)} bytes")

        try:
            response = s3.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=pdf_bytes,
                ContentType="application/pdf"
            )
            print(f"[DEBUG] S3 upload response: {response}")

            # Cache signed URL
            signed_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_key},
                ExpiresIn=7200  # 2 hours in seconds
            )
            cache_key = f"salary_slip_url_{history.employee_id}_{month}_{year}_{financial_year}"
            cache.set(cache_key, signed_url, timeout=7200)

        except (BotoCoreError, ClientError) as e:
            print(f"[ERROR] Failed to upload to S3 for employee {history.employee_id}: {e}")

    print(f"[INFO] Completed payslip generation for payroll={payroll_id}")
