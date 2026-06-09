from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.loans.models import LoanApplication
from apps.repayments.models import Repayment
from apps.insurance.models import Policy
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


@receiver(post_save, sender=LoanApplication)
def log_loan_creation(sender, instance, created, **kwargs):
    if created:
        log_action(
            AuditLog.Action.CREATE, 'LoanApplication', instance.id,
            f"Prêt #{instance.id} - {instance.montant_demande} FCFA",
            f"Client: {instance.client.user.get_full_name()}, Montant: {instance.montant_demande}, Durée: {instance.duree_mois} mois"
        )


@receiver(post_save, sender=Repayment)
def log_repayment(sender, instance, created, **kwargs):
    if created:
        log_action(
            AuditLog.Action.PAYMENT, 'Repayment', instance.id,
            f"Remboursement #{instance.id} - {instance.montant} FCFA",
            f"Prêt #{instance.loan_id}, Montant: {instance.montant}, Mode: {instance.mode_paiement}, Réf: {instance.reference}"
        )


@receiver(post_save, sender=Policy)
def log_policy(sender, instance, created, **kwargs):
    if created:
        log_action(
            AuditLog.Action.CREATE, 'Policy', instance.id,

            f"Police #{instance.id} - {instance.produit.nom}",
            f"Client: {instance.client.user.get_full_name()}, Produit: {instance.produit.nom}"
        )
