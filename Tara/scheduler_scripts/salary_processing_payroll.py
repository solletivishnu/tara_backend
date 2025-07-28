from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


def schedule_salary_processing():
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute='30',
        hour='14',
        day_of_month='26-30',
        month_of_year='*',
        day_of_week='*'
    )

    task, created = PeriodicTask.objects.get_or_create(
        name='Run Employee Salary Processing',
        defaults={
            'task': 'payroll.tasks.process_all_orgs_salary_task',
            'crontab': schedule,
            'args': json.dumps([]),
        }
    )

    if not created:
        task.crontab = schedule
        task.enabled = True
        task.save()
