from django.contrib import admin
from .models import SolidarityGroup, GroupMember, GroupeLoan


@admin.register(SolidarityGroup)
class SolidarityGroupAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type', 'centre', 'region', 'responsable', 'agent', 'date_creation', 'statut']
    list_filter = ['type', 'statut', 'region']
    search_fields = ['nom', 'centre', 'region']


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['client', 'groupe', 'role', 'date_adhesion', 'est_actif']
    list_filter = ['role', 'est_actif']
    search_fields = ['client__user__first_name', 'client__user__last_name', 'groupe__nom']


@admin.register(GroupeLoan)
class GroupeLoanAdmin(admin.ModelAdmin):
    list_display = ['groupe', 'loan', 'type_caution']
    list_filter = ['type_caution']
    search_fields = ['groupe__nom', 'loan__id']
