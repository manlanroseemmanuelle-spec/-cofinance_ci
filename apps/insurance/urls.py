from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.InsuranceProductListView.as_view(), name='insurance-products'),
    path('policies/', views.PolicyListCreateView.as_view(), name='policy-list'),
    path('policies/mine/', views.MyPoliciesView.as_view(), name='my-policies'),
    path('policies/<int:pk>/', views.PolicyDetailView.as_view(), name='policy-detail'),
]
