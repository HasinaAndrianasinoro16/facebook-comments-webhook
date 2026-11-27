import logging
import time

import httpx

from config import GRAPH_API_VERSION, PAGE_ACCESS_TOKEN

logger = logging.getLogger("facebook_webhook")

GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
POST_FIELDS = "message"

# Une publication reçoit souvent plusieurs commentaires : on garde sa description en mémoire
POST_CACHE_TTL_SECONDS = 600
_post_cache: dict[str, tuple[float, dict]] = {}


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


async def _get(client: httpx.AsyncClient, path: str, params: dict, level=logging.WARNING):
    """GET sur l'API Graph. Renvoie les données, ou None en cas d'erreur."""
    response = await client.get(
        f"{GRAPH_URL}/{path}",
        params=params,
        # Le token passe par l'en-tête, jamais dans l'URL (donc jamais dans les logs)
        headers={"Authorization": f"Bearer {PAGE_ACCESS_TOKEN}"},
    )
    data = response.json()

    if response.status_code != 200 or "error" in data:
        error = data.get("error", {}) if isinstance(data, dict) else {}
        logger.log(
            level,
            "Graph API : erreur %s (code %s) pour %s",
            error.get("message"),
            error.get("code"),
            path,
        )
        return None

    return data


async def _find_post_in_page(client: httpx.AsyncClient, page_id: str, post_id: str):
    """Cherche la publication dans la liste des publications de la Page."""
    data = await _get(
        client,
        f"{page_id}/posts",
        {"fields": f"id,{POST_FIELDS}", "limit": 100},
    )

    for item in (data or {}).get("data", []):
        if item.get("id") == post_id:
            return item

    logger.warning("Publication %s introuvable dans %s/posts", post_id, page_id)
    return None


async def fetch_post(post_id: str | None) -> dict | None:
    """Récupère la description (message) d'une publication. Renvoie None en cas d'échec.

    Accès direct d'abord ; s'il est refusé, on passe par la liste des publications de la Page.
    """
    if not PAGE_ACCESS_TOKEN or not post_id:
        return None

    cached = _post_cache.get(post_id)
    if cached and time.monotonic() - cached[0] < POST_CACHE_TTL_SECONDS:
        return cached[1]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            details = await _get(client, post_id, {"fields": POST_FIELDS}, level=logging.INFO)

            # L'identifiant d'une publication a la forme "<ID_PAGE>_<ID_POST>"
            if details is None and "_" in post_id:
                details = await _find_post_in_page(client, post_id.split("_", 1)[0], post_id)

    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Graph API injoignable pour %s : %s", post_id, type(exc).__name__)
        return None

    # Seuls les succès sont gardés en mémoire : un échec sera retenté au commentaire suivant
    if details is not None:
        _post_cache[post_id] = (time.monotonic(), details)

    return details