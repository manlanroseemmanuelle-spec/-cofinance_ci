# Cofinance CI — Plateforme de Microfinance

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.x-green)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.x-red)](https://django-rest-framework.org)

Plateforme digitale de gestion de microcrédits, d'assurance mobile, d'épargne, de groupes solidaires et de support client en temps réel — conforme aux exigences BCEAO.

## Fonctionnalités

### Modules principaux
| Module | Description |
|--------|-------------|
| **Authentification** | JWT, 3 rôles (ADMIN, AGENT, CLIENT), réinitialisation mot de passe |
| **Crédits** | 6 types de prêts, workflow soumission→analyse→approbation→décaissement, score d'éligibilité automatique, échéancier, garanties, restructuration |
| **Remboursements** | Enregistrement paiements, pénalités 1%/jour, historique, alertes J-3/J+1 |
| **Assurance** | Produits, souscription, expiration J-15, consultation polices |
| **Épargne** | Produits, comptes (CMP-XXXXXX), transactions (TXN-XXXXXX), synthèse |
| **Groupes solidaires** | SHG/JLG, membres (CHEF/MEMBRE/SECRETAIRE), prêts de groupe |
| **Support client** | Chat WebSocket temps réel, présence en ligne, indicateur de frappe, assignation automatique agent |
| **Notifications** | 5 types, lecture/ non-lu, push WebSocket |
| **Dashboard** | KPIs temps réel, graphiques, filtres par agent/région/période |
| **Calendrier** | Échéances 90 jours, filtres, surlignage retards |
| **Comptabilité** | Plan PC-SFD, journal, Grand Livre, Balance, Bilan, CRP |
| **Conformité** | Rapports réglementaires, ratios prudentiels, classification créances, LCB-FT |
| **Paiements** | Passerelles Mobile Money (OM/Wave/MoMo), transactions, comptes |

### Technologies
- **Backend** : Django 6.0, Django REST Framework, SimpleJWT, Channels 4, Daphne
- **Base de données** : SQLite (dev) / PostgreSQL (prod)
- **Temps réel** : WebSocket via Channels + Redis (optionnel)
- **Tâches asynchrones** : Celery + Redis (optionnel)
- **Documentation API** : drf-spectacular (Swagger + Redoc)
- **Frontend** : Vue.js 2 SPA intégrée (single page application)
- **PWA** : manifest.json, service worker, offline-ready

## Prérequis

- Python 3.11+
- Redis (optionnel — pour WebSocket et Celery)
- Git

## Installation rapide

```bash
# 1. Cloner le dépôt
git clone https://github.com/manlanroseemmanuelle-spec/cofinance_ci.git
cd cofinance_ci

# 2. Créer et activer l'environnement virtuel
python -m venv venv
# Windows : venv\Scripts\activate
# Linux/macOS : source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. Charger les données de démonstration
python manage.py seed_db

# 6. Lancer le serveur
python manage.py runserver
```

## Configuration

### Variables d'environnement (.env)

| Variable | Défaut | Description |
|----------|--------|-------------|
| `SECRET_KEY` | Clé Django par défaut | Changez-la en production ! |
| `DEBUG` | `True` | Passer à `False` en production |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hôtes autorisés |
| `DB_ENGINE` | `sqlite` | `postgresql` pour la production |
| `CHANNEL_LAYER_BACKEND` | `channels.layers.InMemoryChannelLayer` | `channels_redis.core.RedisChannelLayer` pour Redis |
| `REDIS_URL` | `redis://localhost:6379/0` | URL Redis |

## Accès

### Identifiants de démonstration

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| **Administrateur** | `admin` | `admin123` |
| **Agent** | `agent1` à `agent5` | `agent123` |
| **Client** | `client1` à `client20` | `client123` |

### URLs

| URL | Description |
|-----|-------------|
| `http://localhost:8000/` | Application SPA |
| `http://localhost:8000/api/docs/` | Documentation Swagger |
| `http://localhost:8000/api/redoc/` | Documentation Redoc |
| `http://localhost:8000/api/schema/` | Schéma OpenAPI |

## API — Endpoints principaux

### Authentification
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/auth/login/` | Connexion (JWT) |
| POST | `/api/auth/register/` | Inscription |
| POST | `/api/auth/refresh/` | Rafraîchir token |
| GET/PUT | `/api/auth/profile/` | Profil utilisateur |
| POST | `/api/auth/change-password/` | Changer mot de passe |
| POST | `/api/auth/forgot-password/` | Demande réinitialisation |
| POST | `/api/auth/reset-password/` | Réinitialiser mot de passe |

### Crédits
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET/POST | `/api/loans/` | Lister/créer (admin) |
| GET | `/api/loans/mine/` | Mes crédits (client/agent) |
| GET/PUT | `/api/loans/<id>/` | Détail/modifier |
| POST | `/api/loans/<id>/status/` | Changer statut |
| POST | `/api/loans/<id>/documents/` | Upload document |
| GET | `/api/loans/products/` | Produits de crédit |

### Chat
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET/POST | `/api/chat/conversations/` | Lister/créer conversation |
| GET | `/api/chat/conversations/<id>/messages/` | Messages |
| POST | `/api/chat/conversations/<id>/send/` | Envoyer message |
| PUT | `/api/chat/conversations/<id>/assign/` | Assigner agent |
| PUT | `/api/chat/conversations/<id>/close/` | Fermer conversation |

### Dashboard
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/dashboard/admin/` | Dashboard admin (filtres: agent_id, region, period) |
| GET | `/api/dashboard/agent/` | Dashboard agent |
| GET | `/api/dashboard/client/` | Dashboard client |
| GET | `/api/dashboard/charts/` | Données graphiques |
| GET | `/api/dashboard/calendar/` | Calendrier échéances 90j |
| GET | `/api/dashboard/clients/` | Liste clients (admin/agent) |
| GET | `/api/dashboard/agents/` | Liste agents (filtre) |
| GET | `/api/dashboard/regions/` | Liste régions (filtre) |

## WebSocket

### Chat
```
ws://localhost:8000/ws/chat/<conversation_id>/?token=<jwt_token>
```

Types de messages :
- `new_message` : Nouveau message
- `user_status` : Présence en ligne/hors-ligne
- `typing` : Indicateur de frappe

### Notifications
```
ws://localhost:8000/ws/notifications/?token=<jwt_token>
```

Types de messages :
- `notification` : Nouvelle notification

## Tâches Celery

```bash
# Worker
celery -A config worker -l info

# Beat (planificateur)
celery -A config beat -l info

# Worker + Beat combiné
celery -A config worker -B -l info
```

Tâches planifiées :
- `envoyer_alertes_echeances` : Quotidienne — alertes J-3 et J+1
- `envoyer_alertes_expiration_assurance` : Quotidienne — expiration assurance J-15

## Tests

```bash
python manage.py test
```

## Production

```bash
# Basculer vers PostgreSQL dans .env
DB_ENGINE=postgresql
POSTGRES_DB=cofinance
POSTGRES_USER=cofinance
POSTGRES_PASSWORD=****

# Collecte des fichiers statiques
python manage.py collectstatic --noinput

# Lancer avec Daphne (ASGI)
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

## Architecture du projet

```
cofinance_ci/
├── apps/
│   ├── accounts/        # Utilisateurs, rôles, JWT
│   ├── loans/           # Crédits, amortissement, garanties
│   ├── repayments/      # Remboursements, pénalités
│   ├── insurance/       # Assurance produits/polices
│   ├── savings/         # Épargne
│   ├── groups/          # Groupes solidaires
│   ├── accounting/      # Comptabilité PC-SFD
│   ├── compliance/      # Conformité BCEAO
│   ├── payments/        # Paiements Mobile Money
│   ├── notifications/   # Notifications in-app
│   ├── support_chat/    # Chat WebSocket temps réel
│   ├── dashboard/       # Tableaux de bord
│   └── common/          # Audit, search, health
├── config/              # Configuration Django
├── templates/           # Templates (SPA Vue.js)
├── static/              # Fichiers statiques (PWA)
├── manage.py
└── requirements.txt
```

## Licence

Projet interne — COFINANCE CI
