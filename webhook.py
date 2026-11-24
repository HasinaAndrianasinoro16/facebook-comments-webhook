"""Routes du webhook Facebook."""

import json

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import PlainTextResponse

from comments import process_comments
from security import verify_signature, verify_token
from storage import dump_raw

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
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """Enregistre la requête telle quelle, puis récupère le texte des commentaires."""
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    # Seules les requêtes réellement envoyées par Facebook sont conservées
    if not verify_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="Invalid Facebook signature")

    # 1. Dump brut : aucune lecture, aucun filtre, aucune modification
    await run_in_threadpool(dump_raw, raw_body)

    # 2. Récupération du texte des commentaires, après la réponse à Facebook
    try:
        payload = json.loads(raw_body)
    except ValueError:
        payload = None

    if payload:
        background_tasks.add_task(process_comments, payload)

    return {"status": "received"}