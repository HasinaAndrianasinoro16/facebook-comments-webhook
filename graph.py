"""Appels à l'API Graph de Meta."""

import logging

import httpx

from config import GRAPH_API_VERSION, PAGE_ACCESS_TOKEN

logger = logging.getLogger("facebook_webhook")

GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


async def fetch_comment(comment_id: str) -> dict | None:
    """Récupère le texte d'un commentaire. Renvoie None en cas d'échec."""
    if not PAGE_ACCESS_TOKEN:
        return None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{GRAPH_URL}/{comment_id}",
                params={"fields": "message,created_time,attachment"},
                # Le token passe par l'en-tête, jamais dans l'URL (donc jamais dans les logs)
                headers={"Authorization": f"Bearer {PAGE_ACCESS_TOKEN}"},
            )
        data = response.json()

    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Graph API injoignable pour %s : %s", comment_id, type(exc).__name__)
        return None

    if response.status_code != 200 or "error" in data:
        error = data.get("error", {}) if isinstance(data, dict) else {}
        logger.warning(
            "Graph API : erreur %s (code %s) pour le commentaire %s",
            error.get("message"),
            error.get("code"),
            comment_id,
        )
        return None

    return data