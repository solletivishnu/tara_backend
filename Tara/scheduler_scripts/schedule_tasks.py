# tara_backend/scripts/schedule_tasks.py

from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

# Create interval (every 1 minute)
schedule, _ = IntervalSchedule.objects.get_or_create(
    every=5,
    period=IntervalSchedule.MINUTES,
)

# Create the periodic task
PeriodicTask.objects.update_or_create(
    name='Print Current Time Every Minute',
    defaults={
        'interval': schedule,
        'task': 'document_drafting.tasks.print_current_time',
        'args': json.dumps([]),
    }
)
