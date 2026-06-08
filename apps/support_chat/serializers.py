from rest_framework import serializers
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

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'message': last_msg.message[:100],
                'timestamp': last_msg.timestamp,
                'sender': last_msg.sender.username
            }
        return None

    def get_unread_count(self, obj):
        return obj.messages.filter(is_read=False).exclude(sender=self.context['request'].user).count()


class ConversationCreateSerializer(serializers.Serializer):
    pass
