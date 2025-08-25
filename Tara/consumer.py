# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import localdate
from channels.db import database_sync_to_async
from django.utils import timezone


class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Expect URL like ws://localhost:8000/ws/attendance/7/
        self.employee_id = self.scope["url_route"]["kwargs"]["employee_id"]

        # Join employee-specific group
        self.user_group = f"user_{self.employee_id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)

        # Optionally: also join their business group if needed
        # For now just user-based
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "ws_connected",
            "employee_id": self.employee_id
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group, self.channel_name)

    # Server push handler
    async def send_attendance_update(self, event):
        await self.send(text_data=json.dumps(event.get("payload", {})))



class LeaveNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.employee_id = self.scope["url_route"]["kwargs"]["employee_id"]
        print(f"WebSocket connected for employee_id: {self.employee_id}")

        self.user_group = f"user_{self.employee_id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "ws_connected",
            "employee_id": self.employee_id
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive(self, text_data):
        """Handle messages from WebSocket client"""
        data = json.loads(text_data)
        
        if data.get('type') == 'mark_read':
            notification_id = data.get('notification_id')
            try:
                notification = await self.get_notification(notification_id)
                await self.mark_notification_read(notification)
                unread_count = await self.get_unread_count()
                
                payload = {
                    "type": "leave_notification",
                    "action": "read",
                    "notification_id": notification_id,
                    "unread_count": unread_count
                }
                
                await self.channel_layer.group_send(
                    self.user_group,
                    {
                        "type": "send_leave_notification",
                        "payload": payload
                    }
                )
            
            except Exception as e:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": str(e)
                }))

    async def send_leave_notification(self, event):
        """Handle incoming notification events"""
        try:
            await self.send(text_data=json.dumps(event["payload"]))
        except Exception as e:
            print(f"Error sending notification: {str(e)}")  # Debug print
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Error processing notification"
            }))

    @database_sync_to_async
    def get_notification(self, notification_id):
        # Import models here instead of at module level
        from payroll.models import LeaveNotification
        return LeaveNotification.objects.get(
            id=notification_id, 
            reviewer_id=self.employee_id
        )

    @database_sync_to_async
    def mark_notification_read(self, notification):
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return notification

    @database_sync_to_async
    def get_unread_count(self):
        # Import models here instead of at module level
        from payroll.models import LeaveNotification
        return LeaveNotification.objects.filter(
            reviewer_id=self.employee_id, 
            is_read=False
        ).count()