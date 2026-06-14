from __future__ import absolute_import, unicode_literals
from pathlib import Path
from datetime import timedelta
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-default-key-change-me')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'channels',

    'apps.accounts',
    'apps.loans',
    'apps.repayments',
    'apps.insurance',
    'apps.notifications',
    'apps.support_chat',
    'apps.dashboard',
    'apps.common',
    'apps.savings',
    'apps.groups',
    'apps.accounting',
    'apps.compliance',
    'apps.payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.accounts.middleware.LoginHistoryMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DB_ENGINE = config('DB_ENGINE', default='sqlite')
if DB_ENGINE == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('POSTGRES_DB'),
            'USER': config('POSTGRES_USER'),
            'PASSWORD': config('POSTGRES_PASSWORD'),
            'HOST': config('POSTGRES_HOST', default='localhost'),
            'PORT': config('POSTGRES_PORT', default='5432'),
            'CONN_MAX_AGE': config('POSTGRES_CONN_MAX_AGE', default=60, cast=int),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

CHANNEL_LAYER_BACKEND = config('CHANNEL_LAYER_BACKEND', default='channels.layers.InMemoryChannelLayer')
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': CHANNEL_LAYER_BACKEND,
    },
}
if CHANNEL_LAYER_BACKEND == 'channels_redis.core.RedisChannelLayer':
    CHANNEL_LAYERS['default']['CONFIG'] = {
        'hosts': [{
            'address': config('REDIS_URL', default='redis://localhost:6379/0'),
            'protocol': 2,
        }],
    }

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': config('DRF_ANON_THROTTLE', default='100/day'),
        'user': config('DRF_USER_THROTTLE', default='1000/day'),
        'login': config('DRF_LOGIN_THROTTLE', default='10/min'),
        'register': '3/min',
        'forgot_password': '3/min',
        'reset_password': '5/min',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Cofinance CI - API Microfinance',
    'DESCRIPTION': """
Plateforme de microfinance intégrée — API REST complète avec authentification JWT,
WebSocket temps réel, et automatisation des processus métier.

## Modules
- **Comptes & Auth** — Inscription, connexion, JWT, profils CLIENT/AGENT/ADMIN/AUDITEUR/COMPTABLE
- **Crédits** — Cycle complet: soumission, analyse, approbation, décaissement, remboursement
- **Remboursements** — Avec pénalités de retard, amortissement, statut auto REMBOURSEE
- **Épargne** — Versements, retraits, intérêts créditeurs, frais
- **Comptabilité** — Écritures, grand livre, balance, bilan, compte de résultat
- **Conformité** — Ratios prudentiels (TIER1, NPL, LIQUIDITY, COVERAGE, PORTFOLIO_QUALITY)
- **Paiements** — Initiation, callback simulation, passerelles Mobile Money
- **Assurance** — Produits, souscription, expiration
- **Messagerie** — Support Chat avec WebSocket + FAQ chatbot automatique
- **Notifications** — Push WebSocket temps réel, email (console en dev)
- **Groupes solidaires** — SHG, GEC, garants solidaires
- **Audit** — Journalisation exhaustive + détection fraude (4 règles)
- **Tableau de bord** — KPIs, statistiques, calendrier des échéances

## Automatisations
- Relance échéances impayées J+1/J+7/J+30 (Celery)
- Calcul intérêts épargne mensuel
- Archivage automatique (notifications > 1 an, audit > 3 ans)
- WebSocket push sur création de notification
- Détection fraude multi-règles

## Prérequis techniques
- Authentification: Bearer JWT (access + refresh)
- Pagination: ?page=1&page_size=10
- Filtres: ?statut=, ?from=, ?to=, ?search=
- WebSocket: ws://host/ws/chat/{id}/?token=JWT
""",
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'TAGS': [
        {'name': 'Authentification', 'description': 'Inscription, connexion, JWT, mot de passe oublié'},
        {'name': 'Crédits', 'description': 'Soumission, analyse, approbation, décaissement, statuts'},
        {'name': 'Remboursements', 'description': 'Remboursements avec pénalités, amortissement'},
        {'name': 'Épargne', 'description': 'Comptes et transactions épargne'},
        {'name': 'Comptabilité', 'description': 'Journal, grand livre, balance, bilan, résultat'},
        {'name': 'Conformité', 'description': 'Ratios prudentiels, classification, rapports'},
        {'name': 'Paiements', 'description': 'Initiation, callback simulation, passerelles Mobile Money'},
        {'name': 'Assurance', 'description': 'Produits et polices d\'assurance'},
        {'name': 'Support Chat', 'description': 'Conversations, messages, FAQ chatbot'},
        {'name': 'Notifications', 'description': 'Notifications push WebSocket'},
        {'name': 'Tableau de bord', 'description': 'KPIs, statistiques, calendrier'},
        {'name': 'Groupes', 'description': 'Groupes solidaires, membres, prêts collectifs'},
        {'name': 'Audit', 'description': 'Journal d\'audit, logs de connexion'},
        {'name': 'Administration', 'description': 'Gestion des utilisateurs'},
    ],
    'ENUM_NAME_OVERRIDES': {
        'TypeEnum': ['PIECE_IDENTITE', 'JUSTIFICATIF_REVENU', 'CONTRAT_TRAVAIL', 'FACTURE', 'AUTRE'],
        'StatutEnum': ['SOUMISE', 'EN_ANALYSE', 'APPROUVEE', 'REJETEE', 'DECAISSEE', 'REMBOURSEE'],
    },
}

# ── Email (development: console backend) ──────────────────────────────
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@cofinance.ci')

CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULE = {
    'alertes-echeances-j3-j1': {
        'task': 'apps.notifications.tasks.envoyer_alertes_echeances',
        'schedule': 60 * 60 * 24,
    },
    'alertes-assurance-j15': {
        'task': 'apps.notifications.tasks.envoyer_alertes_expiration_assurance',
        'schedule': 60 * 60 * 24,
    },
    'calcul-interets-epargne': {
        'task': 'apps.savings.tasks.calculer_interets_epargne',
        'schedule': 60 * 60 * 24 * 30,
    },
    'relance-echeances-impayees': {
        'task': 'apps.repayments.tasks.relance_echeances_impayees',
        'schedule': 60 * 60 * 24,
    },
}


