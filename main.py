import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import validate_config
from storage import store
from webhook import router as webhook_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_config()
    store.load()
    yield


app = FastAPI(title="Facebook Commentaire Webhook", lifespan=lifespan)
app.include_router(webhook_router)


@app.get("/health")
def health():
    return {"status": "OK", "message": "Facebook Webhook is running"}


if __name__ == "__main__":
    import uvicorn

    # Un seul worker : l'index en mémoire et le verrou ne sont pas partagés entre processus.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)