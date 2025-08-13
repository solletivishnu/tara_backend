from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import PayrollWorkflow
from .tasks import generate_and_upload_all_payslips

@receiver(pre_save, sender=PayrollWorkflow)
def trigger_payslip_generation(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_instance = PayrollWorkflow.objects.get(pk=instance.pk)

    if not old_instance.lock_payroll and instance.lock_payroll:
        payroll = instance.payroll
        month = (
            instance.month)
        financial_year = instance.financial_year
        generate_and_upload_all_payslips(
            payroll,
            month,
            financial_year
        )

