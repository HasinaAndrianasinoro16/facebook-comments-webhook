import csv
import logging
import os
import tempfile
import threading
from pathlib import Path

from config import CSV_FIELDNAMES, DATA_FILE

logger = logging.getLogger("facebook_webhook")


class CommentStore:

    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()
        self._comments: dict[str, dict] = {}

    def load(self) -> None:
        """Charge le CSV existant, ou le crée avec son en-tête."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self._write_all()
            return

        with self.path.open("r", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                if row.get("comment_id"):
                    self._comments[row["comment_id"]] = row

        logger.info(
            "%d commentaire(s) chargé(s) depuis %s", len(self._comments), self.path
        )

    def upsert_many(self, records: list[dict]) -> None:
        """Ajoute ou met à jour des commentaires en un seul passage."""
        with self._lock:
            new_rows: list[dict] = []
            needs_rewrite = False

            for record in records:
                comment_id = record["comment_id"]
                existing = self._comments.get(comment_id)

                if existing is None:
                    self._comments[comment_id] = record
                    new_rows.append(record)
                    continue

                # On ne remplace que les valeurs réellement fournies
                # (un événement "remove" n'a pas de message : on garde l'ancien).
                merged = {
                    **existing,
                    **{k: v for k, v in record.items() if v not in (None, "")},
                }

                has_changed = any(
                    merged.get(key) != existing.get(key)
                    for key in CSV_FIELDNAMES
                    if key != "updated_at"
                )

                if has_changed:
                    self._comments[comment_id] = merged
                    needs_rewrite = True

            if needs_rewrite:
                self._write_all()
            elif new_rows:
                self._append(new_rows)

        logger.info("%d événement(s) traité(s)", len(records))

    def _append(self, rows: list[dict]) -> None:
        """Ajoute des lignes à la fin du fichier (rapide)."""
        with self.path.open("a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=CSV_FIELDNAMES, extrasaction="ignore"
            )
            writer.writerows(rows)

    def _write_all(self) -> None:
        """Réécriture atomique : fichier temporaire puis remplacement."""
        fd, tmp_name = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")

        try:
            # utf-8-sig : pour que Excel affiche correctement les accents
            with os.fdopen(fd, "w", encoding="utf-8-sig", newline="") as file:
                writer = csv.DictWriter(
                    file, fieldnames=CSV_FIELDNAMES, extrasaction="ignore"
                )
                writer.writeheader()
                writer.writerows(self._comments.values())

            os.replace(tmp_name, self.path)

        except Exception:
            Path(tmp_name).unlink(missing_ok=True)
            raise


# Instance unique utilisée dans toute l'application
store = CommentStore(DATA_FILE)
