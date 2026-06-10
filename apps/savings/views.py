from decimal import Decimal

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from drf_spectacular.utils import extend_schema

from .models import SavingsProduct, SavingsAccount, SavingsTransaction
from .serializers import (
    SavingsProductSerializer, SavingsAccountSerializer,
    SavingsAccountCreateSerializer, SavingsTransactionSerializer,
    SavingsTransactionCreateSerializer,
)
from apps.accounts.permissions import IsAdmin, IsAdminOrAgent, IsClient, IsOwnerAdminOrAssignedAgent


@extend_schema(tags=['Épargne'])
class SavingsProductListView(generics.ListAPIView):
    serializer_class = SavingsProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SavingsProduct.objects.none()
        return SavingsProduct.objects.filter(est_actif=True)


@extend_schema(tags=['Épargne'])
class SavingsAccountListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SavingsAccountCreateSerializer
        return SavingsAccountSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SavingsAccount.objects.none()
        user = self.request.user
        qs = SavingsAccount.objects.select_related('client__user', 'produit')
        if user.role == 'CLIENT':
            return qs.filter(client=user.client_profile)
        if user.role == 'AGENT':
            return qs.all()
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'CLIENT':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seuls les clients peuvent ouvrir un compte d'épargne.")
        serializer.save(client=self.request.user.client_profile)


@extend_schema(tags=['Épargne'])
class SavingsAccountDetailView(generics.RetrieveAPIView):
    serializer_class = SavingsAccountSerializer
    permission_classes = [IsOwnerAdminOrAssignedAgent]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SavingsAccount.objects.none()
        return SavingsAccount.objects.select_related('client__user', 'produit')


@extend_schema(tags=['Épargne'])
class SavingsTransactionListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SavingsTransactionCreateSerializer
        return SavingsTransactionSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SavingsTransaction.objects.none()
        qs = SavingsTransaction.objects.select_related('compte__client__user', 'agent__user')
        compte = self.request.query_params.get('compte')
        if compte:
            qs = qs.filter(compte_id=compte)
        user = self.request.user
        if user.role == 'CLIENT':
            qs = qs.filter(compte__client=user.client_profile)
        elif user.role == 'AGENT':
            qs = qs.all()
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ('ADMIN', 'AGENT'):
            serializer.save()
        else:
            agent_profile = getattr(user, 'agent_profile', None)
            serializer.save(agent=agent_profile)


@extend_schema(tags=['Épargne'])
class MySavingsView(generics.ListAPIView):
    serializer_class = SavingsAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SavingsAccount.objects.none()
        user = self.request.user
        if user.role == 'CLIENT':
            return SavingsAccount.objects.select_related('client__user', 'produit').filter(
                client=user.client_profile
            )
        return SavingsAccount.objects.none()


@extend_schema(tags=['Épargne'])
class SavingsSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'CLIENT':
            return Response(
                {"detail": "Réservé aux clients."},
                status=status.HTTP_403_FORBIDDEN,
            )
        client = user.client_profile
        comptes = SavingsAccount.objects.filter(client=client)
        total_epargne = comptes.aggregate(total=Sum('solde'))['total'] or Decimal('0.00')
        nombre_comptes = comptes.count()
        interets_cumules = SavingsTransaction.objects.filter(
            compte__client=client, type='INTERET_CREDITEUR'
        ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')

        return Response({
            "total_epargne": total_epargne,
            "nombre_comptes": nombre_comptes,
            "interets_cumules": interets_cumules,
        })
