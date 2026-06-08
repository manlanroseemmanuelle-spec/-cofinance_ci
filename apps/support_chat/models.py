from django.db import models
from django.conf import settings


class Conversation(models.Model):
    class Statut(models.TextChoices):
        OUVERTE = 'OUVERTE', 'Ouverte'
        FERMEE = 'FERMEE', 'Fermée'

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_conversations'
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='agent_conversations'
    )
    status = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.OUVERTE
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-date_mise_a_jour']

    def __str__(self):
        return f"Conversation {self.id} - {self.client.username}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"Message de {self.sender.username} dans {self.conversation.id}"
