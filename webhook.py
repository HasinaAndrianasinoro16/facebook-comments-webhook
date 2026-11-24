from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import PlainTextResponse

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
async def receive_webhook(request: Request):
    """Reçoit un événement de Facebook et l'enregistre tel quel dans le fichier .dmp."""
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    # Seules les requêtes réellement envoyées par Facebook sont conservées
    if not verify_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="Invalid Facebook signature")

    # Aucune lecture, aucun filtre, aucune modification du contenu
    await run_in_threadpool(dump_raw, raw_body)

    return {"status": "received"}