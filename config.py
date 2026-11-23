import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

VERIFY_TOKEN = os.getenv("FACEBOOK_VERIFY_TOKEN", "")
APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")

# Optionnel : satria m'vise post iray manokana mihitsy sinon rah vide dia izy rht zany no alaina
TARGET_POST_ID = os.getenv("FACEBOOK_POST_ID", "").strip()

DATA_FILE = Path(os.getenv("COMMENTS_CSV", "data/facebook_comments.csv"))

CSV_FIELDNAMES = [
    "comment_id",
    "post_id",
    "parent_id",
    "sender_id",
    "sender_name",
    "message",
    "status",
    "event_verb",
    "created_time",
    "updated_at",
]

# event fb izay pris en compte
ALLOWED_VERBS = {"add", "edited", "remove"}


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
