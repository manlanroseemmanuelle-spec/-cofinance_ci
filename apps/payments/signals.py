import logging
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.payments.models import PaymentTransaction

logger = logging.getLogger(__name__)


@receiver(post_save, sender=PaymentTransaction)
def executer_transaction_paiement(sender, instance, **kwargs):
    if instance.statut != 'SUCCES':
        return

    try:
        _traiter_transaction(instance)
    except Exception as e:
        logger.error(
            "Erreur lors du traitement de la transaction #%s: %s",
            instance.id, str(e), exc_info=True,
        )


def _traiter_transaction(tx):
    if tx.type == 'DECAISSEMENT' and tx.loan_id:
        _decaisser_pret(tx)

    elif tx.type == 'REMBOURSEMENT_CREDIT' and tx.loan_id:
        _rembourser_credit(tx)

    elif tx.type == 'VERSEMENT_EPARGNE' and tx.compte_id:
        _verser_epargne(tx)


def _decaisser_pret(tx):
    loan = tx.loan
    if loan.statut == 'DECAISSEE':
        logger.info("Prêt #%s déjà décaissé, ignoré", loan.id)
        return

    loan.statut = 'DECAISSEE'
    loan.save()

    # Écriture comptable
    from apps.accounting.models import Account, JournalEntry, JournalEntryLine

    compte_caisse, _ = Account.objects.get_or_create(
        code='101', defaults={'nom': 'Caisse', 'type': 'ACTIF'}
    )
    compte_client, _ = Account.objects.get_or_create(
        code='161', defaults={'nom': 'Créances clients', 'type': 'ACTIF'}
    )
    ref = f"DEC-{tx.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    entry = JournalEntry.objects.create(
        journal='CAISSE', reference=ref,
        date_ecriture=timezone.now().date(),
        libelle=f"Décaissement prêt #{loan.id} — {loan.client.user.get_full_name()}",
        loan=loan, client=loan.client,
    )
    JournalEntryLine.objects.create(
        entry=entry, account=compte_caisse, sens='CREDIT',
        montant=tx.montant, libelle='Décaissement prêt',
    )
    JournalEntryLine.objects.create(
        entry=entry, account=compte_client, sens='DEBIT',
        montant=tx.montant, libelle='Créance client',
    )

    # Notifications
    from apps.notifications.models import Notification
    Notification.objects.create(
        user=loan.client.user,
        titre="Prêt décaissé",
        message=f"Votre prêt #{loan.id} de {tx.montant} FCFA a été décaissé avec succès.",
    )
    if loan.agent:
        Notification.objects.create(
            user=loan.agent.user,
            titre="Décaissement effectué",
            message=f"Le prêt #{loan.id} de {loan.client.user.get_full_name()} a été décaissé.",
        )

    logger.info("Décaissement prêt #%s traité avec succès", loan.id)


def _rembourser_credit(tx):
    loan = tx.loan
    from apps.repayments.models import Repayment

    # Vérifier si déjà traité
    if Repayment.objects.filter(
        reference__startswith=f"PAY-{tx.reference_interne}"
    ).exists():
        logger.info("Remboursement tx #%s déjà traité, ignoré", tx.id)
        return

    if loan.statut not in ('DECAISSEE', 'REMBOURSEE'):
        logger.warning("Prêt #%s non décaissé, remboursement ignoré", loan.id)
        return
    if loan.statut == 'REMBOURSEE':
        logger.warning("Prêt #%s déjà remboursé, ignoré", loan.id)
        return

    # Échéance à payer
    amort = loan.amortization_schedule.filter(est_paye=False).order_by('date_echeance').first()

    repayment = Repayment.objects.create(
        loan=loan, montant=tx.montant,
        mode_paiement='ORANGE_MONEY',
        reference=f"PAY-{tx.reference_interne}",
        notes=f"Via {tx.gateway.nom} — {tx.reference_interne}",
        amortization=amort,
        agent=loan.agent,
    )

    penalite = repayment.calculer_penalite()
    if penalite:
        repayment.penalite = penalite
        repayment.save()

    if amort:
        amort.est_paye = True
        amort.save()

    # Vérifier soldé
    unpaid = loan.amortization_schedule.filter(est_paye=False).count()
    if unpaid == 0 and loan.statut == 'DECAISSEE':
        loan.statut = 'REMBOURSEE'
        loan.save()

    # Écriture comptable
    from apps.accounting.models import Account, JournalEntry, JournalEntryLine

    compte_caisse, _ = Account.objects.get_or_create(
        code='101', defaults={'nom': 'Caisse', 'type': 'ACTIF'}
    )
    compte_client, _ = Account.objects.get_or_create(
        code='411', defaults={'nom': 'Clients', 'type': 'ACTIF'}
    )
    compte_interets, _ = Account.objects.get_or_create(
        code='701', defaults={'nom': 'Revenus', 'type': 'PRODUIT'}
    )

    principal = tx.montant - (penalite or Decimal('0'))
    ref = f"REM-{tx.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    entry = JournalEntry.objects.create(
        journal='CAISSE', reference=ref,
        date_ecriture=timezone.now().date(),
        libelle=f"Remboursement prêt #{loan.id} via {tx.gateway.nom}",
        loan=loan, client=loan.client,
    )
    JournalEntryLine.objects.create(
        entry=entry, account=compte_caisse, sens='DEBIT',
        montant=tx.montant, libelle='Encaissement remboursement',
    )
    JournalEntryLine.objects.create(
        entry=entry, account=compte_client, sens='CREDIT',
        montant=principal, libelle='Remboursement principal',
    )
    if penalite and penalite > 0:
        JournalEntryLine.objects.create(
            entry=entry, account=compte_interets, sens='CREDIT',
            montant=penalite, libelle='Pénalité de retard',
        )

    logger.info("Remboursement tx #%s traité avec succès", tx.id)


def _verser_epargne(tx):
    compte = tx.compte
    from apps.savings.models import SavingsTransaction

    # Vérifier si déjà traité
    if SavingsTransaction.objects.filter(
        reference=f"PAY-{tx.reference_interne}"
    ).exists():
        logger.info("Versement tx #%s déjà traité, ignoré", tx.id)
        return

    solde_avant = compte.solde
    SavingsTransaction.objects.create(
        compte=compte, type='VERSEMENT',
        montant=tx.montant,
        solde_avant=solde_avant,
        solde_apres=solde_avant + tx.montant,
        reference=f"PAY-{tx.reference_interne}",
        notes=f"Versement via {tx.gateway.nom} ({tx.reference_interne})",
    )

    compte.solde += tx.montant
    compte.save()

    # Notification
    from apps.notifications.models import Notification
    Notification.objects.create(
        user=compte.client.user,
        titre="Versement épargne reçu",
        message=f"Un versement de {tx.montant} FCFA a été crédité sur votre compte épargne {compte.numero_compte}.",
    )

    logger.info("Versement épargne tx #%s traité avec succès", tx.id)
