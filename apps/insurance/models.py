from django.db import models
from django.conf import settings
from django.utils import timezone


class InsuranceProduct(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    duree_jours = models.IntegerField()
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Produit d\'assurance'
        verbose_name_plural = 'Produits d\'assurance'

    def __str__(self):
        return self.nom


class Policy(models.Model):
    class Statut(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        EXPIREE = 'EXPIREE', 'Expirée'
        ANNULEE = 'ANNULEE', 'Annulée'

    client = models.ForeignKey(
        'accounts.Client',
        on_delete=models.CASCADE,
        related_name='insurance_policies'
    )
    produit = models.ForeignKey(
        InsuranceProduct,
        on_delete=models.CASCADE,
        related_name='policies'
    )
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.ACTIVE
    )
    date_souscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Police d\'assurance'
        verbose_name_plural = 'Polices d\'assurance'

    def __str__(self):
        return f"{self.client} - {self.produit.nom}"

    def save(self, *args, **kwargs):
        if not self.date_debut:
            self.date_debut = timezone.now().date()
        if not self.date_fin:
            self.date_fin = self.date_debut + timezone.timedelta(days=self.produit.duree_jours)
        super().save(*args, **kwargs)
