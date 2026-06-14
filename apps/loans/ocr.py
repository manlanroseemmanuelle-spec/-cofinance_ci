def simuler_ocr(fichier):
    """
    Simulation d'OCR pour l'extraction des informations depuis une pièce d'identité.
    Dans une version production, utiliser Tesseract ou une API cloud.
    """
    from datetime import date
    return {
        'nom_complet': '[Simulé] Nom du client',
        'numero_piece': f'OCR-{fichier.name[:8].upper() if hasattr(fichier, "name") else "UNKNOWN"}',
        'date_naissance': str(date(1990, 1, 1)),
        'date_expiration': str(date(2030, 1, 1)),
        'nationalite': 'CIV',
        'confiance': 0.85,
    }
