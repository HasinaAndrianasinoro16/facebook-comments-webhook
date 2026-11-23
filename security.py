import hashlib
import hmac

from config import APP_SECRET, VERIFY_TOKEN


def verify_token(token: str) -> bool:
    """Compare le token reçu avec celui configuré (temps constant)."""
    return hmac.compare_digest(
        token.encode("utf-8"),
        VERIFY_TOKEN.encode("utf-8"),
    )


def verify_signature(raw_body: bytes, signature: str) -> bool:
    """Vérifie l'en-tête X-Hub-Signature-256 envoyé par Facebook."""
    if not APP_SECRET or not signature:
        return False

    algorithm, separator, received = signature.partition("=")

    if algorithm != "sha256" or not separator:
        return False

    expected = hmac.new(
        APP_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    # encode() évite un TypeError si l'en-tête contient des caractères non ASCII
    return hmac.compare_digest(
        expected.encode("utf-8"),
        received.encode("utf-8"),
    )
