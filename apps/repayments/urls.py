from django.urls import path
from . import views

urlpatterns = [
    path('', views.RepaymentListCreateView.as_view(), name='repayment-list'),
    path('<int:pk>/', views.RepaymentDetailView.as_view(), name='repayment-detail'),
    path('loan/<int:loan_id>/', views.LoanRepaymentsView.as_view(), name='loan-repayments'),
]
