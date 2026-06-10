from django.contrib import admin
from .models import PaymentGatewayConfig, PaymentTransaction, MobileMoneyAccount


@admin.register(PaymentGatewayConfig)
class PaymentGatewayConfigAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'est_actif', 'frais_pourcentage', 'frais_fixe']
    exclude = ['api_key', 'api_secret']


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['reference_interne', 'gateway', 'montant', 'statut', 'type', 'telephone', 'date_creation']
    list_filter = ['statut', 'type', 'date_creation']
    search_fields = ['reference_interne', 'reference_externe', 'telephone']


@admin.register(MobileMoneyAccount)
class MobileMoneyAccountAdmin(admin.ModelAdmin):
    list_display = ['client', 'operateur', 'telephone', 'est_verifie', 'est_actif', 'date_ajout']
    list_filter = ['operateur', 'est_verifie', 'est_actif']
