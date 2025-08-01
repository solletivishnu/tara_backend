# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.context_id = self.scope['url_route']['kwargs']['context_id']
        self.group_name = f'business_{self.context_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # You may not need this unless frontend sends messages.
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_attendance_update',
                'message': data.get('message', '')
            }
        )

    async def send_attendance_update(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
