from django.db import models
from django.core.validators import MinValueValidator


class PaymentGatewayConfig(models.Model):
    code = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    api_url = models.URLField()
    api_key = models.TextField(help_text="Chiffrer au repos (AES-256-GCM)")
    api_secret = models.TextField(help_text="Chiffrer au repos (AES-256-GCM)")
    frais_pourcentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    frais_fixe = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    est_actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Passerelle de paiement"
        verbose_name_plural = "Passerelles de paiement"

    def __str__(self):
        return f"{self.nom} ({self.code})"


class PaymentTransaction(models.Model):
    STATUT_CHOICES = [
        ("INITIE", "INITIÉ"),
        ("EN_COURS", "EN COURS"),
        ("SUCCES", "SUCCÈS"),
        ("ECHEC", "ÉCHEC"),
        ("REMBOURSE", "REMBOURSÉ"),
    ]
    TYPE_CHOICES = [
        ("VERSEMENT_EPARGNE", "Versement épargne"),
        ("REMBOURSEMENT_CREDIT", "Remboursement crédit"),
        ("DECAISSEMENT", "Décaissement"),
    ]

    gateway = models.ForeignKey(
        PaymentGatewayConfig, on_delete=models.PROTECT, related_name="transactions"
    )
    loan = models.ForeignKey(
        "loans.LoanApplication",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paiements",
    )
    compte = models.ForeignKey(
        "savings.SavingsAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_transactions",
    )
    reference_interne = models.CharField(max_length=100, unique=True)
    reference_externe = models.CharField(max_length=100, blank=True)
    montant = models.DecimalField(
        max_digits=14, decimal_places=2, validators=[MinValueValidator(0)]
    )
    frais = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    devise = models.CharField(max_length=5, default="XOF")
    telephone = models.CharField(max_length=20)
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default="INITIE", db_index=True
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_execution = models.DateTimeField(null=True, blank=True)
    callback_data = models.JSONField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Transaction de paiement"
        verbose_name_plural = "Transactions de paiement"
        indexes = [
            models.Index(fields=["statut", "reference_interne"]),
        ]

    def __str__(self):
        return f"{self.reference_interne} — {self.montant} {self.devise} ({self.get_statut_display()})"


class MobileMoneyAccount(models.Model):
    OPERATEUR_CHOICES = [
        ("ORANGE_MONEY", "Orange Money"),
        ("WAVE", "Wave"),
        ("MTN_MOMO", "MTN MoMo"),
    ]

    client = models.ForeignKey(
        "accounts.Client",
        on_delete=models.CASCADE,
        related_name="mobile_money_accounts",
    )
    operateur = models.CharField(max_length=20, choices=OPERATEUR_CHOICES)
    telephone = models.CharField(max_length=20)
    est_verifie = models.BooleanField(default=False)
    est_actif = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Compte Mobile Money"
        verbose_name_plural = "Comptes Mobile Money"
        constraints = [
            models.UniqueConstraint(
                fields=["client", "operateur", "telephone"],
                name="uq_client_operateur_telephone",
            ),
        ]

    def __str__(self):
        return f"{self.get_operateur_display()} — {self.telephone}"
