from django.urls import path
from . import views

urlpatterns = [
    path('gateways/', views.PaymentGatewayConfigListView.as_view(), name='gateway-list'),
    path('accounts/', views.MobileMoneyAccountListCreateView.as_view(), name='mm-account-list'),
    path('accounts/mine/', views.MyPaymentAccountsView.as_view(), name='my-mm-accounts'),
    path('accounts/<int:pk>/', views.MobileMoneyAccountRemoveView.as_view(), name='mm-account-remove'),
    path('transactions/', views.PaymentTransactionListView.as_view(), name='payment-list'),
    path('initiate/', views.PaymentInitiateView.as_view(), name='payment-initiate'),
    path('callback/', views.PaymentCallbackView.as_view(), name='payment-callback'),
    path('<int:pk>/retry/', views.PaymentRetryView.as_view(), name='payment-retry'),
]
