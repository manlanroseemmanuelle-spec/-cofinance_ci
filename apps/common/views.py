from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, generics
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import AuditLog
from .serializers import AuditLogSerializer
from apps.accounts.permissions import IsAdmin


@extend_schema(tags=['Santé'], responses={200: OpenApiResponse(description='API is running')})
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'message': 'Cofinance CI API is running'})


@extend_schema(tags=['Audit'])
class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]
    search_fields = ['action', 'model_name', 'object_repr', 'details', 'user__username']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


@extend_schema(tags=['Recherche'], responses={200: dict})
class GlobalSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response({'query': query, 'results': {}})

        from apps.loans.models import LoanApplication
        from apps.insurance.models import Policy
        from apps.support_chat.models import Conversation

        user = request.user
        loans = LoanApplication.objects.select_related('client__user', 'agent__user')
        policies = Policy.objects.select_related('client__user', 'produit')
        conversations = Conversation.objects.select_related('client', 'agent')

        if user.role == 'CLIENT':
            loans = loans.filter(client=user.client_profile)
            policies = policies.filter(client=user.client_profile)
            conversations = conversations.filter(client=user)
        elif user.role == 'AGENT':
            loans = loans.filter(agent=user.agent_profile)
            conversations = conversations.filter(agent=user)

        loans = loans.filter(motif__icontains=query)[:10]
        policies = policies.filter(produit__nom__icontains=query)[:10]
        conversations = conversations.filter(messages__message__icontains=query).distinct()[:10]

        return Response({
            'query': query,
            'results': {
                'loans': [{'id': loan.id, 'motif': loan.motif, 'statut': loan.statut} for loan in loans],
                'policies': [{'id': policy.id, 'produit': policy.produit.nom, 'statut': policy.statut} for policy in policies],
                'conversations': [{'id': conv.id, 'status': conv.status} for conv in conversations],
            }
        })
