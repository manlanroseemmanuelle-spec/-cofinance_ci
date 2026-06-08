from django.contrib import admin
from .models import LoanApplication, AmortizationSchedule, Document


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'montant_demande', 'duree_mois', 'statut', 'score_eligibilite', 'date_creation']
    list_filter = ['statut', 'date_creation']
    search_fields = ['client__user__first_name', 'client__user__last_name']


@admin.register(AmortizationSchedule)
class AmortizationScheduleAdmin(admin.ModelAdmin):
    list_display = ['loan', 'numero_mensualite', 'date_echeance', 'mensualite', 'est_paye']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['loan', 'type', 'date_upload']
