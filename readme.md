# Facebook Webhook – Guide de démarrage

## 1. Présentation

Cette application utilise **Python et FastAPI** pour recevoir, via les Webhooks de Meta, les notifications de commentaires d'une Page Facebook.

Les commentaires reçus (nouveaux, modifiés ou supprimés) sont enregistrés dans un **fichier CSV**, lisible directement avec Excel, LibreOffice ou n'importe quel éditeur de texte.

Il est possible de ne conserver que les commentaires d'une publication précise grâce à la variable `FACEBOOK_POST_ID`.

## 2. Prérequis

Avant de démarrer, assure-toi d'avoir installé :

- Python 3.11 ou supérieur
- pip
- ngrok (pour exposer le serveur local à Facebook)

Il te faut aussi une application Meta (type « Business ») liée à ta Page Facebook.

## 3. Structure du projet

```text
facebook-webhook/
│
├── .venv/
├── data/
│   └── facebook_comments.csv
│
├── main.py            # Création de l'application et démarrage
├── config.py          # Variables d'environnement et colonnes du CSV
├── webhook.py         # Routes GET et POST du webhook
├── extractor.py       # Extraction des commentaires du payload Facebook
├── storage.py         # Classe CommentStore (lecture/écriture du CSV)
├── security.py        # Vérification du token et de la signature
├── utils.py           # Fonctions utilitaires (dates, protection CSV)
├── .env
└── requirements.txt
```

Le dossier `data` et le fichier `facebook_comments.csv` sont créés automatiquement au premier démarrage.

## 4. Installation

Ouvre PowerShell dans le répertoire du projet.

### Étape 1 : Créer l'environnement virtuel

```powershell
py -m venv .venv
```

### Étape 2 : Activer l'environnement virtuel

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloque l'exécution du script :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Puis réactive l'environnement virtuel.

### Étape 3 : Installer les dépendances

```powershell
pip install -r requirements.txt
```

## 5. Configuration du fichier .env

À la racine du projet, crée un fichier `.env` (tu peux copier `.env.example`) :

```env
FACEBOOK_VERIFY_TOKEN=mon_token_de_verification
FACEBOOK_APP_SECRET=TON_APP_SECRET

# Optionnel
FACEBOOK_POST_ID=
COMMENTS_CSV=data/facebook_comments.csv
```

| Variable | Obligatoire | Description |
|---|---|---|
| `FACEBOOK_VERIFY_TOKEN` | Oui | Token personnel que tu choisis, utilisé pour valider l'URL du webhook. |
| `FACEBOOK_APP_SECRET` | Oui | App Secret fourni par Meta, utilisé pour vérifier la signature des requêtes. |
| `FACEBOOK_POST_ID` | Non | Identifiant d'une publication au format `<PAGE_ID>_<POST_ID>`. Si renseigné, seuls les commentaires de cette publication sont enregistrés. Laisse vide pour toutes les publications. |
| `COMMENTS_CSV` | Non | Chemin du fichier CSV. Par défaut : `data/facebook_comments.csv`. |

Si `FACEBOOK_VERIFY_TOKEN` ou `FACEBOOK_APP_SECRET` est absent, l'application refuse de démarrer et affiche la variable manquante.

**Important :** ne partage jamais ton App Secret et ne le publie pas sur un dépôt Git (ajoute `.env` à ton `.gitignore`).

## 6. Démarrer l'application

Dans PowerShell, depuis le dossier du projet :

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Ou simplement :

```powershell
python main.py
```

> L'application doit tourner avec **un seul worker** : l'index des commentaires est gardé en mémoire et n'est pas partagé entre plusieurs processus.

Le serveur est accessible localement à l'adresse :

http://127.0.0.1:8000

Pour vérifier son fonctionnement :

http://127.0.0.1:8000/health

Résultat attendu :

```json
{
    "status": "OK",
    "message": "Facebook Webhook is running"
}
```

## 7. Exposer le serveur avec ngrok

Facebook doit pouvoir accéder à ton serveur depuis Internet.

Dans un deuxième terminal PowerShell, exécute :

```powershell
ngrok http 8000
```

Ngrok génère une URL HTTPS publique, par exemple :

```text
https://abc123.ngrok-free.app
```

L'URL complète de ton webhook est alors :

```text
https://abc123.ngrok-free.app/webhook/facebook
```

**Attention :**
- garde les deux terminaux ouverts pendant les tests ;
- avec la version gratuite de ngrok, l'URL change à chaque redémarrage : il faut alors la mettre à jour dans Meta.

## 8. Configurer le webhook dans Meta

Dans ton application sur [Meta for Developers](https://developers.facebook.com) :

1. Ouvre **Webhooks** et choisis l'objet **Page**.
2. Clique sur **S'abonner à cet objet**, puis renseigne :
   - **URL de rappel** : `https://abc123.ngrok-free.app/webhook/facebook`
   - **Token de vérification** : la valeur de `FACEBOOK_VERIFY_TOKEN`
3. Valide : Facebook envoie une requête de vérification, et le serveur doit répondre correctement.
4. Abonne-toi au champ **`feed`** de l'objet Page.
5. Vérifie que ta Page est bien abonnée à l'application.

## 9. Vérifier le fonctionnement

Une fois le webhook configuré :

1. Publie une publication sur ta Page Facebook.
2. Ajoute un commentaire depuis un autre compte.
3. Vérifie les logs dans PowerShell.
4. Ouvre le fichier `data/facebook_comments.csv`.

Les commentaires reçus sont enregistrés automatiquement.

## 10. Format du fichier CSV

| Colonne | Description |
|---|---|
| `comment_id` | Identifiant unique du commentaire |
| `post_id` | Identifiant de la publication |
| `parent_id` | Identifiant du parent (publication ou commentaire auquel on répond) |
| `sender_id` | Identifiant de l'auteur |
| `sender_name` | Nom de l'auteur |
| `message` | Texte du commentaire |
| `status` | `active` ou `deleted` |
| `event_verb` | Dernier événement reçu : `add`, `edited` ou `remove` |
| `created_time` | Date de création (ISO 8601, UTC) |
| `updated_at` | Date de dernière mise à jour par le serveur (ISO 8601, UTC) |

Comportement à connaître :

- Un commentaire modifié est **mis à jour** (pas de doublon).
- Un commentaire supprimé reste dans le fichier avec `status = deleted`, et son dernier texte est conservé.
- Le fichier est encodé en UTF-8 avec BOM, pour que les accents s'affichent correctement dans Excel.
- Un texte commençant par `=`, `+`, `-` ou `@` est préfixé d'une apostrophe pour éviter l'exécution de formules dans Excel.

## 11. Limites

- Le webhook ne reçoit que les **nouveaux événements** après l'abonnement. Les commentaires publiés avant ne sont pas récupérés ; il faut pour cela interroger l'API Graph (`/{post-id}/comments`).
- Selon les paramètres de confidentialité et les permissions de l'application, certaines informations sur l'auteur (comme le nom) peuvent être absentes.

## 12. Arrêter l'application

Pour arrêter le serveur FastAPI ou ngrok :

```text
CTRL + C
```

## 13. Commandes récapitulatives

| Action | Commande |
|---|---|
| Créer l'environnement | `py -m venv .venv` |
| Activer l'environnement | `.\.venv\Scripts\Activate.ps1` |
| Installer les dépendances | `pip install -r requirements.txt` |
| Démarrer FastAPI | `uvicorn main:app --reload --host 0.0.0.0 --port 8000` |
| Démarrer ngrok | `ngrok http 8000` |