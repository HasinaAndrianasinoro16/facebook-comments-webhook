import logging
import threading

from config import DUMP_FILE

logger = logging.getLogger("facebook_webhook")

_lock = threading.Lock()


def init_storage() -> None:
    """Crée le dossier et le fichier .dmp s'ils n'existent pas."""
    DUMP_FILE.parent.mkdir(parents=True, exist_ok=True)
    DUMP_FILE.touch(exist_ok=True)


def dump_raw(raw_body: bytes) -> None:
    """Ajoute le corps de la requête, octet pour octet, à la fin du fichier.

    Chaque requête est suivie d'un saut de ligne qui sert uniquement de séparateur.
    """
    with _lock:
        with DUMP_FILE.open("ab") as file:
            file.write(raw_body)
            file.write(b"\n")

    logger.info("Requête enregistrée (%d octets)", len(raw_body))