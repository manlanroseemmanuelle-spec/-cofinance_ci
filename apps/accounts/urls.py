from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='auth-register'),
    path('login/', views.LoginView.as_view(), name='auth-login'),
    path('refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('profile/', views.ProfileView.as_view(), name='auth-profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='auth-change-password'),
    path('clients/', views.ClientListView.as_view(), name='client-list'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client-detail'),
    path('agents/', views.AgentListView.as_view(), name='agent-list'),
    path('agents/<int:pk>/', views.AgentDetailView.as_view(), name='agent-detail'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
]
