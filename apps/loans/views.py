from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema
from .models import LoanApplication, AmortizationSchedule, Document
from .serializers import (
    LoanApplicationSerializer, LoanCreateSerializer,
    LoanStatusUpdateSerializer, AmortizationScheduleSerializer,
    DocumentSerializer, DocumentUploadSerializer
)
from .services import calculer_score_eligibilite, generer_echeancier
from apps.accounts.permissions import IsAdmin, IsAdminOrAgent, IsClient


@extend_schema(tags=['Crédits'])
class LoanListCreateView(generics.ListCreateAPIView):
    queryset = LoanApplication.objects.all()

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
    queryset = LoanApplication.objects.all()

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
        new_status = serializer.validated_data['statut']
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


@extend_schema(tags=['Échéancier'])
class AmortizationScheduleListView(generics.ListAPIView):
    serializer_class = AmortizationScheduleSerializer

    def get_queryset(self):
        return AmortizationSchedule.objects.filter(loan_id=self.kwargs['loan_id'])


@extend_schema(tags=['Documents'])
class DocumentListCreateView(generics.ListCreateAPIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentUploadSerializer
        return DocumentSerializer

    def get_queryset(self):
        return Document.objects.filter(loan_id=self.kwargs['loan_id'])

    def perform_create(self, serializer):
        from django.shortcuts import get_object_or_404
        loan = get_object_or_404(LoanApplication, id=self.kwargs['loan_id'])
        serializer.save(loan=loan)


@extend_schema(tags=['Crédits'])
class MyLoansView(generics.ListAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CLIENT':
            return LoanApplication.objects.filter(client=user.client_profile)
        if user.role == 'AGENT':
            return LoanApplication.objects.filter(agent=user.agent_profile)
        return LoanApplication.objects.all()
