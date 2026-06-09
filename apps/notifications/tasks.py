from celery import shared_task
from django.utils import timezone

from apps.insurance.models import Policy
from apps.loans.models import AmortizationSchedule
from .models import Notification


def _create_once(user, titre, message, type_notification):
    Notification.objects.get_or_create(
        user=user,
        titre=titre,
        message=message,
        type=type_notification,
    )


@shared_task
def envoyer_alertes_echeances():
    today = timezone.now().date()
    j_minus_3 = today + timezone.timedelta(days=3)
    j_plus_1 = today - timezone.timedelta(days=1)

    upcoming = AmortizationSchedule.objects.select_related('loan__client__user').filter(
        est_paye=False,
        date_echeance=j_minus_3,
    )
    for echeance in upcoming:
        user = echeance.loan.client.user
        _create_once(
            user,
            f"Échéance crédit J-3 - prêt #{echeance.loan_id}",
            f"Votre échéance de {echeance.mensualite} FCFA est prévue le {echeance.date_echeance}.",
            Notification.Type.REMBOURSEMENT,
        )

    late = AmortizationSchedule.objects.select_related('loan__client__user').filter(
        est_paye=False,
        date_echeance=j_plus_1,
    )
    for echeance in late:
        user = echeance.loan.client.user
        _create_once(
            user,
            f"Retard de paiement J+1 - prêt #{echeance.loan_id}",
            f"Votre échéance du {echeance.date_echeance} est en retard. Merci de régulariser rapidement.",
            Notification.Type.REMBOURSEMENT,
        )


@shared_task
def envoyer_alertes_expiration_assurance():
    target_date = timezone.now().date() + timezone.timedelta(days=15)
    policies = Policy.objects.select_related('client__user', 'produit').filter(
        statut=Policy.Statut.ACTIVE,
        date_fin=target_date,
    )
    for policy in policies:
        _create_once(
            policy.client.user,
            f"Expiration assurance J-15 - {policy.produit.nom}",
            f"Votre assurance {policy.produit.nom} expire le {policy.date_fin}. Pensez au renouvellement.",
            Notification.Type.ASSURANCE,
        )
