from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from apps.loans.models import LoanApplication
from apps.repayments.models import Repayment
from apps.insurance.models import Policy
from apps.support_chat.models import Conversation
from apps.accounts.models import Agent
from apps.accounts.permissions import IsAdmin


@extend_schema(tags=['Dashboard'], responses={200: dict})
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


@extend_schema(tags=['Dashboard'], responses={200: dict})
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


@extend_schema(tags=['Dashboard'], responses={200: dict})
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


@extend_schema(tags=['Dashboard'], responses={200: dict})
class ChartsDataView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        today = timezone.now().date()
        twelve_months_ago = today - timedelta(days=365)

        monthly_loans = []
        monthly_repayments = []
        months = []

        for i in range(11, -1, -1):
            first_of_month = today.replace(day=1) - timedelta(days=30 * i)
            month_start = first_of_month.replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1)

            loan_count = LoanApplication.objects.filter(
                date_creation__gte=month_start, date_creation__lt=month_end
            ).count()

            repay_total = Repayment.objects.filter(
                date_paiement__gte=month_start, date_paiement__lt=month_end
            ).aggregate(Sum('montant'))['montant__sum'] or 0

            months.append(month_start.strftime('%b'))
            monthly_loans.append(loan_count)
            monthly_repayments.append(float(repay_total))

        status_dist = []
        for s, label in LoanApplication.Statut.choices:
            status_dist.append({'label': label, 'value': LoanApplication.objects.filter(statut=s).count()})

        top_agents = []
        agents = Agent.objects.annotate(
            loan_count=Count('analysed_loans'),
            repay_count=Count('enregistre_repayments')
        ).order_by('-loan_count')[:5]
        for a in agents:
            top_agents.append({
                'name': a.user.get_full_name() or a.user.username,
                'loans': a.loan_count,
                'repayments': a.repay_count,
            })

        return Response({
            'months': months,
            'credits_par_mois': monthly_loans,
            'remboursements_par_mois': monthly_repayments,
            'repartition_statuts': status_dist,
            'top_agents': top_agents,
        })
