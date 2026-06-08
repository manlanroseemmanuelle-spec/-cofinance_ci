from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Notification
from .serializers import NotificationSerializer


@extend_schema(tags=['Notifications'])
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@extend_schema(tags=['Notifications'])
class NotificationMarkReadView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def perform_update(self, serializer):
        notification = self.get_object()
        notification.lu = True
        notification.save()


@extend_schema(tags=['Notifications'])
class NotificationMarkAllReadView(generics.GenericAPIView):
    def post(self, request):
        Notification.objects.filter(user=request.user, lu=False).update(lu=True)
        return Response({'message': 'Toutes les notifications marquées comme lues'})


@extend_schema(tags=['Notifications'])
class UnreadCountView(generics.GenericAPIView):
    def get(self, request):
        count = Notification.objects.filter(user=request.user, lu=False).count()
        return Response({'unread_count': count})
