from django.apps import AppConfig
import sys

class DocumentDraftingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'document_drafting'

    def ready(self):
        if 'gunicorn' in sys.argv or 'celery' in sys.argv:
            try:
                from Tara.scheduler_scripts.schedule_tasks import sync_schedules
                sync_schedules()
                print("✅ Celery schedule synced on startup.")
            except Exception as e:
                print(f"⚠️ Failed to sync schedule: {e}")
