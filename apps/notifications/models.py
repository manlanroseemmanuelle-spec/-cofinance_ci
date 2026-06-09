from django.db import models
from django.conf import settings


class Notification(models.Model):
    class Type(models.TextChoices):
        CREDIT = 'CREDIT', 'Crédit'
        ASSURANCE = 'ASSURANCE', 'Assurance'
        REMBOURSEMENT = 'REMBOURSEMENT', 'Remboursement'
        CHAT = 'CHAT', 'Chat'
        SYSTEME = 'SYSTEME', 'Système'

    titre = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.SYSTEME)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['user', 'lu']),
            models.Index(fields=['date_creation']),
        ]

    def __str__(self):
        return f"{self.titre} - {self.user.username}"
