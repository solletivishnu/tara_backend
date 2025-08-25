# broadcast.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

_channel = get_channel_layer()


def broadcast_to_employee(employee_id: int, payload: dict):
    """
    Sends payload to the employee-specific group.
    Your consumer must add connections to group: f"user_{employee_id}"
    """
    async_to_sync(_channel.group_send)(
        f"user_{employee_id}",
        {"type": "send_attendance_update", "payload": payload}
    )


def broadcast_to_business(business_id: int, payload: dict):
    """
    Sends payload to the whole business/team group.
    Your consumer must add connections to group: f"business_{business_id}"
    """
    async_to_sync(_channel.group_send)(
        f"business_{business_id}",
        {"type": "send_attendance_update", "payload": payload}
    )


def broadcast_leave_notification_to_employee(employee_id: int, payload: dict):
    """
    Sends leave notification to the employee-specific group.
    Your consumer must add connections to group: f"user_{employee_id}"
    """
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{employee_id}",
            {
                "type": "send_leave_notification",
                "payload": payload
            }
        )
    except Exception as e:
        print(f"Error broadcasting notification: {str(e)}")  # Debug print
