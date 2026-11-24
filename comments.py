"""Traitement des commentaires : récupération du texte puis enregistrement."""

import logging

from fastapi.concurrency import run_in_threadpool

from extractor import extract_comment_events
from graph import fetch_comment
from storage import save_message
from utils import to_iso, utc_now_iso

logger = logging.getLogger("facebook_webhook")


async def process_comments(payload: dict) -> None:
    """Pour chaque commentaire du payload, récupère son texte et l'enregistre."""
    for value in extract_comment_events(payload):
        try:
            await _process_one(value)
        except Exception:
            logger.exception("Échec du traitement du commentaire %s", value.get("comment_id"))


async def _process_one(value: dict) -> None:
    verb = value["verb"]
    comment_id = str(value["comment_id"])

    # Le texte est parfois déjà dans le payload ; sinon on le demande à l'API Graph.
    # Un commentaire supprimé n'est plus lisible : on n'interroge pas l'API.
    message = value.get("message")
    attachment = None

    if message is None and verb != "remove":
        details = await fetch_comment(comment_id)
        if details:
            message = details.get("message")
            attachment = details.get("attachment")

    sender = value.get("from") or {}

    record = {
        "comment_id": comment_id,
        "post_id": value.get("post_id"),
        "parent_id": value.get("parent_id"),
        "sender_id": sender.get("id"),
        "sender_name": sender.get("name"),
        "message": message,
        "attachment": attachment,
        "event_verb": verb,
        "created_time": to_iso(value.get("created_time")),
        "received_at": utc_now_iso(),
    }

    await run_in_threadpool(save_message, record)