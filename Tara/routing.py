# attendance/routing.py

from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    re_path(r'ws/attendance/(?P<context_id>\w+)/$', consumer.AttendanceConsumer.as_asgi()),
]
