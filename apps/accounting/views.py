from datetime import date
from decimal import Decimal

from django.db.models import Sum, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Account, JournalEntry, JournalEntryLine
from .serializers import (
    AccountSerializer, AccountCreateSerializer,
    JournalEntrySerializer, JournalEntryCreateSerializer,
    JournalEntryValidationSerializer,
)
from apps.accounts.permissions import IsAdmin, IsAdminOrComptable


@extend_schema(tags=['Comptabilité'])
class AccountListCreateView(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrComptable]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AccountCreateSerializer
        return AccountSerializer


@extend_schema(tags=['Comptabilité'])
class AccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrComptable]


@extend_schema(tags=['Comptabilité'])
class JournalEntryListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrComptable]

    def get_queryset(self):
        qs = JournalEntry.objects.prefetch_related('lines__account')
        journal = self.request.query_params.get('journal')
        if journal:
            qs = qs.filter(journal=journal.upper())
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JournalEntryCreateSerializer
        return JournalEntrySerializer


@extend_schema(tags=['Comptabilité'])
class JournalEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JournalEntry.objects.prefetch_related('lines__account')
    permission_classes = [permissions.IsAuthenticated, IsAdminOrComptable]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return JournalEntryCreateSerializer
        return JournalEntrySerializer


@extend_schema(tags=['Comptabilité'])
class JournalEntryValidateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrComptable]

    @extend_schema(request=JournalEntryValidationSerializer, responses=JournalEntrySerializer)
    def post(self, request, pk):
        try:
            entry = JournalEntry.objects.get(pk=pk)
        except JournalEntry.DoesNotExist:
            return Response({'detail': 'Écriture introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = JournalEntryValidationSerializer(data=request.data, context={'entry': entry})
        serializer.is_valid(raise_exception=True)
        entry.valider(request.user)
        return Response(JournalEntrySerializer(entry).data, status=status.HTTP_200_OK)


@extend_schema(tags=['Comptabilité'])
class GrandLivreView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        qs = JournalEntryLine.objects.select_related('entry', 'account').filter(
            entry__est_validee=True
        )
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        if date_from:
            qs = qs.filter(entry__date_ecriture__gte=date_from)
        if date_to:
            qs = qs.filter(entry__date_ecriture__lte=date_to)
        qs = qs.order_by('entry__date_ecriture', 'entry_id')

        data = []
        for line in qs:
            data.append({
                'date': line.entry.date_ecriture,
                'reference': line.entry.reference,
                'journal': line.entry.journal,
                'libelle_ecriture': line.entry.libelle,
                'compte_code': line.account.code,
                'compte_nom': line.account.nom,
                'sens': line.sens,
                'montant': line.montant,
                'libelle_ligne': line.libelle,
            })
        return Response(data)


@extend_schema(tags=['Comptabilité'])
class BalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        balance_date = request.query_params.get('date', date.today().isoformat())
        lines = JournalEntryLine.objects.filter(
            entry__est_validee=True,
            entry__date_ecriture__lte=balance_date,
        )

        totals = (
            lines.values('account_id', 'account__code', 'account__nom')
            .annotate(
                total_debit=Sum('montant', filter=Q(sens='DEBIT')),
                total_credit=Sum('montant', filter=Q(sens='CREDIT')),
            )
            .order_by('account__code')
        )

        data = []
        for t in totals:
            debit = t['total_debit'] or Decimal('0.00')
            credit = t['total_credit'] or Decimal('0.00')
            solde = debit - credit
            data.append({
                'compte_id': t['account_id'],
                'compte_code': t['account__code'],
                'compte_nom': t['account__nom'],
                'total_debit': debit,
                'total_credit': credit,
                'solde': solde,
            })
        return Response(data)


@extend_schema(tags=['Comptabilité'])
class CompteResultatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        period_date = request.query_params.get('date', date.today().isoformat())

        lines = JournalEntryLine.objects.filter(
            entry__est_validee=True,
            entry__date_ecriture__lte=period_date,
        )

        totals = (
            lines.values('account__type')
            .annotate(total=Sum('montant'))
        )

        produits = Decimal('0.00')
        charges = Decimal('0.00')
        for t in totals:
            if t['account__type'] == 'PRODUIT':
                produits += t['total'] or Decimal('0.00')
            elif t['account__type'] == 'CHARGE':
                charges += t['total'] or Decimal('0.00')

        resultat = produits - charges

        return Response({
            'date': period_date,
            'produits': produits,
            'charges': charges,
            'resultat_net': resultat,
        })


@extend_schema(tags=['Comptabilité'])
class BilanView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        bilan_date = request.query_params.get('date', date.today().isoformat())

        lines = JournalEntryLine.objects.filter(
            entry__est_validee=True,
            entry__date_ecriture__lte=bilan_date,
        )

        totals = (
            lines.values('account_id', 'account__code', 'account__nom', 'account__type')
            .annotate(
                total_debit=Sum('montant', filter=Q(sens='DEBIT')),
                total_credit=Sum('montant', filter=Q(sens='CREDIT')),
            )
            .order_by('account__code')
        )

        actif = []
        passif = []
        for t in totals:
            debit = t['total_debit'] or Decimal('0.00')
            credit = t['total_credit'] or Decimal('0.00')
            solde = debit - credit
            entry = {
                'compte_code': t['account__code'],
                'compte_nom': t['account__nom'],
                'solde': abs(solde),
            }
            if t['account__type'] == 'ACTIF':
                actif.append(entry)
            elif t['account__type'] == 'PASSIF':
                passif.append(entry)

        return Response({
            'date': bilan_date,
            'actif': {
                'total': sum(a['solde'] for a in actif),
                'comptes': actif,
            },
            'passif': {
                'total': sum(p['solde'] for p in passif),
                'comptes': passif,
            },
        })
