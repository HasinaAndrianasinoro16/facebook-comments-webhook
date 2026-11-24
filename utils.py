"""Fonctions utilitaires."""

from datetime import datetime, timezone


def to_iso(timestamp) -> str | None:
    """Convertit un timestamp Unix (envoyé par Facebook) en date ISO 8601."""
    if timestamp is None:
        return None

    try:
        return datetime.fromtimestamp(int(timestamp), tz=timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError, OSError):
        return str(timestamp)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()