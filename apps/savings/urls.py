from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.SavingsProductListView.as_view(), name='savings-products'),
    path('comptes/', views.SavingsAccountListCreateView.as_view(), name='savings-accounts'),
    path('comptes/mine/', views.MySavingsView.as_view(), name='my-savings'),
    path('comptes/<int:pk>/', views.SavingsAccountDetailView.as_view(), name='savings-account-detail'),
    path('transactions/', views.SavingsTransactionListCreateView.as_view(), name='savings-transactions'),
    path('resume/', views.SavingsSummaryView.as_view(), name='savings-summary'),
]
