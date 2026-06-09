from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoanListCreateView.as_view(), name='loan-list'),
    path('mine/', views.MyLoansView.as_view(), name='my-loans'),
    path('export/csv/', views.LoanExportCsvView.as_view(), name='loan-export-csv'),
    path('<int:pk>/', views.LoanDetailView.as_view(), name='loan-detail'),
    path('<int:pk>/status/', views.LoanStatusUpdateView.as_view(), name='loan-status'),
    path('<int:loan_id>/schedule/', views.AmortizationScheduleListView.as_view(), name='loan-schedule'),
    path('<int:loan_id>/documents/', views.DocumentListCreateView.as_view(), name='loan-documents'),
    path('<int:loan_id>/history/', views.LoanStatusHistoryListView.as_view(), name='loan-history'),
]
