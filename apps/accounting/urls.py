from django.urls import path
from . import views

urlpatterns = [
    path('accounts/', views.AccountListCreateView.as_view(), name='account-list'),
    path('accounts/<int:pk>/', views.AccountDetailView.as_view(), name='account-detail'),
    path('journals/', views.JournalEntryListCreateView.as_view(), name='journal-list'),
    path('journals/<int:pk>/', views.JournalEntryDetailView.as_view(), name='journal-detail'),
    path('journals/<int:pk>/validate/', views.JournalEntryValidateView.as_view(), name='journal-validate'),
    path('reports/grand-livre/', views.GrandLivreView.as_view(), name='grand-livre'),
    path('reports/balance/', views.BalanceView.as_view(), name='balance'),
    path('reports/compte-resultat/', views.CompteResultatView.as_view(), name='compte-resultat'),
    path('reports/bilan/', views.BilanView.as_view(), name='bilan'),
]
