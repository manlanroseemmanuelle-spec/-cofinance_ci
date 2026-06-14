from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, generics
from rest_framework.views import APIView
from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from io import BytesIO
from .models import AuditLog
from .serializers import AuditLogSerializer
from apps.accounts.permissions import IsAdmin, IsAdminOrAuditeur, IsAuditeur


@extend_schema(tags=['Santé'], responses={200: OpenApiResponse(description='API is running')})
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'message': 'Cofinance CI API is running'})


@extend_schema(tags=['Audit'])
class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrAuditeur]
    search_fields = ['action', 'model_name', 'object_repr', 'details', 'user__username']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


@extend_schema(tags=['Audit'])
class AuditLogExportPdfView(APIView):
    permission_classes = [IsAdminOrAuditeur]

    def get(self, request):
        qs = AuditLog.objects.select_related('user').order_by('-timestamp')
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        action = request.query_params.get('action')
        if date_from:
            qs = qs.filter(timestamp__gte=date_from)
        if date_to:
            qs = qs.filter(timestamp__lte=date_to)
        if action:
            qs = qs.filter(action=action)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph('Journal d\'audit', styles['Title']))
        elements.append(Spacer(1, 6*mm))
        elements.append(Paragraph(f'Généré le {timezone.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))
        elements.append(Spacer(1, 4*mm))

        data = [['Date', 'Action', 'Modèle', 'ID', 'Utilisateur', 'Détails']]
        for log in qs[:500]:
            data.append([
                log.timestamp.strftime('%d/%m/%Y %H:%M'),
                log.get_action_display(),
                log.model_name,
                str(log.object_id or '-'),
                log.user.username if log.user else 'Système',
                (log.details[:50] + '...' if log.details and len(log.details) > 50 else (log.details or ''))
            ])

        col_widths = [40, 50, 60, 30, 50, 80]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="audit.pdf"'
        return response


from rest_framework.pagination import PageNumberPagination


class SearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


@extend_schema(tags=['Recherche'], responses={200: dict})
class GlobalSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response({'results': [], 'query': query})

        from django.db.models import Q
        from apps.loans.models import LoanApplication
        from apps.insurance.models import Policy
        from apps.support_chat.models import Conversation

        results = []

        loans = LoanApplication.objects.filter(
            Q(id__icontains=query) | Q(client__user__first_name__icontains=query) | Q(client__user__last_name__icontains=query)
        )[:5]
        for l in loans:
            results.append({
                'object_id': l.id,
                'object_repr': f"Prêt #{l.id} - {l.client.user.get_full_name()} - {l.montant_demande} FCFA",
                'model_name': 'LoanApplication',
                'action': 'Crédit',
                'user_details': {'username': l.client.user.username},
            })

        policies = Policy.objects.filter(
            Q(client__user__first_name__icontains=query) | Q(client__user__last_name__icontains=query)
        )[:5]
        for p in policies:
            results.append({
                'object_id': p.id,
                'object_repr': f"Police #{p.id} - {p.produit.nom} - {p.client.user.get_full_name()}",
                'model_name': 'Policy',
                'action': 'Assurance',
                'user_details': {'username': p.client.user.username},
            })

        conversations = Conversation.objects.filter(
            Q(client_name__icontains=query) | Q(id__icontains=query)
        )[:5]
        for c in conversations:
            results.append({
                'object_id': c.id,
                'object_repr': f"Conversation #{c.id} - {c.client_name or 'Client'}",
                'model_name': 'Conversation',
                'action': 'Chat',
                'user_details': {'username': c.client_name or 'Client'},
            })

        paginator = SearchPagination()
        page = paginator.paginate_queryset(results, request)
        if page is not None:
            return paginator.get_paginated_response(page)

        return Response({'results': results, 'query': query})