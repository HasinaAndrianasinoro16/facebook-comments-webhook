"""Extraction des événements de commentaire depuis le payload de Facebook."""

from typing import Iterator

from config import ALLOWED_VERBS


def extract_comment_events(payload) -> Iterator[dict]:
    """Produit les `value` des événements de commentaire (ajout, modification, suppression)."""
    if not isinstance(payload, dict):
        return

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):

            if change.get("field") != "feed":
                continue

            value = change.get("value") or {}

            if value.get("item") != "comment":
                continue

            if value.get("verb") not in ALLOWED_VERBS:
                continue

            if not value.get("comment_id"):
                continue

            yield value