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
from apps.accounts.permissions import IsAdmin


@extend_schema(tags=['Santé'], responses={200: OpenApiResponse(description='API is running')})
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'message': 'Cofinance CI API is running'})


@extend_schema(tags=['Audit'])
class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]
    search_fields = ['action', 'model_name', 'object_repr', 'details', 'user__username']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


@extend_schema(tags=['Audit'])
class AuditLogExportPdfView(APIView):
    permission_classes = [IsAdmin]

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


@extend_schema(tags=['Recherche'], responses={200: dict})
class GlobalSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response({'query': query, 'results': {}})

        from apps.loans.models import LoanApplication
        from apps.insurance.models import Policy
        from apps.support_chat.models import Conversation

        user = request.user
        loans = LoanApplication.objects.select_related('client__user', 'agent__user')
        policies = Policy.objects.select_related('client__user', 'produit')
        conversations = Conversation.objects.select_related('client', 'agent')

        if user.role == 'CLIENT':
            loans = loans.filter(client=user.client_profile)
            policies = policies.filter(client=user.client_profile)
            conversations = conversations.filter(client=user)
        elif user.role == 'AGENT':
            loans = loans.filter(agent=user.agent_profile)
            conversations = conversations.filter(agent=user)

        loans = loans.filter(motif__icontains=query)[:10]
        policies = policies.filter(produit__nom__icontains=query)[:10]
        conversations = conversations.filter(messages__message__icontains=query).distinct()[:10]

        return Response({
            'query': query,
            'results': {
                'loans': [{'id': loan.id, 'motif': loan.motif, 'statut': loan.statut} for loan in loans],
                'policies': [{'id': policy.id, 'produit': policy.produit.nom, 'statut': policy.statut} for policy in policies],
                'conversations': [{'id': conv.id, 'status': conv.status} for conv in conversations],
            }
        })