from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Création'
        UPDATE = 'UPDATE', 'Modification'
        DELETE = 'DELETE', 'Suppression'
        LOGIN = 'LOGIN', 'Connexion'
        STATUS_CHANGE = 'STATUS_CHANGE', 'Changement de statut'
        PAYMENT = 'PAYMENT', 'Paiement'
        ASSIGN = 'ASSIGN', 'Assignation'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Utilisateur'
    )
    action = models.CharField(max_length=20, choices=Action.choices, verbose_name='Action')
    model_name = models.CharField(max_length=100, verbose_name='Modèle')
    object_id = models.IntegerField(null=True, blank=True, verbose_name='ID objet')
    object_repr = models.CharField(max_length=255, blank=True, verbose_name='Représentation')
    details = models.TextField(blank=True, verbose_name='Détails')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='Adresse IP')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Date')

    class Meta:
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journal d'audit"
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%d/%m/%Y %H:%M}] {self.get_action_display()} - {self.model_name}#{self.object_id}"
