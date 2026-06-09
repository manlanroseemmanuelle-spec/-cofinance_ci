from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from .models import LoanApplication, AmortizationSchedule, Document, LoanStatusHistory
from .serializers import (
    LoanApplicationSerializer, LoanCreateSerializer,
    LoanStatusUpdateSerializer, AmortizationScheduleSerializer,
    DocumentSerializer, DocumentUploadSerializer, LoanStatusHistorySerializer
)
from .services import calculer_score_eligibilite, generer_echeancier
from apps.accounts.permissions import IsAdminOrAgent, IsOwnerAdminOrAssignedAgent


@extend_schema(tags=['Crédits'])
class LoanListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LoanApplication.objects.none()
        user = self.request.user
        queryset = LoanApplication.objects.select_related('client__user', 'agent__user')
        if user.role == 'CLIENT':
            return queryset.filter(client=user.client_profile)
        if user.role == 'AGENT':
            return queryset.filter(agent=user.agent_profile)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LoanCreateSerializer
        return LoanApplicationSerializer

    def perform_create(self, serializer):
        if self.request.user.role != 'CLIENT':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seuls les clients peuvent soumettre une demande de credit.")
        client = self.request.user.client_profile
        loan = serializer.save(client=client, revenu_mensuel=client.revenu_mensuel)
        score = calculer_score_eligibilite(client)
        loan.score_eligibilite = score
        loan.save()


@extend_schema(tags=['Crédits'])
class LoanDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerAdminOrAssignedAgent]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LoanApplication.objects.none()
        user = self.request.user
        queryset = LoanApplication.objects.select_related('client__user', 'agent__user')
        if user.role == 'CLIENT':
            return queryset.filter(client=user.client_profile)
        if user.role == 'AGENT':
            return queryset.filter(agent=user.agent_profile)
        return queryset

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return LoanCreateSerializer
        return LoanApplicationSerializer


@extend_schema(tags=['Crédits'])
class LoanStatusUpdateView(generics.UpdateAPIView):
    queryset = LoanApplication.objects.all()
    serializer_class = LoanStatusUpdateSerializer
    permission_classes = [IsAdminOrAgent]

    def perform_update(self, serializer):
        loan = self.get_object()
        old_status = loan.statut
        new_status = serializer.validated_data['statut']
        allowed_transitions = {
            LoanApplication.Statut.SOUMISE: {LoanApplication.Statut.EN_ANALYSE, LoanApplication.Statut.REJETEE},
            LoanApplication.Statut.EN_ANALYSE: {LoanApplication.Statut.APPROUVEE, LoanApplication.Statut.REJETEE},
            LoanApplication.Statut.APPROUVEE: {LoanApplication.Statut.DECAISSEE},
            LoanApplication.Statut.REJETEE: set(),
            LoanApplication.Statut.DECAISSEE: set(),
        }
        if new_status != old_status and new_status not in allowed_transitions.get(old_status, set()):
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'statut': f'Transition interdite: {old_status} -> {new_status}'})
        loan.statut = new_status

        if 'agent' in serializer.validated_data:
            from apps.accounts.models import Agent
            from django.shortcuts import get_object_or_404
            loan.agent = get_object_or_404(Agent, id=serializer.validated_data['agent'])

        if new_status == LoanApplication.Statut.APPROUVEE:
            generer_echeancier(loan)

        if new_status == LoanApplication.Statut.EN_ANALYSE and not loan.agent:
            if self.request.user.role == 'AGENT':
                loan.agent = self.request.user.agent_profile

        loan.save()

        from .models import LoanStatusHistory
        LoanStatusHistory.objects.create(
            loan=loan,
            ancien_statut=old_status or '',
            nouveau_statut=new_status,
            changed_by=self.request.user,
            commentaire=serializer.validated_data.get('commentaire', ''),
        )

        from apps.common.signals import log_action
        from apps.common.models import AuditLog
        log_action(
            AuditLog.Action.STATUS_CHANGE, 'LoanApplication', loan.id,
            f"Prêt #{loan.id}: {old_status} -> {new_status}",
            f"Ancien: {old_status}, Nouveau: {new_status}, Agent: {loan.agent}"
        )


@extend_schema(tags=['Échéancier'])
class AmortizationScheduleListView(generics.ListAPIView):
    serializer_class = AmortizationScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return AmortizationSchedule.objects.none()
        queryset = AmortizationSchedule.objects.select_related('loan__client__user', 'loan__agent__user').filter(loan_id=self.kwargs['loan_id'])
        user = self.request.user
        if user.role == 'CLIENT':
            return queryset.filter(loan__client=user.client_profile)
        if user.role == 'AGENT':
            return queryset.filter(loan__agent=user.agent_profile)
        return queryset


@extend_schema(tags=['Documents'])
class DocumentListCreateView(generics.ListCreateAPIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentUploadSerializer
        return DocumentSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Document.objects.none()
        queryset = Document.objects.select_related('loan__client__user', 'loan__agent__user').filter(loan_id=self.kwargs['loan_id'])
        user = self.request.user
        if user.role == 'CLIENT':
            return queryset.filter(loan__client=user.client_profile)
        if user.role == 'AGENT':
            return queryset.filter(loan__agent=user.agent_profile)
        return queryset

    def perform_create(self, serializer):
        from django.shortcuts import get_object_or_404
        user = self.request.user
        loans = LoanApplication.objects.all()
        if user.role == 'CLIENT':
            loans = loans.filter(client=user.client_profile)
        elif user.role == 'AGENT':
            loans = loans.filter(agent=user.agent_profile)
        loan = get_object_or_404(loans, id=self.kwargs['loan_id'])
        serializer.save(loan=loan)


@extend_schema(tags=['Crédits'])
class MyLoansView(generics.ListAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LoanApplication.objects.none()
        user = self.request.user
        if user.role == 'CLIENT':
            return LoanApplication.objects.filter(client=user.client_profile)
        if user.role == 'AGENT':
            return LoanApplication.objects.filter(agent=user.agent_profile)
        return LoanApplication.objects.all()


@extend_schema(tags=['Crédits'])
class LoanStatusHistoryListView(generics.ListAPIView):
    serializer_class = LoanStatusHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LoanStatusHistory.objects.none()
        queryset = LoanStatusHistory.objects.select_related('loan__client__user', 'loan__agent__user').filter(loan_id=self.kwargs['loan_id'])
        user = self.request.user
        if user.role == 'CLIENT':
            return queryset.filter(loan__client=user.client_profile)
        if user.role == 'AGENT':
            return queryset.filter(loan__agent=user.agent_profile)
        return queryset


@extend_schema(tags=['Exports'], responses={200: bytes})
class LoanExportCsvView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = LoanApplication.objects.select_related('client__user', 'agent__user')
        if user.role == 'CLIENT':
            queryset = queryset.filter(client=user.client_profile)
        elif user.role == 'AGENT':
            queryset = queryset.filter(agent=user.agent_profile)

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=\"credits.csv\"'
        response.write('id,client,montant,duree_mois,statut,score,date_creation\\n')
        for loan in queryset:
            client_name = (loan.client.user.get_full_name() or loan.client.user.username).replace(',', ' ')
            response.write(
                f'{loan.id},{client_name},{loan.montant_demande},{loan.duree_mois},'
                f'{loan.statut},{loan.score_eligibilite},{loan.date_creation.isoformat()}\\n'
            )
        return response
