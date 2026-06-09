from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from .models import LoanApplication, AmortizationSchedule


def calculer_score_eligibilite(client):
    score = 0

    if client.revenu_mensuel > 300000:
        score += 40

    bons_remboursements = client.loan_applications.filter(
        statut=LoanApplication.Statut.DECAISSEE
    ).count()
    if bons_remboursements > 0:
        score += 30

    from django.utils import timezone
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

    return min(score, 100)


def generer_echeancier(loan):
    AmortizationSchedule.objects.filter(loan=loan).delete()

    capital = loan.montant_demande
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
