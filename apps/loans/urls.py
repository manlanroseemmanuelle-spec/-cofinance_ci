from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoanListCreateView.as_view(), name='loan-list'),
    path('mine/', views.MyLoansView.as_view(), name='my-loans'),
    path('export/csv/', views.LoanExportCsvView.as_view(), name='loan-export-csv'),
    path('export/pdf/', views.LoanExportPdfView.as_view(), name='loan-export-pdf'),
    path('<int:pk>/', views.LoanDetailView.as_view(), name='loan-detail'),
    path('<int:pk>/status/', views.LoanStatusUpdateView.as_view(), name='loan-status'),
    path('<int:loan_id>/schedule/', views.AmortizationScheduleListView.as_view(), name='loan-schedule'),
    path('<int:loan_id>/documents/', views.DocumentListCreateView.as_view(), name='loan-documents'),
    path('<int:loan_id>/history/', views.LoanStatusHistoryListView.as_view(), name='loan-history'),
    path('products/', views.LoanProductListView.as_view(), name='loan-products'),
    path('collaterals/', views.CollateralListCreateView.as_view(), name='collateral-list'),
    path('restructurings/', views.LoanRestructuringListCreateView.as_view(), name='restructuring-list'),
    path('restructurings/<int:pk>/action/', views.LoanRestructuringActionView.as_view(), name='restructuring-action'),
    path('grace-periods/', views.GracePeriodListCreateView.as_view(), name='grace-period-list'),
    path('<int:loan_id>/grace-periods/', views.GracePeriodListCreateView.as_view(), name='grace-period-by-loan'),
]
