import uuid

from django.db import models


class SavingsProduct(models.Model):
    class TypeProduit(models.TextChoices):
        DEPOT_A_VUE = 'DAV', 'Dépôt à Vue'
        DEPOT_A_TERME = 'DAT', 'Dépôt à Terme'
        EPARGNE_PROGRAMMEE = 'EPARGNE', 'Épargne Programmée'
        EPARGNE_LOGEMENT = 'LOGEMENT', 'Épargne Logement'

    nom = models.CharField(max_length=200, verbose_name="Nom du produit")
    description = models.TextField(blank=True, verbose_name="Description")
    taux_interet_annuel = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Taux d'intérêt annuel (%)"
    )
    duree_jours = models.IntegerField(
        null=True, blank=True, verbose_name="Durée (jours)",
        help_text="Laissez vide pour une durée illimitée",
    )
    montant_min = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name="Montant minimum"
    )
    montant_max = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name="Montant maximum"
    )
    type = models.CharField(
        max_length=10, choices=TypeProduit.choices, verbose_name="Type de produit"
    )
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Produit d'épargne"
        verbose_name_plural = "Produits d'épargne"
        ordering = ['nom']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['est_actif']),
        ]

    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"


class SavingsAccount(models.Model):
    class StatutCompte(models.TextChoices):
        ACTIF = 'ACTIF', 'Actif'
        CLOTURE = 'CLOTURE', 'Clôturé'
        BLOQUE = 'BLOQUE', 'Bloqué'

    client = models.ForeignKey(
        'accounts.Client', on_delete=models.CASCADE, related_name='comptes_epargne',
        verbose_name="Client",
    )
    produit = models.ForeignKey(
        SavingsProduct, on_delete=models.PROTECT, related_name='comptes',
        verbose_name="Produit d'épargne",
    )
    numero_compte = models.CharField(
        max_length=20, unique=True, verbose_name="Numéro de compte"
    )
    solde = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, verbose_name="Solde"
    )
    statut = models.CharField(
        max_length=10, choices=StatutCompte.choices, default=StatutCompte.ACTIF,
        verbose_name="Statut",
    )
    date_ouverture = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ouverture")
    date_cloture = models.DateField(null=True, blank=True, verbose_name="Date de clôture")

    class Meta:
        verbose_name = "Compte d'épargne"
        verbose_name_plural = "Comptes d'épargne"
        ordering = ['-date_ouverture']
        indexes = [
            models.Index(fields=['statut']),
            models.Index(fields=['client', 'statut']),
        ]

    def save(self, *args, **kwargs):
        if not self.numero_compte:
            self.numero_compte = f"CMP-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_compte} - {self.client}"


class SavingsTransaction(models.Model):
    class TypeTransaction(models.TextChoices):
        VERSEMENT = 'VERSEMENT', 'Versement'
        RETRAIT = 'RETRAIT', 'Retrait'
        INTERET_CREDITEUR = 'INTERET_CREDITEUR', 'Intérêt créditeur'
        FRAIS = 'FRAIS', 'Frais'

    compte = models.ForeignKey(
        SavingsAccount, on_delete=models.CASCADE, related_name='transactions',
        verbose_name="Compte",
    )
    type = models.CharField(
        max_length=20, choices=TypeTransaction.choices, verbose_name="Type de transaction"
    )
    montant = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name="Montant"
    )
    solde_avant = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name="Solde avant"
    )
    solde_apres = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name="Solde après"
    )
    reference = models.CharField(
        max_length=100, unique=True, blank=True, verbose_name="Référence"
    )
    agent = models.ForeignKey(
        'accounts.Agent', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transactions_epargne', verbose_name="Agent",
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    date_transaction = models.DateTimeField(auto_now_add=True, verbose_name="Date de transaction")

    class Meta:
        verbose_name = "Transaction d'épargne"
        verbose_name_plural = "Transactions d'épargne"
        ordering = ['-date_transaction']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['compte', 'date_transaction']),
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"TXN-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.get_type_display()} ({self.montant})"
