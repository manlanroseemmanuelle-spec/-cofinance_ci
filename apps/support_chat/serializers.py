from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['timestamp', 'is_read']


class MessageCreateSerializer(serializers.Serializer):
    message = serializers.CharField()


class ConversationSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    agent_name = serializers.CharField(source='agent.get_full_name', read_only=True, allow_null=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_mise_a_jour']

    @extend_schema_field(serializers.DictField(child=serializers.CharField(), allow_null=True))
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'message': last_msg.message[:100],
                'timestamp': last_msg.timestamp,
                'sender': last_msg.sender.username
            }
        return None

    @extend_schema_field(serializers.IntegerField())
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class ConversationCreateSerializer(serializers.Serializer):
    pass
