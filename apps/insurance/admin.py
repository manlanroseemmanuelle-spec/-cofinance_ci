from django.contrib import admin
from .models import InsuranceProduct, Policy


@admin.register(InsuranceProduct)
class InsuranceProductAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prix', 'duree_jours', 'est_actif']
    list_filter = ['est_actif']


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ['client', 'produit', 'date_debut', 'date_fin', 'statut']
    list_filter = ['statut']
