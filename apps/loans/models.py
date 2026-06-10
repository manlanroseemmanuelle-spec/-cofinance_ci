from django.db import models
from django.conf import settings
from decimal import Decimal


class LoanApplication(models.Model):
    class Statut(models.TextChoices):
        SOUMISE = 'SOUMISE', 'Soumise'
        EN_ANALYSE = 'EN_ANALYSE', 'En analyse'
        APPROUVEE = 'APPROUVEE', 'Approuvée'
        REJETEE = 'REJETEE', 'Rejetée'
        DECAISSEE = 'DECAISSEE', 'Décaissée'

    produit = models.ForeignKey(
        'LoanProduct', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='loan_applications',
        verbose_name='Produit de crédit'
    )
    client = models.ForeignKey(
        'accounts.Client',
        on_delete=models.CASCADE,
        related_name='loan_applications'
    )
    montant_demande = models.DecimalField(max_digits=12, decimal_places=2)
    duree_mois = models.IntegerField()
    motif = models.TextField()
    revenu_mensuel = models.DecimalField(max_digits=12, decimal_places=2)
    score_eligibilite = models.IntegerField(default=0)
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.SOUMISE
    )
    taux_interet = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    agent = models.ForeignKey(
        'accounts.Agent',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='analysed_loans'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Demande de crédit'
        verbose_name_plural = 'Demandes de crédit'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['client', 'statut']),
            models.Index(fields=['agent', 'statut']),
            models.Index(fields=['date_creation']),
        ]

    def __str__(self):
        return f"Crédit {self.id} - {self.client} - {self.montant_demande} FCFA"

    @property
    def est_eligible(self):
        return self.score_eligibilite >= 50


class AmortizationSchedule(models.Model):
    loan = models.ForeignKey(
        LoanApplication, on_delete=models.CASCADE,
        related_name='amortization_schedule'
    )
    mensualite = models.DecimalField(max_digits=12, decimal_places=2)
    date_echeance = models.DateField()
    capital_restant = models.DecimalField(max_digits=12, decimal_places=2)
    part_capital = models.DecimalField(max_digits=12, decimal_places=2)
    part_interet = models.DecimalField(max_digits=12, decimal_places=2)
    est_paye = models.BooleanField(default=False)
    numero_mensualite = models.IntegerField()

    class Meta:
        verbose_name = 'Échéance'
        verbose_name_plural = 'Échéances'
        ordering = ['date_echeance']
        constraints = [
            models.UniqueConstraint(fields=['loan', 'numero_mensualite'], name='unique_loan_numero_mensualite'),
        ]
        indexes = [
            models.Index(fields=['loan', 'est_paye']),
            models.Index(fields=['date_echeance', 'est_paye']),
        ]

    def __str__(self):
        return f"Échéance {self.numero_mensualite} - Prêt {self.loan.id}"


class Document(models.Model):
    class TypeDocument(models.TextChoices):
        PIECE_IDENTITE = 'PIECE_IDENTITE', "Pièce d'identité"
        JUSTIFICATIF_REVENU = 'JUSTIFICATIF_REVENU', 'Justificatif de revenu'
        PHOTO_CLIENT = 'PHOTO_CLIENT', 'Photo du client'

    loan = models.ForeignKey(
        LoanApplication, on_delete=models.CASCADE,
        related_name='documents'
    )
    type = models.CharField(max_length=30, choices=TypeDocument.choices)
    fichier = models.FileField(upload_to='documents/')
    date_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        indexes = [
            models.Index(fields=['loan', 'type']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - Prêt {self.loan.id}"


class LoanProduct(models.Model):
    class TypePret(models.TextChoices):
        PERSONNEL = 'PERSONNEL', 'Personnel'
        PROFESSIONNEL = 'PROFESSIONNEL', 'Professionnel'
        EQUIPEMENT = 'EQUIPEMENT', 'Équipement'
        AGRICOLE = 'AGRICOLE', 'Agricole'
        GROUPE = 'GROUPE', 'Groupe'
        SAISONNIER = 'SAISONNIER', 'Saisonnier'

    class FrequenceRemb(models.TextChoices):
        MENSUEL = 'MENSUEL', 'Mensuel'
        HEBDOMADAIRE = 'HEBDOMADAIRE', 'Hebdomadaire'
        TRIMESTRIEL = 'TRIMESTRIEL', 'Trimestriel'

    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    type_pret = models.CharField(max_length=20, choices=TypePret.choices, default=TypePret.PERSONNEL)
    description = models.TextField(blank=True)
    taux_interet_annuel = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    montant_min = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    montant_max = models.DecimalField(max_digits=14, decimal_places=2)
    duree_min_mois = models.IntegerField(default=1)
    duree_max_mois = models.IntegerField(default=60)
    frequence_remboursement = models.CharField(max_length=20, choices=FrequenceRemb.choices, default=FrequenceRemb.MENSUEL)
    taux_penalite_jour = models.DecimalField(max_digits=5, decimal_places=3, default=Decimal('1.000'))
    garantie_requise = models.BooleanField(default=False)
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Produit de crédit'
        verbose_name_plural = 'Produits de crédit'
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.code})"


