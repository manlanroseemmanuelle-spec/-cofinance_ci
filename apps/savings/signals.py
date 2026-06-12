from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.savings.models import SavingsAccount, SavingsTransaction
from apps.notifications.models import Notification
from apps.common.models import AuditLog
from apps.common.signals import log_action


@receiver(post_save, sender=SavingsAccount)
def log_savings_account_creation(sender, instance, created, **kwargs):
    if created:
        log_action(
            AuditLog.Action.CREATE, 'SavingsAccount', instance.id,
            f"Compte epargne {instance.numero_compte}",
            f"Client: {instance.client.user.get_full_name()}, Produit: {instance.produit.nom}"
        )
        Notification.objects.create(
            titre=f"Compte epargne {instance.numero_compte} ouvert",
            message=f"Votre compte epargne {instance.numero_compte} ({instance.produit.nom}) a ete ouvert avec succes.",
            type=Notification.Type.SYSTEME,
            user=instance.client.user,
        )


@receiver(post_save, sender=SavingsTransaction)
def log_savings_transaction(sender, instance, created, **kwargs):
    if created:
        type_labels = dict(SavingsTransaction.TypeTransaction.choices)
        log_action(
            AuditLog.Action.CREATE, 'SavingsTransaction', instance.id,
            f"{type_labels.get(instance.type, instance.type)} - {instance.montant} FCFA",
            f"Compte: {instance.compte.numero_compte}, Montant: {instance.montant}, Solde avant: {instance.solde_avant}, Solde apres: {instance.solde_apres}"
        )