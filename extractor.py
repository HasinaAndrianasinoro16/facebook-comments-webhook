from typing import Iterator

from config import ALLOWED_VERBS, TARGET_POST_ID
from utils import csv_safe, to_iso, utc_now_iso


def extract_comments(payload: dict) -> Iterator[dict]:
    """Parcourt le payload et produit des enregistrements prêts à stocker."""
    now = utc_now_iso()

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):

            if change.get("field") != "feed":
                continue

            value = change.get("value") or {}
            verb = value.get("verb", "")

            if value.get("item") != "comment" or verb not in ALLOWED_VERBS:
                continue

            comment_id = value.get("comment_id")
            if not comment_id:
                continue

            post_id = value.get("post_id")
            if TARGET_POST_ID and post_id != TARGET_POST_ID:
                continue

            sender = value.get("from") or {}

            yield {
                "comment_id": str(comment_id),
                "post_id": post_id,
                "parent_id": value.get("parent_id"),
                "sender_id": sender.get("id"),
                "sender_name": csv_safe(sender.get("name")),
                "message": csv_safe(value.get("message")),
                "status": "deleted" if verb == "remove" else "active",
                "event_verb": verb,
                "created_time": to_iso(value.get("created_time")),
                "updated_at": now,
            }
