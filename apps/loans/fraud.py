from decimal import Decimal


def detecter_fraude(loan_request, client):
    """
    Règles simples de détection de fraude.
    Retourne une liste d'alertes.
    """
    alerts = []

    # Règle 1: Montant incohérent avec le revenu
    if loan_request.montant_demande > client.revenu_mensuel * 12:
        alerts.append("Le montant demandé dépasse 12x le revenu mensuel")

    # Règle 2: Multiples demandes simultanées
    from .models import LoanApplication
    recent_loans = LoanApplication.objects.filter(
        client=client,
        statut__in=['SOUMISE', 'EN_ANALYSE'],
    ).count()
    if recent_loans > 2:
        alerts.append(f"{recent_loans} demandes simultanées en cours")

    # Règle 3: Revenu déclaré incohérent avec la profession
    low_income_professions = ['agriculteur', 'ouvrier', 'ménagère']
    if loan_request.revenu_mensuel > Decimal('500000') and \
       any(p in client.profession.lower() for p in low_income_professions):
        alerts.append("Revenu élevé incohérent avec la profession déclarée")

    # Règle 4: Pas de pièce d'identité
    if client.numero_piece.startswith('TMP-'):
        alerts.append("Pièce d'identité temporaire ou manquante")

    return alerts
