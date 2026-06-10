from django.urls import path
from . import views

urlpatterns = [
    path('', views.SolidarityGroupListCreateView.as_view(), name='group-list'),
    path('mine/', views.MyGroupsView.as_view(), name='my-groups'),
    path('agent/', views.AgentGroupsView.as_view(), name='agent-groups'),
    path('<int:pk>/', views.SolidarityGroupDetailView.as_view(), name='group-detail'),
    path('<int:group_id>/members/', views.GroupMemberListCreateView.as_view(), name='group-members'),
    path('<int:group_id>/members/<int:pk>/', views.GroupMemberRemoveView.as_view(), name='group-member-remove'),
    path('<int:group_id>/loans/', views.GroupeLoanListView.as_view(), name='group-loans'),
]
