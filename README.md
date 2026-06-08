# Cofinance CI - Plateforme de Microfinance

Plateforme de microfinance professionnelle avec API REST, authentification JWT, WebSocket temps réel, documentation Swagger, gestion des rôles et tableau de bord.

## Fonctionnalités

- Authentification JWT (inscription, connexion, refresh)
- Gestion des rôles (Client, Agent, Administrateur)
- Demandes de crédit avec score d'éligibilité automatique
- Échéancier de remboursement automatique
- Remboursements avec calcul de pénalités
- Assurance mobile (produits et souscriptions)
- Notifications automatiques
- Chat temps réel via WebSocket
- Tableau de bord administrateur, agent et client
- Documentation Swagger/Redoc
- Pagination, filtrage et recherche
- Upload de documents

## Technologies

- **Django 5+** - Framework web
- **Django REST Framework** - API REST
- **SimpleJWT** - Authentification JWT
- **Django Channels** - WebSocket
- **Celery + Redis** - Tâches asynchrones
- **drf-spectacular** - Documentation Swagger
- **SQLite** (développement) / **PostgreSQL** (production)

## Installation

```bash
# Cloner le projet
git clone https://github.com/votre-username/cofinance_ci.git
cd cofinance_ci

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py makemigrations
python manage.py migrate

# Générer les données de démonstration
python manage.py seed_db

# Lancer le serveur
python manage.py runserver
```

## Accès

| Rôle | Identifiant | Mot de passe |
|------|------------|-------------|
| Admin | admin | admin123 |
| Agent | agent1 | agent123 |
| Client | client1 | client123 |

## Documentation API

- Swagger : http://localhost:8000/api/docs/
- Redoc : http://localhost:8000/api/redoc/
- Schema : http://localhost:8000/api/schema/

## Endpoints API

### Authentification
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/refresh/` - Rafraîchir token
- `GET /api/auth/profile/` - Profil utilisateur
- `POST /api/auth/change-password/` - Changer mot de passe

### Crédits
- `GET/POST /api/loans/` - Liste/Créer demande
- `GET /api/loans/mine/` - Mes crédits
- `GET/PUT/DELETE /api/loans/{id}/` - Détail
- `PUT /api/loans/{id}/status/` - Mettre à jour statut
- `GET /api/loans/{id}/schedule/` - Échéancier
- `GET/POST /api/loans/{id}/documents/` - Documents

### Remboursements
- `GET/POST /api/repayments/` - Liste/Créer
- `GET /api/repayments/loan/{id}/` - Remboursements d'un prêt

### Assurance
- `GET /api/insurance/products/` - Produits
- `GET/POST /api/insurance/policies/` - Polices
- `GET /api/insurance/policies/mine/` - Mes polices

### Notifications
- `GET /api/notifications/` - Mes notifications
- `GET /api/notifications/unread-count/` - Non lues
- `POST /api/notifications/mark-all-read/` - Tout marquer lu

### Chat (WebSocket)
- `POST /api/chat/conversations/` - Nouvelle conversation
- `GET /api/chat/conversations/` - Mes conversations
- `GET /api/chat/conversations/{id}/messages/` - Messages
- `WebSocket ws://localhost:8000/ws/chat/{id}/` - Chat temps réel

### Dashboard
- `GET /api/dashboard/admin/` - Admin
- `GET /api/dashboard/agent/` - Agent
- `GET /api/dashboard/client/` - Client

## WebSocket Chat

```javascript
const socket = new WebSocket('ws://localhost:8000/ws/chat/1/');
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data.message);
};
socket.send(JSON.stringify({message: 'Bonjour!'}));
```
