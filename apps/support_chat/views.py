from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, ConversationCreateSerializer,
    MessageSerializer, MessageCreateSerializer
)
from apps.accounts.permissions import IsAdminOrAgent, IsConversationParticipant

User = get_user_model()


@extend_schema(tags=['Chat'])
class ConversationListCreateView(generics.ListCreateAPIView):
    queryset = Conversation.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ConversationCreateSerializer
        return ConversationSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Conversation.objects.none()
        user = self.request.user
        if user.role == 'CLIENT':
            return Conversation.objects.filter(client=user)
        elif user.role == 'AGENT':
            return Conversation.objects.filter(agent=user)
        return Conversation.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'CLIENT':
            available_agent = User.objects.filter(
                role='ADMIN', is_active=True
            ).annotate(
                open_count=Count('agent_conversations', filter=Q(agent_conversations__status='OUVERTE'))
            ).order_by('open_count').first()
            conv = Conversation.objects.create(client=user, agent=available_agent)
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seuls les clients peuvent ouvrir une conversation.")
        # Return full conversation data in response
        from rest_framework.renderers import JSONRenderer
        self.created_conv = conv

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        if hasattr(self, 'created_conv'):
            resp_serializer = ConversationSerializer(self.created_conv, context={'request': request})
            return Response(resp_serializer.data, status=status.HTTP_201_CREATED)
        return Response({}, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Chat'])
class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsConversationParticipant]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Conversation.objects.none()
        user = self.request.user
        queryset = Conversation.objects.select_related('client', 'agent')
        if user.role == 'CLIENT':
            return queryset.filter(client=user)
        if user.role == 'AGENT':
            return queryset.filter(agent=user)
        return queryset


@extend_schema(tags=['Chat'])
class ConversationCloseView(generics.UpdateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAdminOrAgent]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Conversation.objects.none()
        if self.request.user.role == 'AGENT':
            return Conversation.objects.filter(agent=self.request.user)
        return Conversation.objects.all()

    def perform_update(self, serializer):
        conversation = self.get_object()
        conversation.status = Conversation.Statut.FERMEE
        conversation.save()


@extend_schema(tags=['Chat'])
class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Message.objects.none()
        user = self.request.user
        conversations = Conversation.objects.filter(id=self.kwargs['conversation_id'])
        if user.role == 'CLIENT':
            conversations = conversations.filter(client=user)
        elif user.role == 'AGENT':
            conversations = conversations.filter(agent=user)
        return Message.objects.select_related('sender', 'conversation').filter(conversation__in=conversations)

    def list(self, request, *args, **kwargs):
        messages = self.get_queryset()
        messages.exclude(sender=request.user).update(is_read=True)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


@extend_schema(tags=['Chat'])
class MessageCreateView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        from django.shortcuts import get_object_or_404
        user = self.request.user
        conversations = Conversation.objects.filter(id=self.kwargs['conversation_id'])
        if user.role == 'CLIENT':
            conversations = conversations.filter(client=user)
        elif user.role == 'AGENT':
            conversations = conversations.filter(agent=user)
        conversation = get_object_or_404(conversations)
        Message.objects.create(
            conversation=conversation,
            sender=self.request.user,
            message=serializer.validated_data['message']
        )


@extend_schema(tags=['Chat'])
class AssignAgentView(generics.UpdateAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAdminOrAgent]

    def perform_update(self, serializer):
        conversation = self.get_object()
        conversation.agent = self.request.user
        conversation.save()
