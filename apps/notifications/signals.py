from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification
from .serializers import NotificationSerializer


@receiver(post_save, sender=Notification)
def push_notification_via_websocket(sender, instance, created, **kwargs):
    if not created:
        return
    channel_layer = get_channel_layer()
    serializer = NotificationSerializer(instance)
    async_to_sync(channel_layer.group_send)(
        f'notifications_user_{instance.user_id}',
        {
            'type': 'send_notification',
            'notification': serializer.data,
        },
    )
