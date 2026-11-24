import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

VERIFY_TOKEN = os.getenv("FACEBOOK_VERIFY_TOKEN", "")
APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")

# Fichier dans lequel les requêtes de Facebook sont enregistrées telles quelles
DUMP_FILE = Path(os.getenv("DUMP_FILE", "data/facebook_webhook.dmp"))


def validate_config() -> None:
    """Lève une erreur au démarrage si une variable obligatoire est absente."""
    required = {
        "FACEBOOK_VERIFY_TOKEN": VERIFY_TOKEN,
        "FACEBOOK_APP_SECRET": APP_SECRET,
    }
    missing = [name for name, value in required.items() if not value]

    if missing:
        raise RuntimeError(
            f"Variables d'environnement manquantes : {', '.join(missing)}"
        )