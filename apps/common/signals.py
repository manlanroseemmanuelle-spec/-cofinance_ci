from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from apps.loans.models import LoanApplication
from apps.repayments.models import Repayment
from apps.insurance.models import Policy
from apps.notifications.models import Notification
from .models import AuditLog

User = get_user_model()


def _get_ip(request):
    if request and hasattr(request, 'META'):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
    return None


def _get_user(request):
    if request and hasattr(request, 'user'):
        return request.user if request.user.is_authenticated else None
    return None


def log_action(action, model_name, object_id, object_repr='', details='', request=None):
    AuditLog.objects.create(
        user=_get_user(request),
        action=action,
        model_name=model_name,
        object_id=object_id,
        object_repr=str(object_repr)[:255],
        details=details,
        ip_address=_get_ip(request),
    )


# ---------------------------------------------------------------------------
# LOAN CREATION — audit log + client notification
# ---------------------------------------------------------------------------
@receiver(post_save, sender=LoanApplication)
def log_loan_creation(sender, instance, created, **kwargs):
    if created:
        log_action(
            AuditLog.Action.CREATE, 'LoanApplication', instance.id,
            f"Pret #{instance.id} - {instance.montant_demande} FCFA",
            f"Client: {instance.client.user.get_full_name()}, Montant: {instance.montant_demande}, Duree: {instance.duree_mois} mois"
        )
        # Notify the client that their loan application has been submitted
        Notification.objects.create(
            titre=f"Pret #{instance.id} soumis",
            message=f"Votre demande de pret de {instance.montant_demande} FCFA a ete soumise avec succes et est en cours de traitement.",
            type=Notification.Type.CREDIT,
            user=instance.client.user,
        )


# ---------------------------------------------------------------------------
# REPAYMENT — audit log + notifications (client + agent)
# ---------------------------------------------------------------------------
@receiver(post_save, sender=Repayment)
def log_repayment(sender, instance, created, **kwargs):
    if created:
        log_action(
            AuditLog.Action.PAYMENT, 'Repayment', instance.id,
            f"Remboursement #{instance.id} - {instance.montant} FCFA",
            f"Pret #{instance.loan_id}, Montant: {instance.montant}, Mode: {instance.mode_paiement}, Ref: {instance.reference}"
        )
        # Notify the client
        Notification.objects.create(
            titre=f"Remboursement #{instance.id} - {instance.montant} FCFA",
            message=f"Remboursement de {instance.montant} FCFA enregistre pour le pret #{instance.loan_id}.",
            type=Notification.Type.REMBOURSEMENT,
            user=instance.loan.client.user,
        )
        # Notify the agent who recorded it
        if instance.agent:
            Notification.objects.create(
                titre=f"Remboursement #{instance.id} enregistre",
                message=f"Remboursement de {instance.montant} FCFA enregistre pour le pret #{instance.loan_id}.",
                type=Notification.Type.REMBOURSEMENT,
                user=instance.agent.user,
            )


# ---------------------------------------------------------------------------
# POLICY (insurance) — audit log + client notification
# ---------------------------------------------------------------------------
@receiver(post_save, sender=Policy)
def log_policy(sender, instance, created, **kwargs):
    if created:
        log_action(
            AuditLog.Action.CREATE, 'Policy', instance.id,
            f"Police #{instance.id} - {instance.produit.nom}",
            f"Client: {instance.client.user.get_full_name()}, Produit: {instance.produit.nom}"
        )
        Notification.objects.create(
            titre=f"Police #{instance.id} - {instance.produit.nom}",
            message=f"Votre police d'assurance {instance.produit.nom} a ete creee avec succes. Valable du {instance.date_debut} au {instance.date_fin}.",
            type=Notification.Type.ASSURANCE,
            user=instance.client.user,
        )
