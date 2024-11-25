from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from celery import shared_task
from notifications.models import Notification
from personnel.models import User

@shared_task
def send_notification(user_id, message):
    try:
        user = User.objects.get(id=user_id)
        Notification.objects.create(user=user, message=message)

        # WebSocket üzerinden bildirim gönder
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "send_notification",
                "message": message,
            }
        )
        return f"Notification sent to {user.username}"
    except User.DoesNotExist:
        return f"User with id {user_id} does not exist"
