from django.contrib import admin
from .models import Repayment


@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'loan', 'montant', 'penalite', 'mode_paiement', 'date_paiement', 'reference']
    list_filter = ['mode_paiement', 'date_paiement']
    search_fields = ['reference', 'loan__id']
