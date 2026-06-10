from django.contrib import admin
from .models import RegulatoryReport, PrudentialRatio, LoanClassification, DeclarationSuspicion


@admin.register(RegulatoryReport)
class RegulatoryReportAdmin(admin.ModelAdmin):
    list_display = ['type', 'periode', 'statut', 'date_generation', 'generated_by']
    list_filter = ['type', 'statut']
    search_fields = ['periode']


@admin.register(PrudentialRatio)
class PrudentialRatioAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'valeur_actuelle', 'statut', 'date_calcul']
    list_filter = ['statut']
    search_fields = ['code', 'nom']


@admin.register(LoanClassification)
class LoanClassificationAdmin(admin.ModelAdmin):
    list_display = ['loan', 'classe', 'jours_retard', 'taux_provision', 'montant_provision', 'date_classification']
    list_filter = ['classe']
    search_fields = ['loan__reference']


@admin.register(DeclarationSuspicion)
class DeclarationSuspicionAdmin(admin.ModelAdmin):
    list_display = ['client', 'reference', 'transaction', 'montant', 'date_faits', 'date_declaration', 'declared_by']
    search_fields = ['reference', 'transaction', 'client__user__username']
    list_filter = ['date_faits', 'date_declaration']
