from django.db import models
from django.utils.translation import gettext_lazy as _


class RegulatoryReport(models.Model):
    class TypeChoices(models.TextChoices):
        MENSUEL = "MENSUEL", _("Mensuel")
        TRIMESTRIEL = "TRIMESTRIEL", _("Trimestriel")
        ANNUEL = "ANNUEL", _("Annuel")

    class StatutChoices(models.TextChoices):
        BROUILLON = "BROUILLON", _("Brouillon")
        FINALISE = "FINALISE", _("Finalisé")
        TRANSMIS = "TRANSMIS", _("Transmis")

    type = models.CharField(
        max_length=20,
        choices=TypeChoices.choices,
        verbose_name=_("Type"),
    )
    periode = models.CharField(
        max_length=7,
        help_text=_("YYYY-MM for monthly, YYYY-T for quarterly, YYYY for annual"),
        verbose_name=_("Période"),
    )
    date_generation = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de génération"),
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutChoices.choices,
        default=StatutChoices.BROUILLON,
        verbose_name=_("Statut"),
    )
    contenu = models.JSONField(verbose_name=_("Contenu"))
    generated_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        verbose_name=_("Généré par"),
    )

    class Meta:
        verbose_name = _("Rapport réglementaire")
        verbose_name_plural = _("Rapports réglementaires")
        unique_together = ("type", "periode")
        indexes = [
            models.Index(fields=["type", "periode"]),
            models.Index(fields=["statut"]),
            models.Index(fields=["date_generation"]),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.periode}"


class PrudentialRatio(models.Model):
    class StatutChoices(models.TextChoices):
        CONFORME = "CONFORME", _("Conforme")
        NON_CONFORME = "NON_CONFORME", _("Non conforme")
        EN_SURVEILLANCE = "EN_SURVEILLANCE", _("En surveillance")

    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Code"),
    )
    nom = models.CharField(
        max_length=200,
        verbose_name=_("Nom"),
    )
    formule = models.TextField(
        help_text=_("Description du calcul"),
        verbose_name=_("Formule"),
    )
    seuil_min = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Seuil minimum"),
    )
    valeur_actuelle = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Valeur actuelle"),
    )
    date_calcul = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de calcul"),
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutChoices.choices,
        default=StatutChoices.EN_SURVEILLANCE,
        verbose_name=_("Statut"),
    )

    class Meta:
        verbose_name = _("Ratio prudentiel")
        verbose_name_plural = _("Ratios prudentiels")
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["statut"]),
            models.Index(fields=["date_calcul"]),
        ]

    def __str__(self):
        return f"{self.nom} ({self.code})"


class LoanClassification(models.Model):
    class ClasseChoices(models.TextChoices):
        SAINE = "SAINE", _("Saine")
        SOUS_SURVEILLANCE = "SOUS_SURVEILLANCE", _("Sous surveillance")
        DOUTEUSE = "DOUTEUSE", _("Douteuse")
        COMPROMISE = "COMPROMISE", _("Compromise")

    loan = models.OneToOneField(
        "loans.LoanApplication",
        on_delete=models.CASCADE,
        unique=True,
        verbose_name=_("Prêt"),
    )
    classe = models.CharField(
        max_length=30,
        choices=ClasseChoices.choices,
        verbose_name=_("Classe"),
    )
    jours_retard = models.IntegerField(
        default=0,
        verbose_name=_("Jours de retard"),
    )
    taux_provision = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("Taux de provision"),
    )
    montant_provision = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name=_("Montant de la provision"),
    )
    date_classification = models.DateField(
        auto_now_add=True,
        verbose_name=_("Date de classification"),
    )
    date_mise_a_jour = models.DateField(
        auto_now=True,
        verbose_name=_("Date de mise à jour"),
    )

    class Meta:
        verbose_name = _("Classification de créance")
        verbose_name_plural = _("Classifications de créances")
        indexes = [
            models.Index(fields=["classe"]),
            models.Index(fields=["jours_retard"]),
            models.Index(fields=["date_classification"]),
            models.Index(fields=["date_mise_a_jour"]),
        ]

    def __str__(self):
        return f"{self.loan} - {self.get_classe_display()}"


class DeclarationSuspicion(models.Model):
    client = models.ForeignKey(
        "accounts.Client",
        on_delete=models.CASCADE,
        verbose_name=_("Client"),
    )
    transaction = models.CharField(
        max_length=100,
        verbose_name=_("Transaction"),
    )
    montant = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_("Montant"),
    )
    motifs = models.TextField(verbose_name=_("Motifs"))
    date_faits = models.DateField(verbose_name=_("Date des faits"))
    date_declaration = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de déclaration"),
    )
    declared_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        verbose_name=_("Déclaré par"),
    )
    reference = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name=_("Référence"),
    )

    class Meta:
        verbose_name = _("Déclaration de soupçon")
        verbose_name_plural = _("Déclarations de soupçon")
        indexes = [
            models.Index(fields=["client"]),
            models.Index(fields=["date_faits"]),
            models.Index(fields=["date_declaration"]),
            models.Index(fields=["reference"]),
        ]

    def __str__(self):
        return f"{self.client} - {self.reference or self.transaction}"
