from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema
from django.db.models import Sum, Count
from django.utils import timezone
from apps.loans.models import LoanApplication
from apps.repayments.models import Repayment
from apps.insurance.models import Policy
from apps.support_chat.models import Conversation
from apps.accounts.permissions import IsAdmin


@extend_schema(tags=['Dashboard'])
class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        total_loans = LoanApplication.objects.count()
        approved_loans = LoanApplication.objects.filter(statut='APPROUVEE').count()
        rejected_loans = LoanApplication.objects.filter(statut='REJETEE').count()
        disbursed_loans = LoanApplication.objects.filter(statut='DECAISSEE').count()
        pending_loans = LoanApplication.objects.filter(statut__in=['SOUMISE', 'EN_ANALYSE']).count()

        total_amount_loaned = LoanApplication.objects.filter(
            statut='DECAISSEE'
        ).aggregate(Sum('montant_demande'))['montant_demande__sum'] or 0

        total_repayments = Repayment.objects.aggregate(
            total=Sum('montant'),
            total_penalites=Sum('penalite')
        )

        active_policies = Policy.objects.filter(statut='ACTIVE').count()
        expired_policies = Policy.objects.filter(statut='EXPIREE').count()

        total_conversations = Conversation.objects.count()
        open_conversations = Conversation.objects.filter(status='OUVERTE').count()
        closed_conversations = Conversation.objects.filter(status='FERMEE').count()

        return Response({
            'credits': {
                'total': total_loans,
                'approuvees': approved_loans,
                'rejetees': rejected_loans,
                'decaisses': disbursed_loans,
                'en_attente': pending_loans,
            },
            'financier': {
                'montant_prete': total_amount_loaned,
                'montant_rembourse': total_repayments['total'] or 0,
                'penalites': total_repayments['total_penalites'] or 0,
            },
            'assurance': {
                'souscriptions_actives': active_policies,
                'expirees': expired_policies,
            },
            'support': {
                'total_conversations': total_conversations,
                'ouvertes': open_conversations,
                'fermees': closed_conversations,
            },
        })


@extend_schema(tags=['Dashboard'])
class AgentDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'AGENT':
            return Response({'error': 'Acces reserve aux agents'}, status=status.HTTP_403_FORBIDDEN)
        agent = request.user.agent_profile

        my_loans = LoanApplication.objects.filter(agent=agent)
        total_loans = my_loans.count()
        pending = my_loans.filter(statut__in=['SOUMISE', 'EN_ANALYSE']).count()
        approved = my_loans.filter(statut='APPROUVEE').count()

        my_repayments = Repayment.objects.filter(agent=agent)
        total_collected = my_repayments.aggregate(Sum('montant'))['montant__sum'] or 0

        my_conversations = Conversation.objects.filter(agent=request.user)
        open_chats = my_conversations.filter(status='OUVERTE').count()

        return Response({
            'credits': {
                'total': total_loans,
                'en_attente': pending,
                'approuvees': approved,
            },
            'collecte': {
                'total_rembourse': total_collected,
                'nombre_transactions': my_repayments.count(),
            },
            'support': {
                'conversations_ouvertes': open_chats,
                'total_conversations': my_conversations.count(),
            },
        })


@extend_schema(tags=['Dashboard'])
class ClientDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'CLIENT':
            return Response({'error': 'Acces reserve aux clients'}, status=status.HTTP_403_FORBIDDEN)
        client = request.user.client_profile

        my_loans = LoanApplication.objects.filter(client=client)
        total_loans = my_loans.count()
        active_loans = my_loans.filter(statut='DECAISSEE').count()
        pending = my_loans.filter(statut__in=['SOUMISE', 'EN_ANALYSE']).count()

        total_borrowed = my_loans.filter(statut='DECAISSEE').aggregate(
            Sum('montant_demande')
        )['montant_demande__sum'] or 0

        my_repayments = Repayment.objects.filter(loan__client=client)
        total_repaid = my_repayments.aggregate(Sum('montant'))['montant__sum'] or 0

        my_policies = Policy.objects.filter(client=client)
        active_policies = my_policies.filter(statut='ACTIVE').count()

        unread_notifications = request.user.notifications.filter(lu=False).count()

        return Response({
            'credits': {
                'total': total_loans,
                'actifs': active_loans,
                'en_attente': pending,
                'total_emprunte': total_borrowed,
                'total_rembourse': total_repaid,
            },
            'assurance': {
                'polices_actives': active_policies,
                'total': my_policies.count(),
            },
            'notifications_non_lues': unread_notifications,
            'score_credit': client.score_credit,
        })
