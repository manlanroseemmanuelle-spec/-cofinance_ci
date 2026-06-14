from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'CLIENT', 'Client'
        AGENT = 'AGENT', 'Agent de terrain'
        ADMIN = 'ADMIN', 'Administrateur'
        AUDITEUR = 'AUDITEUR', 'Auditeur'
        COMPTABLE = 'COMPTABLE', 'Comptable'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    telephone = models.CharField(max_length=20, unique=True)
    adresse = models.TextField(blank=True)
    region = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    profession = models.CharField(max_length=100)
    revenu_mensuel = models.DecimalField(max_digits=12, decimal_places=2)
    score_credit = models.IntegerField(default=0)
    date_naissance = models.DateField()
    numero_piece = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f"Client: {self.user.get_full_name()}"

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save()


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    matricule = models.CharField(max_length=50, unique=True)
    region = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'

    def __str__(self):
        return f"Agent: {self.user.get_full_name()} ({self.matricule})"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Token de réinitialisation'
        verbose_name_plural = 'Tokens de réinitialisation'

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Reset token for {self.user.username} (expires {self.expires_at})"


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    date_connexion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Historique de connexion'
        verbose_name_plural = 'Historiques de connexion'
        ordering = ['-date_connexion']

    def __str__(self):
        return f"{self.user.username} - {self.date_connexion}"
