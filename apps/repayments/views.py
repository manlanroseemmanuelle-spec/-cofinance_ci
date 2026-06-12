import uuid
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Repayment
from .serializers import RepaymentSerializer, RepaymentCreateSerializer
from apps.accounts.permissions import IsOwnerAdminOrAssignedAgent
from apps.notifications.models import Notification


@extend_schema(tags=['Remboursements'])
class RepaymentListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Repayment.objects.none()
        user = self.request.user
        queryset = Repayment.objects.select_related('loan__client__user', 'loan__agent__user', 'agent__user')
        if user.role == 'CLIENT':
            return queryset.filter(loan__client=user.client_profile)
        if user.role == 'AGENT':
            return queryset.filter(loan__agent=user.agent_profile)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RepaymentCreateSerializer
        return RepaymentSerializer

    def perform_create(self, serializer):
        loan = serializer.validated_data['loan']
        user = self.request.user
        if user.role == 'CLIENT' and loan.client.user_id != user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Vous ne pouvez payer que vos propres prêts.")
        if user.role == 'AGENT' and loan.agent and loan.agent.user_id != user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Ce prêt n'est pas assigné à cet agent.")
        repayment = serializer.save(
            reference=f"REP-{uuid.uuid4().hex[:8].upper()}",
            agent=self.request.user.agent_profile if hasattr(self.request.user, 'agent_profile') else None
        )
        penalite = repayment.calculer_penalite()
        repayment.penalite = penalite
        repayment.save()

        # Notify client
        Notification.objects.create(
            titre=f"Remboursement #{repayment.id} - {repayment.montant} FCFA",
            message=f"Remboursement de {repayment.montant} FCFA enregistre pour le pret #{repayment.loan_id}.",
            type=Notification.Type.REMBOURSEMENT,
            user=repayment.loan.client.user,
        )
        # Notify agent who recorded it
        if repayment.agent:
            Notification.objects.create(
                titre=f"Remboursement #{repayment.id} enregistre",
                message=f"Remboursement de {repayment.montant} FCFA enregistre pour le pret #{repayment.loan_id}.",
                type=Notification.Type.REMBOURSEMENT,
                user=repayment.agent.user,
            )

        if repayment.amortization:
            repayment.amortization.est_paye = True
            repayment.amortization.save()

        # Accounting entry for repayment
        try:
            from apps.accounting.models import Account, JournalEntry, JournalEntryLine
            from django.utils import timezone
            from decimal import Decimal
            compte_caisse, _ = Account.objects.get_or_create(
                code='101', defaults={'nom': 'Caisse', 'type': 'ACTIF'}
            )
            compte_client, _ = Account.objects.get_or_create(
                code='411', defaults={'nom': 'Clients', 'type': 'ACTIF'}
            )
            compte_interets, _ = Account.objects.get_or_create(
                code='701', defaults={'nom': 'Revenus', 'type': 'PRODUIT'}
            )
            montant = repayment.montant
            penalite = repayment.penalite or Decimal('0')
            principal = montant - penalite
            ref = f"REM-{repayment.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            entry = JournalEntry.objects.create(
                journal='CAISSE',
                reference=ref,
                date_ecriture=timezone.now().date(),
                libelle=f"Remboursement prêt #{repayment.loan_id} - {repayment.loan.client.user.get_full_name()}",
                loan=repayment.loan,
                client=repayment.loan.client,
                agent=repayment.agent,
            )
            JournalEntryLine.objects.create(entry=entry, account=compte_caisse, sens='DEBIT', montant=montant, libelle='Encaissement')
            JournalEntryLine.objects.create(entry=entry, account=compte_client, sens='CREDIT', montant=principal, libelle='Remboursement principal')
            if penalite > 0:
                JournalEntryLine.objects.create(entry=entry, account=compte_interets, sens='CREDIT', montant=penalite, libelle='Pénalité de retard')
        except Exception:
            pass


@extend_schema(tags=['Remboursements'])
class RepaymentDetailView(generics.RetrieveAPIView):
    serializer_class = RepaymentSerializer
    permission_classes = [IsOwnerAdminOrAssignedAgent]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Repayment.objects.none()
        user = self.request.user
        queryset = Repayment.objects.select_related('loan__client__user', 'loan__agent__user', 'agent__user')
        if user.role == 'CLIENT':
            return queryset.filter(loan__client=user.client_profile)
        if user.role == 'AGENT':
            return queryset.filter(loan__agent=user.agent_profile)
        return queryset


@extend_schema(tags=['Remboursements'])
class LoanRepaymentsView(generics.ListAPIView):
    serializer_class = RepaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Repayment.objects.none()
        queryset = Repayment.objects.select_related('loan__client__user', 'loan__agent__user').filter(loan_id=self.kwargs['loan_id'])
        user = self.request.user
        if user.role == 'CLIENT':
            return queryset.filter(loan__client=user.client_profile)
        if user.role == 'AGENT':
            return queryset.filter(loan__agent=user.agent_profile)
        return queryset
