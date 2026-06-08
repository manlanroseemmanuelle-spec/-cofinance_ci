from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'CLIENT', 'Client'
        AGENT = 'AGENT', 'Agent de terrain'
        ADMIN = 'ADMIN', 'Administrateur'

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

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f"Client: {self.user.get_full_name()}"


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    matricule = models.CharField(max_length=50, unique=True)
    region = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'

    def __str__(self):
        return f"Agent: {self.user.get_full_name()} ({self.matricule})"
