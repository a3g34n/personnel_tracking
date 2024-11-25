from celery import shared_task
from notifications.models import Notification
from personnel.models import User

@shared_task
def send_notification(user_id, message):
    user = User.objects.get(id=user_id)
    Notification.objects.create(user=user, message=message)
    return f'Notification sent to {user.username}'
