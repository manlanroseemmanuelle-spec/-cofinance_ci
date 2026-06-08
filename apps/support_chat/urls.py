from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:pk>/close/', views.ConversationCloseView.as_view(), name='conversation-close'),
    path('conversations/<int:pk>/assign/', views.AssignAgentView.as_view(), name='conversation-assign'),
    path('conversations/<int:conversation_id>/messages/', views.MessageListView.as_view(), name='message-list'),
    path('conversations/<int:conversation_id>/send/', views.MessageCreateView.as_view(), name='message-send'),
]
