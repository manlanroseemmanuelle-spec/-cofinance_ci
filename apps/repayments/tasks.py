from celery import shared_task
from django.utils import timezone


@shared_task
def relance_echeances_impayees():
    from django.core.mail import send_mail
    from django.conf import settings
    from apps.loans.models import AmortizationSchedule
    from apps.notifications.models import Notification

    today = timezone.now().date()
    overdue = AmortizationSchedule.objects.filter(
        est_paye=False,
        date_echeance__lt=today,
        loan__statut='DECAISSEE',
    ).select_related('loan__client__user')

    for echeance in overdue:
        jours_retard = (today - echeance.date_echeance).days
        client = echeance.loan.client
        titre = f"Échéance #{echeance.numero_mensualite} impayée (J+{jours_retard})"
        message = f"Votre échéance de {echeance.mensualite} FCFA du {echeance.date_echeance} est impayée depuis {jours_retard} jours."

        Notification.objects.create(
            titre=titre,
            message=message,
            type='REMBOURSEMENT',
            user=client.user,
        )

        if client.user.email and jours_retard in (1, 7, 30):
            send_mail(
                subject=titre,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.user.email],
                fail_silently=True,
            )
