from django.contrib import admin
from .models import LoanApplication, AmortizationSchedule, Document, LoanProduct, Collateral, LoanRestructuring, GracePeriod


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'produit', 'montant_demande', 'duree_mois', 'statut', 'score_eligibilite', 'date_creation']
    list_filter = ['statut', 'produit', 'date_creation']
    search_fields = ['client__user__first_name', 'client__user__last_name']


@admin.register(AmortizationSchedule)
class AmortizationScheduleAdmin(admin.ModelAdmin):
    list_display = ['loan', 'numero_mensualite', 'date_echeance', 'mensualite', 'est_paye']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['loan', 'type', 'date_upload']


@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'type_pret', 'taux_interet_annuel', 'montant_min', 'montant_max', 'est_actif']
    list_filter = ['type_pret', 'est_actif']


@admin.register(Collateral)
class CollateralAdmin(admin.ModelAdmin):
    list_display = ['loan', 'type', 'valeur_estimee', 'caution_solidaire']


@admin.register(LoanRestructuring)
class LoanRestructuringAdmin(admin.ModelAdmin):
    list_display = ['loan', 'type', 'statut', 'date_soumission']


@admin.register(GracePeriod)
class GracePeriodAdmin(admin.ModelAdmin):
    list_display = ['loan', 'mois_debut', 'mois_fin', 'type_interet']
