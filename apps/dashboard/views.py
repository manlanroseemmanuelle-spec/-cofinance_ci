from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema
from django.db.models import Sum, Count, Q, Subquery, OuterRef
from django.db.models.fields import IntegerField, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta, date
from apps.loans.models import LoanApplication, AmortizationSchedule
from apps.repayments.models import Repayment
from apps.insurance.models import Policy
from apps.support_chat.models import Conversation
from apps.accounts.models import Agent, Client
from apps.accounts.serializers import UserSerializer
from apps.accounts.permissions import IsAdmin


def _apply_period(qs, field, period):
    if period == '7d':
        return qs.filter(**{f'{field}__gte': timezone.now() - timedelta(days=7)})
    if period == '30d':
        return qs.filter(**{f'{field}__gte': timezone.now() - timedelta(days=30)})
    if period == '90d':
        return qs.filter(**{f'{field}__gte': timezone.now() - timedelta(days=90)})
    return qs

@extend_schema(tags=['Dashboard'], responses={200: dict})
class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        agent_id = request.query_params.get('agent_id')
        region = request.query_params.get('region')
        period = request.query_params.get('period', '30d')

        loan_qs = LoanApplication.objects.all()
        repay_qs = Repayment.objects.all()
        policy_qs = Policy.objects.all()

        if agent_id:
            loan_qs = loan_qs.filter(agent_id=agent_id)
            repay_qs = repay_qs.filter(agent_id=agent_id)
        if region:
            loan_qs = loan_qs.filter(client__user__region=region)
            repay_qs = repay_qs.filter(loan__client__user__region=region)
            policy_qs = policy_qs.filter(client__user__region=region)
        if period != 'all':
            loan_qs = _apply_period(loan_qs, 'date_creation', period)
            repay_qs = _apply_period(repay_qs, 'date_paiement', period)

        total_loans = loan_qs.count()
        approved_loans = loan_qs.filter(statut='APPROUVEE').count()
        rejected_loans = loan_qs.filter(statut='REJETEE').count()
        disbursed_loans = loan_qs.filter(statut='DECAISSEE').count()
        pending_loans = loan_qs.filter(statut__in=['SOUMISE', 'EN_ANALYSE']).count()

        total_amount_loaned = loan_qs.filter(
            statut='DECAISSEE'
        ).aggregate(Sum('montant_demande'))['montant_demande__sum'] or 0

        total_repayments = repay_qs.aggregate(
            total=Sum('montant'),
            total_penalites=Sum('penalite')
        )

        active_policies = policy_qs.filter(statut='ACTIVE').count()
        expired_policies = policy_qs.filter(statut='EXPIREE').count()

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


@extend_schema(tags=['Dashboard'], responses={200: dict})
class CalendarView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        end_date = today + timedelta(days=90)

        if request.user.role == 'ADMIN':
            schedules = AmortizationSchedule.objects.select_related(
                'loan__client__user'
            ).filter(
                date_echeance__gte=today,
                date_echeance__lte=end_date,
            ).order_by('date_echeance')
        elif request.user.role == 'AGENT':
            agent = request.user.agent_profile
            schedules = AmortizationSchedule.objects.select_related(
                'loan__client__user'
            ).filter(
                loan__agent=agent,
                date_echeance__gte=today,
                date_echeance__lte=end_date,
            ).order_by('date_echeance')
        else:
            client = request.user.client_profile
            schedules = AmortizationSchedule.objects.select_related(
                'loan__client__user'
            ).filter(
                loan__client=client,
                date_echeance__gte=today,
                date_echeance__lte=end_date,
            ).order_by('date_echeance')

        events = []
        for s in schedules:
            events.append({
                'id': s.id,
                'title': f"#{s.loan_id} - {s.mensualite} FCFA",
                'date': s.date_echeance.isoformat(),
                'montant': str(s.mensualite),
                'part_capital': str(s.part_capital),
                'part_interet': str(s.part_interet),
                'est_paye': s.est_paye,
                'numero': s.numero_mensualite,
                'client': s.loan.client.user.get_full_name() or s.loan.client.user.username,
                'loan_id': s.loan_id,
            })

        overdue = AmortizationSchedule.objects.filter(
            Q(loan__in=[s.loan_id for s in schedules]) if schedules else Q(),
            est_paye=False,
            date_echeance__lt=today,
        ).count()

        return Response({
            'events': events,
            'overdue': overdue,
            'total': schedules.count(),
            'monthly_total': sum(
                float(s.mensualite) for s in schedules
                if s.date_echeance.month == today.month and s.date_echeance.year == today.year
            ),
        })


@extend_schema(tags=['Dashboard'], responses={200: dict})
class DashboardClientListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role == 'ADMIN':
            clients = Client.objects.select_related('user').all()
        elif request.user.role == 'AGENT':
            agent = request.user.agent_profile
            loan_client_ids = LoanApplication.objects.filter(
                agent=agent
            ).values_list('client_id', flat=True).distinct()
            clients = Client.objects.select_related('user').filter(id__in=loan_client_ids)
        else:
            return Response({'error': 'Acces reserve aux agents et admins'}, status=status.HTTP_403_FORBIDDEN)

        active_loans_sub = LoanApplication.objects.filter(
            client=OuterRef('pk'), statut='DECAISSEE'
        ).values('client').annotate(
            cnt=Count('id')
        ).values('cnt')

        total_due_sub = AmortizationSchedule.objects.filter(
            loan__client=OuterRef('pk'), est_paye=False
        ).values('loan__client').annotate(
            total=Coalesce(Sum('mensualite'), 0)
        ).values('total')

        clients = clients.annotate(
            active_loans=Coalesce(Subquery(active_loans_sub, output_field=IntegerField()), 0),
            total_due_amt=Coalesce(Subquery(total_due_sub, output_field=DecimalField()), 0),
        )

        data = [{
            'id': c.id,
            'username': c.user.username,
            'nom': c.user.get_full_name() or c.user.username,
            'telephone': c.user.telephone,
            'region': c.user.region,
            'profession': c.profession,
            'score_credit': c.score_credit,
            'prets_actifs': c.active_loans,
            'total_du': str(c.total_due_amt),
        } for c in clients]

        return Response(data)


@extend_schema(tags=['Dashboard'], responses={200: list})
class DashboardAgentListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        agents = Agent.objects.select_related('user').all()
        return Response([{
            'id': a.id,
            'nom': a.user.get_full_name() or a.user.username,
            'matricule': a.matricule,
            'region': a.region,
        } for a in agents])


@extend_schema(tags=['Dashboard'], responses={200: list})
class DashboardRegionListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        regions = Agent.objects.values_list('region', flat=True).distinct().order_by('region')
        all_regions = list(set(list(regions) + list(
            Client.objects.values_list('user__region', flat=True).distinct()
        )))
        all_regions = sorted([r for r in all_regions if r])
        return Response(all_regions)
