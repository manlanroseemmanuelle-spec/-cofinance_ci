from django.contrib import admin
from .models import SavingsProduct, SavingsAccount, SavingsTransaction


@admin.register(SavingsProduct)
class SavingsProductAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type', 'taux_interet_annuel', 'montant_min', 'montant_max', 'est_actif']
    list_filter = ['type', 'est_actif']
    search_fields = ['nom', 'description']


@admin.register(SavingsAccount)
class SavingsAccountAdmin(admin.ModelAdmin):
    list_display = ['numero_compte', 'client', 'produit', 'solde', 'statut', 'date_ouverture']
    list_filter = ['statut', 'produit']
    search_fields = ['numero_compte', 'client__user__first_name', 'client__user__last_name']
    readonly_fields = ['numero_compte', 'solde', 'date_ouverture']


@admin.register(SavingsTransaction)
class SavingsTransactionAdmin(admin.ModelAdmin):
    list_display = ['reference', 'compte', 'type', 'montant', 'solde_avant', 'solde_apres', 'date_transaction']
    list_filter = ['type', 'date_transaction']
    search_fields = ['reference', 'compte__numero_compte']
    readonly_fields = ['reference', 'solde_avant', 'solde_apres', 'date_transaction']
