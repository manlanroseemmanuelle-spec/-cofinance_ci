import random
import uuid
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import Client, Agent
from apps.loans.models import LoanApplication, AmortizationSchedule, Document
from apps.repayments.models import Repayment
from apps.insurance.models import InsuranceProduct, Policy
from apps.notifications.models import Notification
from apps.support_chat.models import Conversation, Message
from apps.savings.models import SavingsProduct, SavingsAccount, SavingsTransaction
from apps.groups.models import SolidarityGroup, GroupMember
from apps.accounting.models import Account
from apps.payments.models import PaymentGatewayConfig

User = get_user_model()


class Command(BaseCommand):
    help = 'Génère un jeu de données de démonstration'

    def handle(self, *args, **options):
        self.stdout.write('Génération des données de démonstration...')

        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@cofinance.ci',
                'first_name': 'Admin',
                'last_name': 'Système',
                'telephone': '+2250100000000',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        self.stdout.write(f'[OK] Admin cree: admin / admin123')

        agent_data = [
            {'username': 'agent1', 'email': 'agent1@cofinance.ci', 'first_name': 'Koffi', 'last_name': 'Konan', 'telephone': '+2250100000001', 'matricule': 'AGT001', 'region': 'Abidjan'},
            {'username': 'agent2', 'email': 'agent2@cofinance.ci', 'first_name': 'Aminata', 'last_name': 'Diallo', 'telephone': '+2250100000002', 'matricule': 'AGT002', 'region': 'Abidjan'},
            {'username': 'agent3', 'email': 'agent3@cofinance.ci', 'first_name': 'Moussa', 'last_name': 'Traoré', 'telephone': '+2250100000003', 'matricule': 'AGT003', 'region': 'Bouaké'},
            {'username': 'agent4', 'email': 'agent4@cofinance.ci', 'first_name': 'Fatou', 'last_name': 'Sow', 'telephone': '+2250100000004', 'matricule': 'AGT004', 'region': 'Yamoussoukro'},
            {'username': 'agent5', 'email': 'agent5@cofinance.ci', 'first_name': 'Yao', 'last_name': 'N\'Guessan', 'telephone': '+2250100000005', 'matricule': 'AGT005', 'region': 'San Pedro'},
        ]

        agents = []
        for data in agent_data:
            user, _ = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'telephone': data['telephone'],
                    'role': 'AGENT',
                }
            )
            user.set_password('agent123')
            user.save()
            agent, _ = Agent.objects.get_or_create(
                user=user,
                defaults={
                    'matricule': data['matricule'],
                    'region': data['region'],
                }
            )
            agents.append(agent)
        self.stdout.write(f'[OK] 5 agents crees')

        client_data = [
            {'username': 'client1', 'email': 'client1@email.com', 'first_name': 'Jean', 'last_name': 'Kouamé', 'telephone': '+2250100000011', 'profession': 'Commerçant', 'revenu': 500000, 'annee': 1985},
            {'username': 'client2', 'email': 'client2@email.com', 'first_name': 'Marie', 'last_name': 'Bamba', 'telephone': '+2250100000012', 'profession': 'Enseignante', 'revenu': 350000, 'annee': 1990},
            {'username': 'client3', 'email': 'client3@email.com', 'first_name': 'Paul', 'last_name': 'Yao', 'telephone': '+2250100000013', 'profession': 'Agriculteur', 'revenu': 250000, 'annee': 1980},
            {'username': 'client4', 'email': 'client4@email.com', 'first_name': 'Grace', 'last_name': 'Zadi', 'telephone': '+2250100000014', 'profession': 'Coiffeuse', 'revenu': 200000, 'annee': 1995},
            {'username': 'client5', 'email': 'client5@email.com', 'first_name': 'Ahmed', 'last_name': 'Cissé', 'telephone': '+2250100000015', 'profession': 'Transporteur', 'revenu': 600000, 'annee': 1982},
            {'username': 'client6', 'email': 'client6@email.com', 'first_name': 'Awa', 'last_name': 'Touré', 'telephone': '+2250100000016', 'profession': 'Restauratrice', 'revenu': 450000, 'annee': 1992},
            {'username': 'client7', 'email': 'client7@email.com', 'first_name': 'David', 'last_name': 'Gbagbo', 'telephone': '+2250100000017', 'profession': 'Électricien', 'revenu': 300000, 'annee': 1988},
            {'username': 'client8', 'email': 'client8@email.com', 'first_name': 'Sarah', 'last_name': 'Koné', 'telephone': '+2250100000018', 'profession': 'Couturière', 'revenu': 180000, 'annee': 1998},
            {'username': 'client9', 'email': 'client9@email.com', 'first_name': 'Olivier', 'last_name': 'Niamké', 'telephone': '+2250100000019', 'profession': 'Informaticien', 'revenu': 550000, 'annee': 1991},
            {'username': 'client10', 'email': 'client10@email.com', 'first_name': 'Ruth', 'last_name': 'Aka', 'telephone': '+2250100000020', 'profession': 'Infirmière', 'revenu': 400000, 'annee': 1987},
            {'username': 'client11', 'email': 'client11@email.com', 'first_name': 'Léon', 'last_name': 'Brou', 'telephone': '+2250100000021', 'profession': 'Mécanicien', 'revenu': 320000, 'annee': 1983},
            {'username': 'client12', 'email': 'client12@email.com', 'first_name': 'Esther', 'last_name': 'Kouassi', 'telephone': '+2250100000022', 'profession': 'Vendeuse', 'revenu': 150000, 'annee': 1996},
            {'username': 'client13', 'email': 'client13@email.com', 'first_name': 'Franck', 'last_name': 'Soro', 'telephone': '+2250100000023', 'profession': 'Plombier', 'revenu': 280000, 'annee': 1989},
            {'username': 'client14', 'email': 'client14@email.com', 'first_name': 'Chantal', 'last_name': 'Bénié', 'telephone': '+2250100000024', 'profession': 'Fonctionnaire', 'revenu': 480000, 'annee': 1986},
            {'username': 'client15', 'email': 'client15@email.com', 'first_name': 'Alain', 'last_name': 'Dibi', 'telephone': '+2250100000025', 'profession': 'Photographe', 'revenu': 220000, 'annee': 1994},
            {'username': 'client16', 'email': 'client16@email.com', 'first_name': 'Béatrice', 'last_name': 'Kouadio', 'telephone': '+2250100000026', 'profession': 'Esthéticienne', 'revenu': 380000, 'annee': 1993},
            {'username': 'client17', 'email': 'client17@email.com', 'first_name': 'Thierry', 'last_name': 'Zongo', 'telephone': '+2250100000027', 'profession': 'Chauffeur', 'revenu': 200000, 'annee': 1991},
            {'username': 'client18', 'email': 'client18@email.com', 'first_name': 'Nadège', 'last_name': 'Séka', 'telephone': '+2250100000028', 'profession': 'Comptable', 'revenu': 420000, 'annee': 1990},
            {'username': 'client19', 'email': 'client19@email.com', 'first_name': 'Hervé', 'last_name': 'Mamadou', 'telephone': '+2250100000029', 'profession': 'Coiffeur', 'revenu': 170000, 'annee': 1997},
            {'username': 'client20', 'email': 'client20@email.com', 'first_name': 'Sylvie', 'last_name': 'Allou', 'telephone': '+2250100000030', 'profession': 'Infirmière', 'revenu': 450000, 'annee': 1984},
        ]

        clients = []
        for data in client_data:
            user, _ = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'telephone': data['telephone'],
                    'role': 'CLIENT',
                    'region': random.choice(['Abidjan', 'Bouaké', 'Yamoussoukro', 'San Pedro', 'Man']),
                }
            )
            user.set_password('client123')
            user.save()
            client, _ = Client.objects.get_or_create(
                user=user,
                defaults={
                    'profession': data['profession'],
                    'revenu_mensuel': data['revenu'],
                    'score_credit': random.randint(30, 95),
                    'date_naissance': date(data['annee'], random.randint(1, 12), random.randint(1, 28)),
                    'numero_piece': f'CNI{random.randint(100000, 999999)}',
                }
            )
            clients.append(client)
        self.stdout.write(f'[OK] 20 clients crees (mot de passe: client123)')

        statuts = ['SOUMISE', 'EN_ANALYSE', 'APPROUVEE', 'REJETEE', 'DECAISSEE']
        loan_motifs = [
            "Financement de mon commerce d'habillement",
            "Achat d'équipement agricole",
            "Rénovation de ma boutique",
            "Achat de matière première",
            "Extension de mon activité de transport",
            "Équipement de mon atelier de couture",
            "Achat de stock pour ma pharmacie",
            "Financement de ma campagne agricole",
            "Acquisition de matériel informatique",
            "Création d'un point de vente",
        ]

        for i, client in enumerate(clients):
            for _ in range(random.randint(1, 4)):
                montant = random.choice([100000, 150000, 200000, 300000, 500000, 750000, 1000000])
                duree = random.choice([3, 6, 9, 12, 18, 24])
                statut = random.choice(statuts)

                loan = LoanApplication.objects.create(
                    client=client,
                    montant_demande=montant,
                    duree_mois=duree,
                    motif=random.choice(loan_motifs),
                    revenu_mensuel=client.revenu_mensuel,
                    score_eligibilite=random.randint(20, 95),
                    statut=statut,
                    agent=random.choice(agents) if statut in ['EN_ANALYSE', 'APPROUVEE', 'DECAISSEE'] else None,
                )
                self._create_amortization(loan)

                for _ in range(random.randint(0, 3)):
                    Repayment.objects.create(
                        loan=loan,
                        montant=random.randint(10000, 100000),
                        mode_paiement=random.choice(['ORANGE_MONEY', 'WAVE', 'MTN_MOMO', 'ESPECES']),
                        reference=f"REP-{uuid.uuid4().hex[:8].upper()}",
                        agent=random.choice(agents) if random.random() > 0.5 else None,
                    )
        self.stdout.write(f'[OK] 50+ credits et 100+ remboursements crees')

        products = [
            {'nom': 'Assurance Vie', 'description': 'Protection deces toutes causes', 'prix': 15000, 'duree_jours': 365},
            {'nom': 'Assurance Deces Accidentel', 'description': "Protection en cas d'accident mortel", 'prix': 10000, 'duree_jours': 365},
            {'nom': 'Assurance Invalidite', 'description': "Protection en cas d'invalidite permanente", 'prix': 12000, 'duree_jours': 365},
            {'nom': 'Assurance Maladie', 'description': 'Couverture des frais medicaux', 'prix': 25000, 'duree_jours': 365},
            {'nom': 'Assurance Credit', 'description': 'Protection remboursement credit', 'prix': 20000, 'duree_jours': 365},
            {'nom': 'Assurance Multirisque', 'description': 'Protection complete', 'prix': 35000, 'duree_jours': 365},
            {'nom': 'Assurance Voyage', 'description': 'Protection durant les deplacements', 'prix': 8000, 'duree_jours': 90},
            {'nom': 'Assurance Education', 'description': 'Protection frais de scolarite', 'prix': 18000, 'duree_jours': 365},
            {'nom': 'Assurance Funerailles', 'description': 'Prise en charge des obseques', 'prix': 5000, 'duree_jours': 365},
            {'nom': 'Assurance Sante', 'description': 'Couverture sante elargie', 'prix': 15000, 'duree_jours': 180},
        ]

        for product in products:
            InsuranceProduct.objects.get_or_create(
                nom=product['nom'],
                defaults=product
            )
        self.stdout.write(f'[OK] 10 produits assurance crees')

        for client in clients:
            if random.random() > 0.5:
                produit = InsuranceProduct.objects.order_by('?').first()
                Policy.objects.create(
                    client=client,
                    produit=produit,
                    date_debut=timezone.now().date() - timedelta(days=random.randint(1, 300)),
                    date_fin=timezone.now().date() + timedelta(days=random.randint(1, 180)),
                    statut=random.choice(['ACTIVE', 'ACTIVE', 'ACTIVE', 'EXPIREE']),
                )
        self.stdout.write(f'[OK] Polices d\'assurance crees')

        for client in clients[:20]:
            Notification.objects.create(
                titre='Bienvenue sur Cofinance CI',
                message=f'Cher {client.user.first_name}, votre compte a été créé avec succès.',
                type='SYSTEME',
                user=client.user,
            )
        Notification.objects.create(
            titre='Rappel de remboursement',
            message='Votre échéance de crédit approche. Pensez à effectuer votre remboursement.',
            type='CREDIT', user=clients[0].user
        )
        self.stdout.write(f'[OK] Notifications crees')

        conversations_created = 0
        for client in clients[:15]:
            conv = Conversation.objects.create(client=client.user, agent=random.choice(agents).user)
            for _ in range(random.randint(1, 5)):
                Message.objects.create(
                    conversation=conv,
                    sender=client.user,
                    message=f"Bonjour, j'ai une question concernant mon dossier."
                )
                Message.objects.create(
                    conversation=conv,
                    sender=conv.agent,
                    message=f"Bonjour {client.user.first_name}, je suis là pour vous aider."
                )
            conversations_created += 1
        self.stdout.write(f'[OK] {conversations_created} conversations chat crees')

        savings_products = [
            SavingsProduct.objects.create(nom='Epargne Libre', type='EPARGNE', taux_interet_annuel=3.5, montant_min=5000, montant_max=5000000, est_actif=True),
            SavingsProduct.objects.create(nom='Depot a Vue', type='DAV', taux_interet_annuel=1.0, montant_min=10000, montant_max=0, est_actif=True),
            SavingsProduct.objects.create(nom='Depot a Terme 3 mois', type='DAT', taux_interet_annuel=5.0, duree_jours=90, montant_min=100000, montant_max=5000000, est_actif=True),
            SavingsProduct.objects.create(nom='Depot a Terme 6 mois', type='DAT', taux_interet_annuel=6.0, duree_jours=180, montant_min=100000, montant_max=10000000, est_actif=True),
            SavingsProduct.objects.create(nom='Epargne Logement', type='LOGEMENT', taux_interet_annuel=4.0, montant_min=50000, montant_max=0, est_actif=True),
        ]
        clients_all = list(Client.objects.all())
        agents_all = list(Agent.objects.all())
        savings_accounts_created = 0
        for i, client in enumerate(clients_all[:10]):
            prod = random.choice(savings_products)
            compte = SavingsAccount.objects.create(
                client=client, produit=prod, solde=random.uniform(50000, 2000000),
                statut='ACTIF'
            )
            for _ in range(random.randint(0, 5)):
                t_type = random.choice(['VERSEMENT', 'VERSEMENT', 'RETRAIT', 'INTERET_CREDITEUR'])
                montant = random.uniform(10000, 300000)
                SavingsTransaction.objects.create(
                    compte=compte, type=t_type, montant=montant,
                    solde_avant=compte.solde, solde_apres=compte.solde + (montant if t_type in ['VERSEMENT','INTERET_CREDITEUR'] else -montant),
                    agent=random.choice(agents_all)
                )
                if t_type in ['VERSEMENT','INTERET_CREDITEUR']:
                    compte.solde += montant
                else:
                    compte.solde = max(0, compte.solde - montant)
            compte.save()
            savings_accounts_created += 1
        self.stdout.write(f'[OK] {savings_accounts_created} comptes epargne crees')

        group_types = ['SHG', 'JLG']
        groups_created = 0
        for i in range(6):
            g = SolidarityGroup.objects.create(
                nom=f'Groupe Solidaire {chr(65+i)}',
                type=random.choice(group_types),
                centre=random.choice(['Abidjan', 'Yamoussoukro', 'Bouake', 'San-Pedro']),
                region=random.choice(['Lagunes', 'Lacs', 'Vallee du Bandama', 'Bas-Sassandra']),
                responsable=random.choice(clients_all) if random.random() > 0.3 else None,
                agent=random.choice(agents_all) if random.random() > 0.4 else None,
                statut=random.choice(['ACTIF', 'ACTIF', 'ACTIF', 'INACTIF']),
            )
            members_count = random.randint(5, 15)
            for m in random.sample(clients_all, min(members_count, len(clients_all))):
                GroupMember.objects.create(
                    groupe=g, client=m,
                    role=random.choice(['CHEF', 'MEMBRE', 'MEMBRE', 'MEMBRE', 'SECRETAIRE']),
                    est_actif=True
                )
            groups_created += 1
        self.stdout.write(f'[OK] {groups_created} groupes solidaires crees')

        for code, nom, typ in [
            ('101', 'Caisse', 'ACTIF'), ('131', 'Capital Social', 'PASSIF'),
            ('411', 'Clients', 'ACTIF'), ('421', 'Fournisseurs', 'PASSIF'),
            ('511', 'Banque', 'ACTIF'), ('701', 'Revenus', 'PRODUIT'),
            ('601', 'Charges Personnel', 'CHARGE'), ('661', 'Interets', 'CHARGE'),
            ('471', 'Compte de Tiers', 'PASSIF'), ('521', 'Prets', 'ACTIF'),
        ]:
            Account.objects.create(code=code, nom=nom, type=typ, solde_actuel=random.uniform(100000, 50000000))
        self.stdout.write(f'[OK] 10 comptes comptables crees')

        PaymentGatewayConfig.objects.create(code='OM', nom='Orange Money', api_url='https://api.orange.com', api_key='key_om', api_secret='secret_om', est_actif=True)
        PaymentGatewayConfig.objects.create(code='WV', nom='Wave', api_url='https://api.wave.com', api_key='key_wv', api_secret='secret_wv', est_actif=True)
        PaymentGatewayConfig.objects.create(code='MTN', nom='MTN Mobile Money', api_url='https://api.mtn.com', api_key='key_mtn', api_secret='secret_mtn', frais_pourcentage=1.5, est_actif=True)
        self.stdout.write(f'[OK] 3 passerelles de paiement crees')

        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Donnees de demonstration generees avec succes!'))
        self.stdout.write(f'   Admin: admin / admin123')
        self.stdout.write(f'   Agents: agent1 à agent5 / agent123')
        self.stdout.write(f'   Clients: client1 à client20 / client123')

    def _create_amortization(self, loan):
        taux_mensuel = (loan.taux_interet / 100) / 12
        capital = float(loan.montant_demande)
        n = loan.duree_mois

        mensualite = capital * (taux_mensuel * (1 + taux_mensuel) ** n) / ((1 + taux_mensuel) ** n - 1)

        capital_restant = capital
        date_debut = timezone.now().date() + timedelta(days=30)

        for i in range(1, n + 1):
            part_interet = capital_restant * taux_mensuel
            part_capital = mensualite - part_interet
            capital_restant -= part_capital

            if i == n:
                part_capital += capital_restant
                mensualite = part_capital + part_interet
                capital_restant = 0

            AmortizationSchedule.objects.create(
                loan=loan,
                mensualite=round(mensualite, 2),
                date_echeance=date_debut + timedelta(days=30 * (i - 1)),
                capital_restant=round(max(capital_restant, 0), 2),
                part_capital=round(part_capital, 2),
                part_interet=round(part_interet, 2),
                numero_mensualite=i,
            )
