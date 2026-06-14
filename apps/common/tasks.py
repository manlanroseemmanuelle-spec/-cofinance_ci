from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def archiver_donnees():
    """Archive les données anciennes (soft delete) pour performance."""
    from apps.notifications.models import Notification
    from apps.common.models import AuditLog

    cutoff = timezone.now() - timedelta(days=365)

    # Archiver notifications > 1 an
    old_notifs = Notification.objects.filter(date_creation__lt=cutoff)
    count_notifs = old_notifs.count()
    old_notifs.delete()

    # Archiver audit logs > 3 ans
    audit_cutoff = timezone.now() - timedelta(days=365*3)
    old_audits = AuditLog.objects.filter(timestamp__lt=audit_cutoff)
    count_audits = old_audits.count()
    old_audits.delete()

    return f"Archivé: {count_notifs} notifications, {count_audits} logs"
