from django.core.management.base import BaseCommand

from apps.notifications.tasks import (
    envoyer_alertes_echeances,
    envoyer_alertes_expiration_assurance,
)


class Command(BaseCommand):
    help = 'Déclenche les alertes J-3/J+1 crédits et J-15 assurance'

    def handle(self, *args, **options):
        envoyer_alertes_echeances()
        envoyer_alertes_expiration_assurance()
        self.stdout.write(self.style.SUCCESS('Alertes envoyées avec succès.'))
