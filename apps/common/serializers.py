from rest_framework import serializers
from .models import AuditLog
from apps.accounts.serializers import UserSerializer


class AuditLogSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'
