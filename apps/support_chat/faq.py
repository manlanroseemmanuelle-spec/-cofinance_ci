FAQ = {
    'délai': 'Le délai de traitement d\'une demande de crédit est de 48h à 72h ouvrées après soumission des documents.',
    'taux': 'Nos taux d\'intérêt varient de 5% à 15% selon le produit et la durée. Consultez notre grille tarifaire.',
    'remboursement': 'Les remboursements peuvent être effectués par Orange Money, Wave, MTN MoMo ou en espèces en agence.',
    'document': 'Les pièces requises sont : pièce d\'identité, justificatif de revenu, photo d\'identité et garantie selon le montant.',
    'épargne': 'Nos produits d\'épargne offrent des taux allant jusqu\'à 5% annuel selon le type de compte.',
    'assurance': 'L\'assurance crédit couvre le remboursement en cas d\'imprévu (décès, invalidité, perte d\'emploi).',
    'score': 'Votre score de crédit est calculé sur la base de votre revenu, historique de remboursement, âge et assurance active.',
    'plafond': 'Le montant maximum de crédit est déterminé par votre profil et peut aller jusqu\'à 10 000 000 FCFA.',
    'délai_remboursement': 'Les délais de remboursement s\'étendent de 3 à 60 mois selon le produit choisi.',
}


def repondre_faq(message):
    """Retourne une réponse automatique si le message contient un mot-clé connu."""
    message_lower = message.lower()
    for mot_cle, reponse in FAQ.items():
        if mot_cle in message_lower:
            return reponse
    return None
