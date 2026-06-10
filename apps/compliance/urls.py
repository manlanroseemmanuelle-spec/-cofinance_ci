from django.urls import path
from . import views

urlpatterns = [
    path('reports/', views.RegulatoryReportListCreateView.as_view(), name='report-list'),
    path('reports/<int:pk>/', views.RegulatoryReportDetailView.as_view(), name='report-detail'),
    path('reports/<int:pk>/finalize/', views.RegulatoryReportFinalizeView.as_view(), name='report-finalize'),
    path('ratios/', views.PrudentialRatioListView.as_view(), name='ratio-list'),
    path('ratios/compute/', views.PrudentialRatioComputeView.as_view(), name='ratio-compute'),
    path('classifications/', views.ClassificationListView.as_view(), name='classification-list'),
    path('classifications/<int:loan_id>/', views.ClassificationUpdateView.as_view(), name='classification-update'),
    path('declarations/', views.DeclarationSuspicionListCreateView.as_view(), name='declaration-list'),
    path('dashboard/', views.ComplianceDashboardView.as_view(), name='compliance-dashboard'),
]
