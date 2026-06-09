import uuid
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Repayment
from .serializers import RepaymentSerializer, RepaymentCreateSerializer
from apps.loans.models import AmortizationSchedule
from apps.accounts.permissions import IsAdminOrAgent


@extend_schema(tags=['Remboursements'])
class RepaymentListCreateView(generics.ListCreateAPIView):
    queryset = Repayment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RepaymentCreateSerializer
        return RepaymentSerializer

    def perform_create(self, serializer):
        repayment = serializer.save(
            reference=f"REP-{uuid.uuid4().hex[:8].upper()}",
            agent=self.request.user.agent_profile if hasattr(self.request.user, 'agent_profile') else None
        )
        penalite = repayment.calculer_penalite()
        repayment.penalite = penalite
        repayment.save()

        if repayment.amortization:
            repayment.amortization.est_paye = True
            repayment.amortization.save()


@extend_schema(tags=['Remboursements'])
class RepaymentDetailView(generics.RetrieveAPIView):
    queryset = Repayment.objects.all()
    serializer_class = RepaymentSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=['Remboursements'])
class LoanRepaymentsView(generics.ListAPIView):
    serializer_class = RepaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Repayment.objects.none()
        return Repayment.objects.filter(loan_id=self.kwargs['loan_id'])
