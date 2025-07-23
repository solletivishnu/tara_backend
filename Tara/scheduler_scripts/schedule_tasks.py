from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

# Step 1: Create or get the interval (every 10 minutes)
schedule, _ = IntervalSchedule.objects.get_or_create(
    every=10,
    period=IntervalSchedule.MINUTES,
)

# Step 2: Get or create the periodic task
task, created = PeriodicTask.objects.get_or_create(
    name='Print Current Time Every Minute',  # Keep same name or rename for clarity
    defaults={
        'task': 'document_drafting.tasks.print_current_time',
        'args': json.dumps([]),
    }
)

# Step 3: Force-assign the interval and update other values if needed
task.interval = schedule
task.task = 'document_drafting.tasks.print_current_time'
task.args = json.dumps([])

# Step 4: Save the task (this ensures the FK is updated)
task.save()
