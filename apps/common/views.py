from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'message': 'Cofinance CI API is running'})
