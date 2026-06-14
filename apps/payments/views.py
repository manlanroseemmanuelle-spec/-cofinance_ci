from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from .models import PaymentGatewayConfig, PaymentTransaction, MobileMoneyAccount
from .serializers import (
    PaymentGatewayConfigSerializer, PaymentGatewayConfigCreateSerializer,
    PaymentTransactionSerializer, PaymentTransactionCreateSerializer,
    MobileMoneyAccountSerializer, MobileMoneyAccountCreateSerializer,
    PaymentInitiateSerializer, PaymentCallbackSerializer,
)
from apps.accounts.permissions import IsAdmin, IsClient


@extend_schema(tags=['Paiements'])
class PaymentGatewayConfigListView(generics.ListCreateAPIView):
    queryset = PaymentGatewayConfig.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PaymentGatewayConfigCreateSerializer
        return PaymentGatewayConfigSerializer


@extend_schema(tags=['Paiements'])
class MobileMoneyAccountListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MobileMoneyAccount.objects.none()
        user = self.request.user
        qs = MobileMoneyAccount.objects.select_related('client__user')
        if user.role == 'CLIENT':
            return qs.filter(client=user.client_profile)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MobileMoneyAccountCreateSerializer
        return MobileMoneyAccountSerializer

    def perform_create(self, serializer):
        if self.request.user.role != 'CLIENT':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seuls les clients peuvent ajouter un compte Mobile Money.")
        serializer.save(client=self.request.user.client_profile)


@extend_schema(tags=['Paiements'])
class MobileMoneyAccountRemoveView(generics.DestroyAPIView):
    serializer_class = MobileMoneyAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MobileMoneyAccount.objects.none()
        user = self.request.user
        qs = MobileMoneyAccount.objects.all()
        if user.role == 'CLIENT':
            return qs.filter(client=user.client_profile)
        return qs


@extend_schema(tags=['Paiements'])
class PaymentTransactionListView(generics.ListAPIView):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return PaymentTransaction.objects.none()
        user = self.request.user
        qs = PaymentTransaction.objects.select_related('gateway', 'loan', 'compte')
        if user.role == 'CLIENT':
            qs = qs.filter(
                models.Q(loan__client=user.client_profile) |
                models.Q(compte__client=user.client_profile)
            )
        elif user.role == 'AGENT':
            qs = qs.filter(
                models.Q(loan__agent=user.agent_profile) |
                models.Q(compte__client__agent=user.agent_profile)
            )
        statut = self.request.query_params.get('statut')
        tx_type = self.request.query_params.get('type')
        date_from = self.request.query_params.get('from')
        date_to = self.request.query_params.get('to')
        if statut:
            qs = qs.filter(statut=statut)
        if tx_type:
            qs = qs.filter(type=tx_type)
        if date_from:
            qs = qs.filter(date_creation__gte=date_from)
        if date_to:
            qs = qs.filter(date_creation__lte=date_to)
        return qs


@extend_schema(tags=['Paiements'])
class PaymentInitiateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=PaymentInitiateSerializer, responses=PaymentTransactionSerializer)
    def post(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        loan_id = data.get('loan_id')
        if loan_id:
            from apps.loans.models import LoanApplication
            loan = LoanApplication.objects.filter(id=loan_id).first()
            if not loan:
                return Response({'error': 'Prêt inexistant'}, status=400)
            if request.user.role == 'CLIENT' and loan.client.user_id != request.user.id:
                return Response({'error': 'Ce prêt ne vous appartient pas'}, status=403)
            if request.user.role == 'AGENT' and loan.agent and loan.agent.user_id != request.user.id:
                return Response({'error': 'Ce prêt ne vous est pas assigné'}, status=403)

        import uuid
        reference = uuid.uuid4().hex[:12].upper()
        tx = PaymentTransaction.objects.create(
            gateway_id=data['gateway'],
            telephone=data['telephone'],
            montant=data['montant'],
            type=data['type'],
            reference_interne=reference,
            statut='INITIE',
            loan_id=data.get('loan_id'),
            compte_id=data.get('compte_id'),
        )
        return Response(
            {'reference_interne': reference, 'statut': 'INITIE', 'id': tx.id},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['Paiements'])
class PaymentCallbackView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=PaymentCallbackSerializer, responses=PaymentTransactionSerializer)
    def post(self, request):
        serializer = PaymentCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            tx = PaymentTransaction.objects.get(reference_interne=data['reference_interne'])
        except PaymentTransaction.DoesNotExist:
            return Response({'error': 'Transaction introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        tx.statut = data['statut']
        tx.reference_externe = data.get('reference_externe', '')
        tx.date_execution = timezone.now()
        if data.get('callback_data'):
            tx.callback_data = data['callback_data']
        tx.save()
        return Response(PaymentTransactionSerializer(tx).data)


@extend_schema(tags=['Paiements'])
class PaymentRetryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=PaymentTransactionSerializer)
    def post(self, request, pk):
        try:
            tx = PaymentTransaction.objects.get(pk=pk)
        except PaymentTransaction.DoesNotExist:
            return Response({'error': 'Transaction introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        if tx.statut != 'ECHEC':
            return Response({'error': 'Seules les transactions échouées peuvent être relancées.'}, status=status.HTTP_400_BAD_REQUEST)
        import uuid
        tx.reference_interne = uuid.uuid4().hex[:12].upper()
        tx.statut = 'INITIE'
        tx.reference_externe = ''
        tx.callback_data = None
        tx.date_execution = None
        tx.save()
        return Response({'reference_interne': tx.reference_interne, 'statut': tx.statut})


@extend_schema(tags=['Paiements'])
class MyPaymentAccountsView(generics.ListAPIView):
    serializer_class = MobileMoneyAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return MobileMoneyAccount.objects.none()
        user = self.request.user
        if user.role != 'CLIENT':
            return MobileMoneyAccount.objects.none()
        return MobileMoneyAccount.objects.filter(client=user.client_profile)
