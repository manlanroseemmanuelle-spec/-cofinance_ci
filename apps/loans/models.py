from django.db import models
from django.conf import settings


class LoanApplication(models.Model):
    class Statut(models.TextChoices):
        SOUMISE = 'SOUMISE', 'Soumise'
        EN_ANALYSE = 'EN_ANALYSE', 'En analyse'
        APPROUVEE = 'APPROUVEE', 'Approuvée'
        REJETEE = 'REJETEE', 'Rejetée'
        DECAISSEE = 'DECAISSEE', 'Décaissée'

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

    def __str__(self):
        return f"{self.get_type_display()} - Prêt {self.loan.id}"


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

    def __str__(self):
        return f"#{self.loan.id}: {self.ancien_statut} -> {self.nouveau_statut}"
