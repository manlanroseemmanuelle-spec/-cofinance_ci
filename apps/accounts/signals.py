from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.notifications.models import Notification
from apps.common.models import AuditLog
from apps.common.signals import log_action

User = get_user_model()


@receiver(post_save, sender=User)
def log_user_registration(sender, instance, created, **kwargs):
    if created:
        log_action(
            AuditLog.Action.CREATE, 'User', instance.id,
            f"Utilisateur {instance.username}",
            f"Nom: {instance.get_full_name()}, Role: {instance.role}, Telephone: {instance.telephone}"
        )
        # Send welcome notification to new user
        Notification.objects.create(
            titre="Bienvenue sur CoFinance CI",
            message=f"Bienvenue {instance.get_full_name()}! Votre compte a ete cree avec succes. Nous sommes ravis de vous compter parmi nous.",
            type=Notification.Type.SYSTEME,
            user=instance,
        )