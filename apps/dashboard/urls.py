from django.urls import path
from . import views

urlpatterns = [
    path('admin/', views.AdminDashboardView.as_view(), name='dashboard-admin'),
    path('agent/', views.AgentDashboardView.as_view(), name='dashboard-agent'),
    path('client/', views.ClientDashboardView.as_view(), name='dashboard-client'),
    path('charts/', views.ChartsDataView.as_view(), name='dashboard-charts'),
    path('calendar/', views.CalendarView.as_view(), name='dashboard-calendar'),
    path('clients/', views.DashboardClientListView.as_view(), name='dashboard-clients'),
    path('agents/', views.DashboardAgentListView.as_view(), name='dashboard-agents'),
    path('regions/', views.DashboardRegionListView.as_view(), name='dashboard-regions'),
]
