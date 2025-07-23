from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

# Create or get interval (every 10 minutes)
schedule, _ = IntervalSchedule.objects.get_or_create(
    every=10,
    period=IntervalSchedule.MINUTES,
)

# Create or update the periodic task
PeriodicTask.objects.update_or_create(
    name='Print Current Time Every 10 Minutes',
    defaults={
        'interval': schedule,
        'task': 'document_drafting.tasks.print_current_time',
        'args': json.dumps([]),
    }
)
