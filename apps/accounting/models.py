from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.conf import settings
from django.utils import timezone


class Account(models.Model):
    class TypeCompte(models.TextChoices):
        ACTIF = 'ACTIF', 'Actif'
        PASSIF = 'PASSIF', 'Passif'
        PRODUIT = 'PRODUIT', 'Produit'
        CHARGE = 'CHARGE', 'Charge'

    code = models.CharField(max_length=10, unique=True, verbose_name='Code')
    nom = models.CharField(max_length=200, verbose_name='Nom')
    type = models.CharField(
        max_length=10, choices=TypeCompte.choices, verbose_name='Type'
    )
    niveau = models.IntegerField(default=1, verbose_name='Niveau')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='enfants',
        verbose_name='Compte parent'
    )
    solde_actuel = models.DecimalField(
        max_digits=16, decimal_places=2, default=0,
        verbose_name='Solde actuel'
    )
    est_actif = models.BooleanField(default=True, verbose_name='Actif')

    class Meta:
        verbose_name = 'Compte'
        verbose_name_plural = 'Comptes'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['type']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"{self.code} - {self.nom}"


class JournalEntry(models.Model):
    class Journal(models.TextChoices):
        CAISSE = 'CAISSE', 'Caisse'
        BANQUE = 'BANQUE', 'Banque'
        OPERATIONS_DIVERSES = 'DIVERS', 'Opérations diverses'
        OD = 'OD', 'OD'
        ASSURANCE = 'ASSURANCE', 'Assurance'

    journal = models.CharField(
        max_length=20, choices=Journal.choices, verbose_name='Journal'
    )
    reference = models.CharField(
        max_length=100, unique=True, verbose_name='Référence'
    )
    date_ecriture = models.DateField(verbose_name="Date d'écriture")
    libelle = models.TextField(verbose_name='Libellé')
    loan = models.ForeignKey(
        'loans.LoanApplication',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ecritures_comptables',
        verbose_name='Prêt'
    )
    client = models.ForeignKey(
        'accounts.Client',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ecritures_comptables',
        verbose_name='Client'
    )
    agent = models.ForeignKey(
        'accounts.Agent',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ecritures_comptables',
        verbose_name='Agent'
    )
    est_validee = models.BooleanField(default=False, verbose_name='Validée')
    validee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='validated_entries',
        verbose_name='Validée par'
    )
    date_validation = models.DateTimeField(
        null=True, blank=True, verbose_name='Date de validation'
    )
    date_creation = models.DateTimeField(
        auto_now_add=True, verbose_name='Date de création'
    )

    class Meta:
        verbose_name = 'Écriture comptable'
        verbose_name_plural = 'Écritures comptables'
        ordering = ['-date_ecriture', '-date_creation']
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['date_ecriture']),
            models.Index(fields=['journal', 'date_ecriture']),
            models.Index(fields=['est_validee']),
        ]

    def __str__(self):
        return f"{self.reference} - {self.libelle[:50]}"

    @classmethod
    def generer_reference(cls, journal=None):
        prefix = 'EC'
        today = timezone.now().strftime('%Y%m%d')
        last_entry = cls.objects.filter(
            reference__startswith=f'{prefix}-{today}'
        ).order_by('reference').last()
        if last_entry and last_entry.reference:
            last_num = int(last_entry.reference.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        return f'{prefix}-{today}-{new_num:03d}'

    def valider(self, user):
        if self.est_validee:
            raise ValidationError("Cette écriture est déjà validée.")
        total_debit = self.lines.filter(sens='DEBIT').aggregate(total=models.Sum('montant'))['total'] or 0
        total_credit = self.lines.filter(sens='CREDIT').aggregate(total=models.Sum('montant'))['total'] or 0
        if total_debit != total_credit:
            raise ValidationError(
                "Le total des débits (%s) ne correspond pas au total des crédits (%s)." % (total_debit, total_credit)
            )
        self.est_validee = True
        self.validee_par = user
        self.date_validation = timezone.now()
        self.save()


class JournalEntryLine(models.Model):
    class Sens(models.TextChoices):
        DEBIT = 'DEBIT', 'Débit'
        CREDIT = 'CREDIT', 'Crédit'

    entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Écriture'
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='journal_lines',
        verbose_name='Compte'
    )
    sens = models.CharField(
        max_length=10, choices=Sens.choices, verbose_name='Sens'
    )
    montant = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name='Montant'
    )
    libelle = models.TextField(blank=True, verbose_name='Libellé')

    class Meta:
        verbose_name = 'Ligne d\'écriture'
        verbose_name_plural = 'Lignes d\'écriture'
        ordering = ['entry', 'id']
        indexes = [
            models.Index(fields=['entry']),
            models.Index(fields=['account']),
            models.Index(fields=['entry', 'account']),
        ]

    def __str__(self):
        return f"{self.entry.reference} - {self.account.code} ({self.sens}: {self.montant})"

    def clean(self):
        if self.montant <= 0:
            raise ValidationError({'montant': 'Le montant doit être supérieur à zéro.'})

    def update_account_balance(self):
        if self.sens == 'DEBIT':
            Account.objects.filter(pk=self.account.pk).update(solde_actuel=F('solde_actuel') + self.montant)
        elif self.sens == 'CREDIT':
            Account.objects.filter(pk=self.account.pk).update(solde_actuel=F('solde_actuel') - self.montant)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.update_account_balance()
