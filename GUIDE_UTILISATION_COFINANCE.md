# Guide complet d'utilisation — Plateforme COFINANCE CI

> Ce document explique, **pas à pas et avec des exemples concrets**, ce qu'est la plateforme,
> ce que chaque utilisateur peut faire, et comment **tout tester** soi-même — même sans rien y connaître.
> Suivez-le de haut en bas : à la fin, vous aurez fait fonctionner l'application en entier.

---

## 1. C'est quoi COFINANCE CI ?

COFINANCE CI est une société de **microfinance** (petits crédits) et d'**assurance mobile** en Côte d'Ivoire.
Avant, tout se faisait sur **papier** : un client remplissait un formulaire, un agent le ressaisissait dans Excel,
et ça prenait **5 à 10 jours**. Impossible de suivre un dossier en temps réel.

Cette plateforme **digitalise tout**. Concrètement, elle permet de :

1. **Demander un crédit en ligne** et suivre son dossier en temps réel.
2. **Souscrire une assurance** depuis un téléphone.
3. **Enregistrer et suivre les remboursements** automatiquement (avec intérêts et pénalités).
4. **Discuter en direct (chat temps réel)** avec un conseiller, sans appel téléphonique.
5. **Piloter toute l'activité** via un tableau de bord pour la direction.

Tout passe par une **API** (le « moteur ») documentée, et une **interface web** (l'écran que voit l'utilisateur).

---

## 2. Les 3 acteurs (qui fait quoi)

La plateforme connaît **3 types d'utilisateurs**. Chacun voit et fait des choses différentes.

| Acteur | Qui c'est | Ce qu'il fait principalement |
|--------|-----------|------------------------------|
| **CLIENT** | Le micro-entrepreneur, la commerçante, l'agriculteur | Demande des crédits, souscrit des assurances, suit ses remboursements, ouvre un chat |
| **AGENT** | L'employé de terrain de COFINANCE | Suit les dossiers qui lui sont assignés, enregistre les remboursements, répond aux clients |
| **ADMIN** | La direction / le siège | Valide les crédits, voit toutes les statistiques, gère les utilisateurs, supervise tout |

