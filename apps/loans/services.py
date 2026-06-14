from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.db import models
from .models import LoanApplication, AmortizationSchedule


def calculer_score_eligibilite(client):
    from django.utils import timezone
    score = 0

    if client.revenu_mensuel > 300000:
        score += 40

    bons_remboursements = client.loan_applications.filter(
        statut=LoanApplication.Statut.DECAISSEE
    ).count()
    if bons_remboursements > 0:
        score += 30

    if client.date_naissance:
        age = timezone.now().year - client.date_naissance.year
        if age >= 18:
            score += 20

    if hasattr(client, 'insurance_policies'):
        policies_actives = client.insurance_policies.filter(
            statut='ACTIVE'
        ).count()
        if policies_actives > 0:
            score += 10

    # Ratio d'endettement
    from apps.repayments.models import Repayment
    total_mensualites = Repayment.objects.filter(
        loan__client=client,
        loan__statut=LoanApplication.Statut.DECAISSEE,
    ).aggregate(total=models.Sum('montant'))['total'] or 0
    if client.revenu_mensuel > 0:
        ratio = total_mensualites / client.revenu_mensuel
        if ratio > 0.4:
            score -= 20

    # Ancienneté du compte
    if hasattr(client, 'user') and client.user.date_joined:
        if (timezone.now() - client.user.date_joined).days > 365:
            score += 10

    # Remboursements effectués à temps
    on_time = Repayment.objects.filter(
        loan__client=client,
        penalite=0,
    ).count()
    score += min(on_time * 5, 20)

    # Compte épargne avec solde > 0
    if hasattr(client, 'comptes_epargne'):
        epargne_positif = client.comptes_epargne.filter(
            solde__gt=0,
            statut='ACTIF',
        ).exists()
        if epargne_positif:
            score += 15

    # Pénalités passées
    penalites = Repayment.objects.filter(
        loan__client=client,
        penalite__gt=0,
    ).count()
    score -= penalites * 10

    return min(score, 100)


def generer_echeancier(loan):
    AmortizationSchedule.objects.filter(loan=loan).delete()

    frais_dossier = Decimal('0')
    if loan.produit and loan.produit.frais_dossier > 0:
        frais_dossier = loan.montant_demande * (loan.produit.frais_dossier / Decimal('100'))

    capital = loan.montant_demande + frais_dossier
    taux_mensuel = (loan.taux_interet / 100) / 12
    n_mensualites = loan.duree_mois

    mensualite = capital * (taux_mensuel * (1 + taux_mensuel) ** n_mensualites) / \
                 ((1 + taux_mensuel) ** n_mensualites - 1)

    capital_restant = capital
    date_debut = date.today() + relativedelta(months=1)

    for i in range(1, n_mensualites + 1):
        part_interet = capital_restant * taux_mensuel
        part_capital = mensualite - part_interet
        capital_restant -= part_capital

        if i == n_mensualites:
            part_capital += capital_restant
            mensualite = part_capital + part_interet
            capital_restant = 0

        AmortizationSchedule.objects.create(
            loan=loan,
            mensualite=round(mensualite, 2),
            date_echeance=date_debut + relativedelta(months=i - 1),
            capital_restant=round(max(capital_restant, 0), 2),
            part_capital=round(part_capital, 2),
            part_interet=round(part_interet, 2),
            numero_mensualite=i,
        )
