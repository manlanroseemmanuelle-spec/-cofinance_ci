from celery import shared_task
from django.utils import timezone
from decimal import Decimal


@shared_task
def calculer_interets_epargne():
    from .models import SavingsAccount, SavingsTransaction
    from django.db.models import F
    comptes = SavingsAccount.objects.filter(statut='ACTIF')
    for compte in comptes:
        taux = compte.produit.taux_interet_annuel / Decimal('12') / 100
        interets = compte.solde * taux
        if interets > 0:
            SavingsTransaction.objects.create(
                compte=compte,
                type='INTERET_CREDITEUR',
                montant=interets,
                notes='Intérêts créditeurs mensuels',
                solde_avant=compte.solde,
                solde_apres=compte.solde + interets,
            )
            SavingsAccount.objects.filter(id=compte.id).update(solde=F('solde') + interets)
