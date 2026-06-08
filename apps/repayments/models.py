from django.db import models
from django.utils import timezone
from decimal import Decimal


class Repayment(models.Model):
    class ModePaiement(models.TextChoices):
        ORANGE_MONEY = 'ORANGE_MONEY', 'Orange Money'
        WAVE = 'WAVE', 'Wave'
        MTN_MOMO = 'MTN_MOMO', 'MTN MoMo'
        ESPECES = 'ESPECES', 'Espèces'

    loan = models.ForeignKey(
        'loans.LoanApplication',
        on_delete=models.CASCADE,
        related_name='repayments'
    )
    amortization = models.ForeignKey(
        'loans.AmortizationSchedule',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='repayments'
    )
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    penalite = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date_paiement = models.DateTimeField(auto_now_add=True)
    mode_paiement = models.CharField(max_length=20, choices=ModePaiement.choices)
    agent = models.ForeignKey(
        'accounts.Agent',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='enregistre_repayments'
    )
    reference = models.CharField(max_length=100, blank=True, unique=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Remboursement'
        verbose_name_plural = 'Remboursements'
        ordering = ['-date_paiement']

    def __str__(self):
        return f"Remboursement {self.id} - Prêt {self.loan.id} - {self.montant} FCFA"

    def calculer_penalite(self):
        if self.amortization and self.amortization.date_echeance < timezone.now().date():
            jours_retard = (timezone.now().date() - self.amortization.date_echeance).days
            taux_penalite = Decimal('0.01')
            penalite = self.montant * taux_penalite * Decimal(str(jours_retard))
            return round(penalite, 2)
        return Decimal('0')
