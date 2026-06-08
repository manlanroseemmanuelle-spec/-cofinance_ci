from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Client, Agent


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'telephone', 'region', 'is_active']
    list_filter = ['role', 'is_active', 'region']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('telephone', 'adresse', 'region', 'photo', 'role')}),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['user', 'profession', 'revenu_mensuel', 'score_credit', 'numero_piece']
    search_fields = ['user__first_name', 'user__last_name', 'numero_piece']


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['user', 'matricule', 'region']
    search_fields = ['user__first_name', 'user__last_name', 'matricule']
