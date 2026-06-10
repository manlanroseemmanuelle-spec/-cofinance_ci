from django.contrib import admin
from .models import Account, JournalEntry, JournalEntryLine


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'type', 'niveau', 'parent', 'solde_actuel', 'est_actif']
    list_filter = ['type', 'niveau', 'est_actif']
    search_fields = ['code', 'nom']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['reference', 'journal', 'date_ecriture', 'libelle', 'est_validee', 'date_creation']
    list_filter = ['journal', 'est_validee', 'date_ecriture']
    search_fields = ['reference', 'libelle']
    readonly_fields = ['reference', 'date_creation', 'date_validation', 'validee_par']


@admin.register(JournalEntryLine)
class JournalEntryLineAdmin(admin.ModelAdmin):
    list_display = ['entry', 'account', 'sens', 'montant', 'libelle']
    list_filter = ['sens', 'account']
    search_fields = ['entry__reference', 'account__code', 'libelle']
