from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.db.models import Count, Q

from .models import RegulatoryReport, PrudentialRatio, LoanClassification, DeclarationSuspicion
from .serializers import (
    RegulatoryReportSerializer,
    RegulatoryReportCreateSerializer,
    PrudentialRatioSerializer,
    PrudentialRatioListSerializer,
    LoanClassificationSerializer,
    DeclarationSuspicionSerializer,
    DeclarationSuspicionCreateSerializer,
)
from apps.accounts.permissions import IsAdmin, IsAdminOrAgent


@extend_schema(tags=['Conformité'])
class RegulatoryReportListCreateView(generics.ListCreateAPIView):
    queryset = RegulatoryReport.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RegulatoryReportCreateSerializer
        return RegulatoryReportSerializer


@extend_schema(tags=['Conformité'])
class RegulatoryReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RegulatoryReport.objects.all()
    serializer_class = RegulatoryReportSerializer
    permission_classes = [IsAdmin]


@extend_schema(tags=['Conformité'])
class RegulatoryReportFinalizeView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            report = RegulatoryReport.objects.get(pk=pk)
        except RegulatoryReport.DoesNotExist:
            return Response({'error': 'Rapport introuvable'}, status=status.HTTP_404_NOT_FOUND)

        if report.statut != RegulatoryReport.StatutChoices.BROUILLON:
            return Response(
                {'error': 'Seuls les rapports en brouillon peuvent être finalisés'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.statut = RegulatoryReport.StatutChoices.FINALISE
        report.save()
        return Response(RegulatoryReportSerializer(report).data)


@extend_schema(tags=['Conformité'])
class PrudentialRatioListView(generics.ListAPIView):
    queryset = PrudentialRatio.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.query_params.get('dashboard') == 'true':
            return PrudentialRatioListSerializer
        return PrudentialRatioSerializer


@extend_schema(tags=['Conformité'])
class PrudentialRatioComputeView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        ratios = PrudentialRatio.objects.all()
        updated = []
        for ratio in ratios:
            valeur, statut = self._compute_ratio(ratio)
            ratio.valeur_actuelle = valeur
            ratio.statut = statut
            ratio.save()
            updated.append(PrudentialRatioSerializer(ratio).data)
        return Response({'ratios': updated})

    def _compute_ratio(self, ratio):
        from decimal import Decimal
        valeur = Decimal('0.00')
        statut = PrudentialRatio.StatutChoices.CONFORME
        if ratio.seuil_min is not None and valeur < ratio.seuil_min:
            statut = PrudentialRatio.StatutChoices.NON_CONFORME
        return valeur, statut


@extend_schema(tags=['Conformité'])
class ClassificationListView(generics.ListAPIView):
    queryset = LoanClassification.objects.all()
    serializer_class = LoanClassificationSerializer
    permission_classes = [IsAdminOrAgent]

    def get_queryset(self):
        qs = super().get_queryset()
        classe = self.request.query_params.get('classe')
        if classe:
            qs = qs.filter(classe=classe)
        return qs


@extend_schema(tags=['Conformité'])
class ClassificationUpdateView(generics.UpdateAPIView):
    queryset = LoanClassification.objects.all()
    serializer_class = LoanClassificationSerializer
    permission_classes = [IsAdminOrAgent]
    lookup_field = 'loan_id'
    lookup_url_kwarg = 'loan_id'


@extend_schema(tags=['Conformité'])
class DeclarationSuspicionListCreateView(generics.ListCreateAPIView):
    queryset = DeclarationSuspicion.objects.all()
    permission_classes = [IsAdminOrAgent]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DeclarationSuspicionCreateSerializer
        return DeclarationSuspicionSerializer


@extend_schema(tags=['Conformité'])
class ComplianceDashboardView(APIView):
    permission_classes = [IsAdminOrAgent]

    def get(self, request):
        ratios = PrudentialRatioListSerializer(PrudentialRatio.objects.all(), many=True).data
        reports_count = RegulatoryReport.objects.aggregate(
            total=Count('id'),
            brouillon=Count('id', filter=Q(statut=RegulatoryReport.StatutChoices.BROUILLON)),
            finalise=Count('id', filter=Q(statut=RegulatoryReport.StatutChoices.FINALISE)),
            transmis=Count('id', filter=Q(statut=RegulatoryReport.StatutChoices.TRANSMIS)),
        )
        classifications = LoanClassification.objects.values('classe').annotate(total=Count('id'))
        return Response({
            'ratios': ratios,
            'reports_count': reports_count,
            'classifications': list(classifications),
        })
