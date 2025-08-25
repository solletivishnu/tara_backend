# attendance/routing.py

from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    re_path(r"^ws/attendance/(?P<employee_id>\d+)/$", consumer.AttendanceConsumer.as_asgi()),
    re_path(r"^ws/leave_notification/(?P<employee_id>\d+)/$", consumer.LeaveNotificationConsumer.as_asgi()),
]
