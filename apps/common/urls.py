from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('audit/', views.AuditLogListView.as_view(), name='audit-log'),
    path('audit/export/pdf/', views.AuditLogExportPdfView.as_view(), name='audit-export-pdf'),
    path('search/', views.GlobalSearchView.as_view(), name='global-search'),
]
