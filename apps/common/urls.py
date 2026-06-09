from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('audit/', views.AuditLogListView.as_view(), name='audit-log'),
]
