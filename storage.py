"""Fichiers de stockage : dump brut (.dmp) et commentaires avec leur texte (.jsonl)."""

import json
import logging
import threading

from config import DUMP_FILE, MESSAGES_FILE

logger = logging.getLogger("facebook_webhook")

_lock = threading.Lock()


def init_storage() -> None:
    """Crée les dossiers et les fichiers s'ils n'existent pas."""
    for path in (DUMP_FILE, MESSAGES_FILE):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)


def dump_raw(raw_body: bytes) -> None:
    """Ajoute le corps de la requête, octet pour octet, à la fin du fichier .dmp.

    Chaque requête est suivie d'un saut de ligne qui sert uniquement de séparateur.
    """
    with _lock:
        with DUMP_FILE.open("ab") as file:
            file.write(raw_body)
            file.write(b"\n")

    logger.info("Requête enregistrée (%d octets)", len(raw_body))


def save_message(record: dict) -> None:
    """Ajoute un commentaire (avec son texte) au fichier .jsonl, une ligne par événement."""
    line = json.dumps(record, ensure_ascii=False)

    with _lock:
        with MESSAGES_FILE.open("a", encoding="utf-8") as file:
            file.write(line + "\n")