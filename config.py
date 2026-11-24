"""Configuration de l'application (lue depuis les variables d'environnement)."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

VERIFY_TOKEN = os.getenv("FACEBOOK_VERIFY_TOKEN", "")
APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")

# Token d'accès de la Page : sert à lire le texte des commentaires via l'API Graph
PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_TOKEN", "")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v27.0")

# Requêtes de Facebook enregistrées telles quelles (aucune modification)
DUMP_FILE = Path(os.getenv("DUMP_FILE", "data/facebook_webhook.dmp"))

# Commentaires avec leur texte (une ligne JSON par événement)
MESSAGES_FILE = Path(os.getenv("MESSAGES_FILE", "data/facebook_comments.jsonl"))

# Événements de commentaire pris en compte
ALLOWED_VERBS = {"add", "edited", "remove"}


def validate_config() -> None:
    """Vérifie la configuration au démarrage."""
    required = {
        "FACEBOOK_VERIFY_TOKEN": VERIFY_TOKEN,
        "FACEBOOK_APP_SECRET": APP_SECRET,
    }
    missing = [name for name, value in required.items() if not value]

    if missing:
        raise RuntimeError(
            f"Variables d'environnement manquantes : {', '.join(missing)}"
        )

    if not PAGE_ACCESS_TOKEN:
        logging.getLogger("facebook_webhook").warning(
            "FACEBOOK_PAGE_TOKEN absent : le texte des commentaires ne sera pas récupéré."
        )