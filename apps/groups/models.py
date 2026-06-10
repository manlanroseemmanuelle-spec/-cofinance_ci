from django.db import models
from django.conf import settings


class SolidarityGroup(models.Model):
    class TypeChoices(models.TextChoices):
        SHG = 'SHG', 'Self-Help Group'
        JLG = 'JLG', 'Joint Liability Group'

    class StatutChoices(models.TextChoices):
        ACTIF = 'ACTIF', 'Actif'
        INACTIF = 'INACTIF', 'Inactif'
        DISSOUS = 'DISSOUS', 'Dissous'

    nom = models.CharField(max_length=200)
    type = models.CharField(max_length=3, choices=TypeChoices.choices)
    centre = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100)
    responsable = models.ForeignKey(
        'accounts.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='groups_responsible',
    )
    agent = models.ForeignKey(
        'accounts.Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_groups',
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=8,
        choices=StatutChoices.choices,
        default=StatutChoices.ACTIF,
    )

    class Meta:
        verbose_name = 'Groupe Solidaire'
        verbose_name_plural = 'Groupes Solidaires'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['statut']),
            models.Index(fields=['region']),
        ]

    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"


class GroupMember(models.Model):
    class RoleChoices(models.TextChoices):
        CHEF = 'CHEF', 'Chef'
        MEMBRE = 'MEMBRE', 'Membre'
        SECRETAIRE = 'SECRETAIRE', 'Secrétaire'

    groupe = models.ForeignKey(
        SolidarityGroup,
        on_delete=models.CASCADE,
        related_name='members',
    )
    client = models.ForeignKey(
        'accounts.Client',
        on_delete=models.CASCADE,
        related_name='solidarity_groups',
    )
    role = models.CharField(
        max_length=10,
        choices=RoleChoices.choices,
        default=RoleChoices.MEMBRE,
    )
    date_adhesion = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Membre du Groupe'
        verbose_name_plural = 'Membres du Groupe'
        ordering = ['groupe', 'role']
        constraints = [
            models.UniqueConstraint(
                fields=['groupe', 'client'],
                name='unique_group_member',
            ),
        ]
        indexes = [
            models.Index(fields=['groupe', 'client']),
            models.Index(fields=['est_actif']),
        ]

    def __str__(self):
        return f"{self.client} - {self.groupe} ({self.get_role_display()})"


class GroupeLoan(models.Model):
    class TypeCautionChoices(models.TextChoices):
        SOLIDAIRE = 'SOLIDAIRE', 'Solidaire'
        INDIVIDUELLE = 'INDIVIDUELLE', 'Individuelle'

    groupe = models.ForeignKey(
        SolidarityGroup,
        on_delete=models.CASCADE,
        related_name='loans',
    )
    loan = models.ForeignKey(
        'loans.LoanApplication',
        on_delete=models.CASCADE,
        related_name='groupe_loan',
    )
    type_caution = models.CharField(
        max_length=12,
        choices=TypeCautionChoices.choices,
        default=TypeCautionChoices.SOLIDAIRE,
    )

    class Meta:
        verbose_name = 'Prêt de Groupe'
        verbose_name_plural = 'Prêts de Groupe'
        ordering = ['groupe', 'loan']
        indexes = [
            models.Index(fields=['groupe', 'loan']),
            models.Index(fields=['type_caution']),
        ]

    def __str__(self):
        return f"Prêt {self.loan} - {self.groupe}"
