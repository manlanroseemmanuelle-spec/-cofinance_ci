from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, generics
from drf_spectacular.utils import extend_schema
from .models import AuditLog
from .serializers import AuditLogSerializer
from apps.accounts.permissions import IsAdmin


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'message': 'Cofinance CI API is running'})


@extend_schema(tags=['Audit'])
class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]
    search_fields = ['action', 'model_name', 'object_repr', 'details', 'user__username']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
