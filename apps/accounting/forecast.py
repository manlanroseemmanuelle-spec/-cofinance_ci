from datetime import date, timedelta
from decimal import Decimal


def prevoir_tresorerie(jours=90):
    """
    Prévision de trésorerie basée sur les échéances à venir et les décaissements prévus.
    """
    from django.db.models import Sum
    from apps.loans.models import AmortizationSchedule, LoanApplication
    from django.utils import timezone

    today = timezone.now().date()
    horizon = today + timedelta(days=jours)

    # Entrées prévues (remboursements à venir)
    entrees = AmortizationSchedule.objects.filter(
        est_paye=False,
        date_echeance__gte=today,
        date_echeance__lte=horizon,
        loan__statut='DECAISSEE',
    ).aggregate(total=Sum('mensualite'))['total'] or 0

    # Sorties prévues (décaissements de prêts approuvés)
    sorties = LoanApplication.objects.filter(
        statut='APPROUVEE',
        date_mise_a_jour__gte=today,
    ).aggregate(total=Sum('montant_demande'))['total'] or 0

    return {
        'horizon_jours': jours,
        'entrees_prevues': float(entrees),
        'sorties_prevues': float(sorties),
        'solde_projete': float(entrees - sorties),
    }