> **Idée clé :** une même action (ex. « changer le statut d'un crédit ») n'est **pas autorisée** pour tout le monde.
> Un client ne peut pas approuver son propre crédit — seul un admin/agent le peut. La plateforme **bloque** automatiquement ce qui n'est pas permis.

---

## 3. Démarrer la plateforme (à faire une seule fois)

### 3.1 Lancer le projet

Ouvrez un terminal dans le dossier du projet et tapez :

```bash
# 1. Activer l'environnement
venv\Scripts\activate           # Windows
# source venv/bin/activate      # Linux/Mac

# 2. Préparer la base de données
python manage.py migrate

# 3. Remplir avec des données de démonstration (clients, crédits, etc.)
python manage.py seed_db

# 4. Démarrer le serveur
python manage.py runserver
```

L'application est maintenant accessible sur **http://localhost:8000**.

### 3.2 Les identifiants de démonstration

Après `seed_db`, ces comptes existent déjà (tous prêts à tester) :

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| **Admin** | `admin` | `admin123` |
| **Agents** | `agent1`, `agent2`, … `agent5` | `agent123` |
| **Clients** | `client1`, `client2`, … `client20` | `client123` |

### 3.3 Les 3 adresses à connaître

| Adresse | À quoi ça sert |
|---------|----------------|
| **http://localhost:8000/** | L'**interface web** (l'application visible) |
| **http://localhost:8000/api/docs/** | La **documentation interactive (Swagger)** : la liste de toutes les actions possibles, testables directement |
| **http://localhost:8000/api/redoc/** | La même documentation, présentée autrement (Redoc) |

---

## 4. Deux façons de tester (choisissez la vôtre)

Tout ce qui suit peut être testé de **deux manières**. Les deux donnent le même résultat.

### Façon A — L'interface web (le plus simple)
Allez sur **http://localhost:8000/**, connectez-vous, et cliquez dans les menus. Idéal pour « voir » l'application.

### Façon B — Swagger / API (pour tout tester précisément)
Allez sur **http://localhost:8000/api/docs/**. Vous y voyez **toutes les actions** classées par module.
Pour tester une action :
1. Trouvez l'action `POST /api/auth/login/`, cliquez **« Try it out »**.
2. Entrez `{"username": "client1", "password": "client123"}` puis **Execute**.
3. Copiez le **`access`** renvoyé (c'est votre « clé d'entrée », appelée **token**).
4. En haut de la page, cliquez **« Authorize »**, collez `Bearer VOTRE_TOKEN`, validez.
5. Désormais, toutes les actions que vous testez se font **en tant que ce compte**.

> Dans les exemples ci-dessous, on montre la version **API** (avec `curl`) parce qu'elle est précise et copiable.
> Vous pouvez faire exactement la même chose dans Swagger en cliquant.

**Comment se connecter en ligne de commande :**

```bash
# Récupérer son token (sa clé d'accès)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"client1\",\"password\":\"client123\"}"
```

Réponse :
```json
{ "access": "eyJhbGc....LONG_TOKEN", "refresh": "eyJhbGc...." }
```

On réutilise ensuite ce `access` dans **chaque** appel via l'en-tête :
`Authorization: Bearer eyJhbGc....LONG_TOKEN`

---

## 5. Parcours complet du CLIENT (du début à la fin)

> On se connecte en tant que **client1 / client123**. Objectif : demander un crédit, déposer ses pièces,
> suivre son dossier, souscrire une assurance, payer une échéance et discuter avec un conseiller.

### Étape 1 — Se connecter
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"client1\",\"password\":\"client123\"}"
```
➡️ On récupère son **token**. On le note (on l'appellera `$TOKEN`).

### Étape 2 — Voir le catalogue des crédits disponibles
*« Quels types de crédits puis-je demander ? »*
```bash
curl http://localhost:8000/api/loans/products/ \
  -H "Authorization: Bearer $TOKEN"
```
➡️ Renvoie 6 produits : Microcrédit Personnel, Crédit Professionnel, Crédit d'Équipement, Crédit Agricole,
Crédit Solidaire, Crédit Saisonnier (avec taux, montants min/max, durées).

### Étape 3 — Faire une demande de crédit
*« Je veux 150 000 FCFA sur 6 mois pour acheter du stock. »*
```bash
curl -X POST http://localhost:8000/api/loans/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"montant_demande\":\"150000\",\"duree_mois\":6,\"motif\":\"Achat de stock\",\"revenu_mensuel\":\"120000\"}"
```
➡️ Réponse concrète :
```json
{ "id": 42, "montant_demande": "150000.00", "duree_mois": 6,
  "motif": "Achat de stock", "score_eligibilite": 95, "statut": "SOUMISE" }
```
**Ce qui s'est passé tout seul :** la plateforme a **calculé un score d'éligibilité** (ici 95/100) à partir
de l'historique du client, et a mis le dossier au statut **SOUMISE**. **Notez le `id` (42)** : il sert pour la suite.

### Étape 4 — Déposer une pièce justificative (sa carte d'identité)
*« Je joins ma pièce d'identité au dossier. »* (formats acceptés : PDF, JPG, PNG — max 5 Mo)
```bash
curl -X POST http://localhost:8000/api/loans/42/documents/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "type=PIECE_IDENTITE" \
  -F "fichier=@C:/chemin/vers/ma_cni.png"
```
➡️ Le fichier est **réellement enregistré** sur le serveur. Types possibles : `PIECE_IDENTITE`,
`JUSTIFICATIF_REVENU`, `PHOTO_CLIENT`.

### Étape 5 — Revoir ses documents et le détail de son dossier
```bash
# Mes documents pour ce crédit
curl http://localhost:8000/api/loans/42/documents/ -H "Authorization: Bearer $TOKEN"

# Le détail complet du crédit
curl http://localhost:8000/api/loans/42/ -H "Authorization: Bearer $TOKEN"
```
➡️ On voit le fichier déposé (avec son URL) et tous les détails : montant, statut, score, taux, agent assigné…

### Étape 6 — Suivre TOUS ses crédits
```bash
curl http://localhost:8000/api/loans/mine/ -H "Authorization: Bearer $TOKEN"
```

### Étape 7 — Souscrire une assurance
*« Je regarde les assurances et je souscris à la première. »*
```bash
# Voir le catalogue d'assurances
curl http://localhost:8000/api/insurance/products/ -H "Authorization: Bearer $TOKEN"

# Souscrire au produit n°1
curl -X POST http://localhost:8000/api/insurance/policies/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"produit_id\":1}"
```
➡️ Une **police d'assurance** est créée, avec une date de fin calculée automatiquement. Le client sera
prévenu **15 jours avant l'expiration**.
```bash
# Voir mes assurances
curl http://localhost:8000/api/insurance/policies/mine/ -H "Authorization: Bearer $TOKEN"
```

### Étape 8 — Voir ses notifications
*Chaque événement important génère une notification (crédit décaissé, etc.).*
```bash
curl http://localhost:8000/api/notifications/ -H "Authorization: Bearer $TOKEN"
curl http://localhost:8000/api/notifications/unread-count/ -H "Authorization: Bearer $TOKEN"
```
➡️ Exemple de message reçu : *« Votre demande de prêt de 150000 FCFA est maintenant Décaissée. »*

### Étape 9 — Ouvrir un chat avec un conseiller
*« J'ai une question, je discute en direct. »*
```bash
# Ouvrir une conversation
curl -X POST http://localhost:8000/api/chat/conversations/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{}"

# Envoyer un message (remplacez 7 par l'id de la conversation créée)
curl -X POST http://localhost:8000/api/chat/conversations/7/send/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"message\":\"Bonjour, où en est mon dossier ?\"}"
```
➡️ Le message part **instantanément** (temps réel). Voir le **chapitre 8** pour la démo « 2 onglets ».

### Étape 10 — Voir son propre tableau de bord
```bash
curl http://localhost:8000/api/dashboard/client/ -H "Authorization: Bearer $TOKEN"
```
➡️ Résumé personnel : crédits en cours, prochaines échéances, assurances actives.

---

## 6. Parcours complet de l'AGENT

> On se connecte en tant que **agent1 / agent123**. L'agent suit les dossiers, enregistre les paiements
> et répond aux clients.

### Étape 1 — Se connecter
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"agent1\",\"password\":\"agent123\"}"
```

### Étape 2 — Voir son tableau de bord agent
```bash
curl http://localhost:8000/api/dashboard/agent/ -H "Authorization: Bearer $TOKEN"
```
➡️ Ses dossiers assignés, ses montants à recouvrer, ses tâches.

### Étape 3 — Voir les crédits qui lui sont assignés
```bash
curl http://localhost:8000/api/loans/ -H "Authorization: Bearer $TOKEN"
```
➡️ L'agent ne voit **que ses dossiers** (pas ceux des autres agents).

### Étape 4 — Enregistrer un remboursement d'un client
*« Le client m'a remis 25 000 FCFA en espèces pour son crédit n°42. »*
```bash
curl -X POST http://localhost:8000/api/repayments/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"loan\":42,\"montant\":\"25000\",\"mode_paiement\":\"ESPECES\",\"notes\":\"Versement guichet\"}"
```
➡️ Modes possibles : `ORANGE_MONEY`, `WAVE`, `MTN_MOMO`, `ESPECES`. La plateforme calcule
**automatiquement** les pénalités de retard s'il y en a.

### Étape 5 — Voir l'historique des remboursements d'un crédit
```bash
curl http://localhost:8000/api/repayments/loan/42/ -H "Authorization: Bearer $TOKEN"
```

### Étape 6 — Répondre à un client dans le chat
```bash
# Voir les conversations
curl http://localhost:8000/api/chat/conversations/ -H "Authorization: Bearer $TOKEN"

# Répondre
curl -X POST http://localhost:8000/api/chat/conversations/7/send/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"message\":\"Bonjour, votre dossier est en cours d'analyse.\"}"
```

---

## 7. Parcours complet de l'ADMIN (la direction)

> On se connecte en tant que **admin / admin123**. L'admin **valide les crédits**, voit **toutes** les
> statistiques et **gère les utilisateurs**.

### Étape 1 — Se connecter
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

### Étape 2 — Le tableau de bord de pilotage (le cœur pour la direction)
```bash
curl http://localhost:8000/api/dashboard/admin/ -H "Authorization: Bearer $TOKEN"
```
➡️ En temps réel : nombre de demandes par statut, taux de recouvrement, souscriptions actives,
conversations ouvertes, etc.
```bash
# Données pour les graphiques
curl http://localhost:8000/api/dashboard/charts/ -H "Authorization: Bearer $TOKEN"
```

### Étape 3 — Faire avancer un crédit dans le workflow (le plus important)

Un crédit suit **4 étapes obligatoires, dans l'ordre** :

```
SOUMISE  →  EN_ANALYSE  →  APPROUVEE  →  DECAISSEE
                                ↘  (ou)  REJETEE
```

```bash
# 1) Mettre en analyse
curl -X PATCH http://localhost:8000/api/loans/42/status/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"statut\":\"EN_ANALYSE\"}"

# 2) Approuver
curl -X PATCH http://localhost:8000/api/loans/42/status/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"statut\":\"APPROUVEE\"}"

# 3) Décaisser (verser l'argent)
curl -X PATCH http://localhost:8000/api/loans/42/status/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"statut\":\"DECAISSEE\"}"
```

**Ce qui se passe automatiquement au décaissement :** un **échéancier de remboursement complet**
est généré (une ligne par mois, avec la part de capital et la part d'intérêts), et le **client reçoit une notification**.

> **Test important — la plateforme protège le processus :** essayez de sauter une étape
> (passer directement de `SOUMISE` à `DECAISSEE`). La plateforme **refuse** avec une erreur
> *« Transition interdite »*. C'est la preuve que ce n'est pas un simple affichage : les règles métier sont appliquées.

### Étape 4 — Voir l'historique des statuts d'un crédit
```bash
curl http://localhost:8000/api/loans/42/history/ -H "Authorization: Bearer $TOKEN"
```
➡️ Qui a changé quoi et quand (traçabilité complète).

### Étape 5 — Voir l'échéancier généré
```bash
curl http://localhost:8000/api/loans/42/schedule/ -H "Authorization: Bearer $TOKEN"
```
➡️ Exemple d'une échéance : `date 2026-07-14 | mensualité 25 734,21 | capital 24 484,21 | intérêts 1 250,00`.

### Étape 6 — Gérer les utilisateurs
```bash
curl http://localhost:8000/api/auth/clients/ -H "Authorization: Bearer $TOKEN"   # liste des clients
curl http://localhost:8000/api/auth/agents/  -H "Authorization: Bearer $TOKEN"   # liste des agents
curl http://localhost:8000/api/auth/users/   -H "Authorization: Bearer $TOKEN"   # tous les comptes
```

### Étape 7 — Exporter les données (rapports)
```bash
curl http://localhost:8000/api/loans/export/csv/ -H "Authorization: Bearer $TOKEN" -o credits.csv
curl http://localhost:8000/api/loans/export/pdf/ -H "Authorization: Bearer $TOKEN" -o credits.pdf
```

### Étape 8 — Le journal d'audit (qui a fait quoi)
```bash
curl http://localhost:8000/api/common/audit/ -H "Authorization: Bearer $TOKEN"
```

---

## 8. Le chat en temps réel (la démo « 2 onglets »)

C'est l'**innovation phare** : un client et un agent discutent **en direct**, sans recharger la page.

**Comment le démontrer visuellement :**

1. Ouvrez **http://localhost:8000/** dans un **premier onglet**, connecté en **client1**.
   Allez dans la section **Chat** et ouvrez une conversation.
2. Ouvrez **http://localhost:8000/** dans un **deuxième onglet** (ou navigation privée), connecté en **admin** ou **agent1**.
   Ouvrez la même conversation.
3. **Écrivez dans un onglet → le message apparaît instantanément dans l'autre**, sans rafraîchir.
4. **Bonus :** quand une personne tape, l'autre voit *« en train d'écrire… »*.

> Techniquement, ça passe par une **WebSocket** (`ws://localhost:8000/ws/chat/{id}/`). Tout l'historique
> des messages est **sauvegardé** : on peut fermer et rouvrir, les messages sont toujours là.

---

## 9. Modules avancés (bonus au-delà du cahier des charges)

Le projet va plus loin que demandé. Voici ces modules et un exemple pour chacun.

### Épargne (savings)
```bash
curl http://localhost:8000/api/savings/products/ -H "Authorization: Bearer $TOKEN"   # produits d'épargne
curl http://localhost:8000/api/savings/comptes/mine/ -H "Authorization: Bearer $TOKEN" # mes comptes
# Enregistrer un versement (agent/admin)
curl -X POST http://localhost:8000/api/savings/transactions/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"compte\":1,\"type\":\"VERSEMENT\",\"montant\":\"50000\"}"
```

### Groupes solidaires (groups)
```bash
curl http://localhost:8000/api/groups/ -H "Authorization: Bearer $TOKEN"          # tous les groupes
curl http://localhost:8000/api/groups/mine/ -H "Authorization: Bearer $TOKEN"     # mes groupes
```

### Paiements Mobile Money (payments)
```bash
curl http://localhost:8000/api/payments/gateways/ -H "Authorization: Bearer $TOKEN"  # Orange/Wave/MTN
# Initier un paiement
curl -X POST http://localhost:8000/api/payments/initiate/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"gateway\":1,\"telephone\":\"+2250700000000\",\"montant\":\"25000\",\"type\":\"REMBOURSEMENT\"}"
```

### Comptabilité (accounting)
```bash
curl http://localhost:8000/api/accounting/reports/balance/ -H "Authorization: Bearer $TOKEN"
curl http://localhost:8000/api/accounting/reports/bilan/   -H "Authorization: Bearer $TOKEN"
curl http://localhost:8000/api/accounting/reports/compte-resultat/ -H "Authorization: Bearer $TOKEN"
```

### Conformité réglementaire (compliance)
```bash
curl http://localhost:8000/api/compliance/ratios/ -H "Authorization: Bearer $TOKEN"       # ratios prudentiels
curl http://localhost:8000/api/compliance/dashboard/ -H "Authorization: Bearer $TOKEN"    # tableau conformité
```

---

## 10. Scénario complet de A à Z (l'histoire de Jean)

Pour tout voir s'enchaîner, suivez cette **histoire** dans l'ordre :

1. **Jean (client1)** se connecte et **demande un crédit** de 150 000 FCFA (chapitre 5, étapes 1-3).
   → Le dossier est créé en statut **SOUMISE**, avec un **score** calculé automatiquement.
2. **Jean dépose sa pièce d'identité** (étape 4). → Le fichier est enregistré.
3. **L'admin** se connecte, voit la demande sur son **tableau de bord**, et la fait avancer :
   **EN_ANALYSE → APPROUVEE → DECAISSEE** (chapitre 7, étape 3).
4. Au décaissement, **l'échéancier se génère tout seul** et **Jean reçoit une notification**
   *« Votre crédit est décaissé. »*
5. Chaque mois, **l'agent enregistre le remboursement** de Jean (chapitre 6, étape 4).
6. Jean **souscrit une assurance** (chapitre 5, étape 7) et **discute avec un conseiller** dans le chat (chapitre 8).
7. **L'admin** suit le **taux de recouvrement** et exporte un **rapport PDF** (chapitre 7, étapes 2 et 7).

À la fin de ce scénario, vous avez utilisé **tous les modules** de la plateforme.

---

## 11. Récapitulatif de toutes les actions (par module)

| Module | Action | Méthode + adresse | Qui |
|--------|--------|-------------------|-----|
| **Comptes** | S'inscrire | `POST /api/auth/register/` | Tous |
| | Se connecter | `POST /api/auth/login/` | Tous |
| | Voir/modifier son profil | `GET/PUT /api/auth/profile/` | Connecté |
| | Changer mot de passe | `POST /api/auth/change-password/` | Connecté |
| | Mot de passe oublié | `POST /api/auth/forgot-password/` | Tous |
| | Liste clients/agents/users | `GET /api/auth/clients|agents|users/` | Admin |
| **Crédits** | Demander un crédit | `POST /api/loans/` | Client |
| | Mes crédits | `GET /api/loans/mine/` | Client |
| | Détail d'un crédit | `GET /api/loans/{id}/` | Concerné |
| | Changer le statut | `PATCH /api/loans/{id}/status/` | Agent/Admin |
| | Déposer un document | `POST /api/loans/{id}/documents/` | Client |
| | Voir l'échéancier | `GET /api/loans/{id}/schedule/` | Concerné |
| | Historique des statuts | `GET /api/loans/{id}/history/` | Concerné |
| | Catalogue produits | `GET /api/loans/products/` | Connecté |
| | Export CSV / PDF | `GET /api/loans/export/csv|pdf/` | Admin |
| **Remboursements** | Enregistrer un paiement | `POST /api/repayments/` | Agent/Admin |
| | Remboursements d'un crédit | `GET /api/repayments/loan/{id}/` | Concerné |
| **Assurance** | Catalogue | `GET /api/insurance/products/` | Connecté |
| | Souscrire | `POST /api/insurance/policies/` | Client |
| | Mes polices | `GET /api/insurance/policies/mine/` | Client |
| **Notifications** | Mes notifications | `GET /api/notifications/` | Connecté |
| | Non lues (compteur) | `GET /api/notifications/unread-count/` | Connecté |
| | Marquer comme lue | `PATCH /api/notifications/{id}/read/` | Connecté |
| **Chat** | Ouvrir conversation | `POST /api/chat/conversations/` | Client |
| | Envoyer un message | `POST /api/chat/conversations/{id}/send/` | Concerné |
| | Temps réel | `ws://.../ws/chat/{id}/` | Concerné |
| **Tableau de bord** | Admin / Agent / Client | `GET /api/dashboard/admin|agent|client/` | Selon rôle |
| **Épargne** | Comptes / transactions | `GET/POST /api/savings/...` | Selon rôle |
| **Groupes** | Groupes solidaires | `GET /api/groups/...` | Selon rôle |
| **Paiements** | Mobile Money | `POST /api/payments/initiate/` | Connecté |
| **Comptabilité** | Bilan / balance / résultat | `GET /api/accounting/reports/...` | Admin |
| **Conformité** | Ratios / déclarations | `GET /api/compliance/...` | Admin |

> **La liste exhaustive et testable** est toujours sur **http://localhost:8000/api/docs/**.

---

## 12. Questions fréquentes / dépannage

**« J'ai une erreur 401 (Unauthorized). »**
→ Vous n'êtes pas connecté ou votre token a expiré. Reconnectez-vous (`/api/auth/login/`) et utilisez le nouveau `access`.

**« J'ai une erreur 403 (Forbidden). »**
→ Votre rôle n'a pas le droit de faire cette action (ex. un client qui essaie d'approuver un crédit). C'est normal.

**« J'ai une erreur 400 lors de la création. »**
→ Il manque un champ obligatoire ou une valeur est invalide. La réponse indique précisément lequel
(ex. *« revenu_mensuel : ce champ est obligatoire »*).

**« Transition interdite. »**
→ Vous essayez de sauter une étape du workflow d'un crédit. Respectez l'ordre :
SOUMISE → EN_ANALYSE → APPROUVEE → DECAISSEE.

**« Je veux repartir de zéro avec des données propres. »**
→ Relancez `python manage.py seed_db` : la commande réinitialise et recrée les données de démonstration.

---

*Fin du guide. En suivant les chapitres 5, 6 et 7 dans l'ordre, vous aurez testé l'intégralité de la plateforme.*
