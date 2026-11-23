"""Routes du webhook Facebook."""

import json

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import PlainTextResponse

from extractor import extract_comments
from security import verify_signature, verify_token
from storage import store

router = APIRouter(prefix="/webhook/facebook", tags=["facebook"])


@router.get("")
def verify_webhook(
    mode: str = Query(default="", alias="hub.mode"),
    token: str = Query(default="", alias="hub.verify_token"),
    challenge: str = Query(default="", alias="hub.challenge"),
):
    """Vérification de l'URL par Facebook lors de l'abonnement."""
    if mode == "subscribe" and verify_token(token):
        return PlainTextResponse(content=challenge, status_code=200)

    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("")
async def receive_webhook(request: Request):
    """Réception des événements (nouveaux commentaires, modifications, suppressions)."""
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="Invalid Facebook signature")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if payload.get("object") != "page":
        return {"status": "ignored"}

    records = list(extract_comments(payload))

    if records:
        # Écriture disque hors de la boucle asyncio pour ne pas la bloquer
        await run_in_threadpool(store.upsert_many, records)

    return {"status": "received", "processed": len(records)}
