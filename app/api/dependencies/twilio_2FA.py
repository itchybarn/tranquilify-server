from twilio.rest import Client
from twilio.http.async_http_client import AsyncTwilioHttpClient
from app.core.config import settings

# A single client (and its underlying async HTTP connection pool) is reused across
# requests instead of building a new one every call, which previously leaked connections.
_twilio_client: Client | None = None

# create client, make it so client can be passed to routes as a DI
async def get_twilio_client() -> Client:
    global _twilio_client
    if _twilio_client is None:
        http_client = AsyncTwilioHttpClient()
        _twilio_client = Client(
            settings.TWILIO_SID,
            settings.TWILIO_CLIENT_SECRET,
            http_client=http_client
        )
    return _twilio_client

async def close_twilio_client() -> None:
    global _twilio_client
    if _twilio_client is None:
        return
    # Best-effort close of the underlying httpx.AsyncClient. Its exact attribute path
    # is twilio-version dependent, so resolve it defensively and never fail shutdown.
    http_client = getattr(_twilio_client, "http_client", None)
    inner = getattr(http_client, "client", None)
    aclose = getattr(inner, "aclose", None)
    if aclose is not None:
        try:
            await aclose()
        except Exception:
            pass
    _twilio_client = None

async def send_verification(twilio_client: Client, destination: str, channel: str):
    verification = await twilio_client.verify.v2.services(
        settings.TRANQUILIFY_SERVICE_SID
    ).verifications.create_async(to=destination, channel=channel)
    return verification.status

async def check_verification(twilio_client: Client, destination: str, code: str):
    verification_check = await twilio_client.verify.v2.services(
        settings.TRANQUILIFY_SERVICE_SID
    ).verifications_checks.create_async(to=destination, code=code)
    return verification_check.status