class Collateral(models.Model):
    class TypeGarantie(models.TextChoices):
        BIEN_IMMOBILIER = 'BIEN_IMMOBILIER', 'Bien immobilier'
        VEHICULE = 'VEHICULE', 'Véhicule'
        CAUTION_SOLIDAIRE = 'CAUTION_SOLIDAIRE', 'Caution solidaire'
        DEPOT_GARANTIE = 'DEPOT_GARANTIE', 'Dépôt de garantie'
        MATERIEL = 'MATERIEL', 'Matériel'
        AUTRE = 'AUTRE', 'Autre'

    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='collaterals')
    type = models.CharField(max_length=20, choices=TypeGarantie.choices)
    description = models.TextField()
    valeur_estimee = models.DecimalField(max_digits=14, decimal_places=2)
    caution_solidaire = models.ForeignKey('accounts.Client', on_delete=models.SET_NULL, null=True, blank=True, related_name='garanties_donnees')
    fichier_justificatif = models.FileField(upload_to='collaterals/', blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Garantie'
        verbose_name_plural = 'Garanties'

    def __str__(self):
        return f"{self.get_type_display()} - Prêt #{self.loan_id}"


class LoanRestructuring(models.Model):
    class TypeRestructuration(models.TextChoices):
        REECHELONNEMENT = 'REECHELONNEMENT', 'Rééchelonnement'
        REFINANCEMENT = 'REFINANCEMENT', 'Refinancement'
        REPORT_ECHEANCE = 'REPORT_ECHEANCE', "Report d'échéance"
        REDUCTION_TAUX = 'REDUCTION_TAUX', 'Réduction de taux'

    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='restructurings')
    type = models.CharField(max_length=20, choices=TypeRestructuration.choices)
    statut = models.CharField(max_length=20, choices=[('SOUMISE', 'Soumise'), ('APPROUVEE', 'Approuvée'), ('REJETEE', 'Rejetée')], default='SOUMISE')
    nouvelle_duree_mois = models.IntegerField(null=True, blank=True)
    nouveau_taux = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    nouveau_montant = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    motif = models.TextField()
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_approbation = models.DateTimeField(null=True, blank=True)
    approuve_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='restructurings_approved')

    class Meta:
        verbose_name = 'Restructuration de prêt'
        verbose_name_plural = 'Restructurations de prêt'

    def __str__(self):
        return f"{self.get_type_display()} - Prêt #{self.loan_id}"


class GracePeriod(models.Model):
    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='grace_periods')
    mois_debut = models.IntegerField(help_text="Numéro de mensualité de début")
    mois_fin = models.IntegerField(help_text="Numéro de mensualité de fin")
    type_interet = models.CharField(max_length=20, choices=[('CAPITALISE', 'Capitalisé'), ('PAYE', 'Payé')], default='CAPITALISE')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Période de grâce'
        verbose_name_plural = 'Périodes de grâce'

    def __str__(self):
        return f"Grâce Prêt #{self.loan_id}: mois {self.mois_debut}-{self.mois_fin}"


class LoanStatusHistory(models.Model):
    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='status_history', verbose_name='Prêt')
    ancien_statut = models.CharField(max_length=20, blank=True, verbose_name='Ancien statut')
    nouveau_statut = models.CharField(max_length=20, verbose_name='Nouveau statut')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Modifié par')
    commentaire = models.TextField(blank=True, verbose_name='Commentaire')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date')

    class Meta:
        verbose_name = "Historique de statut"
        verbose_name_plural = "Historiques de statut"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['loan', 'date']),
        ]

    def __str__(self):
        return f"#{self.loan.id}: {self.ancien_statut} -> {self.nouveau_statut}"
