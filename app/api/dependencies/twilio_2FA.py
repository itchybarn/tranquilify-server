from twilio.rest import Client
from twilio.http.async_http_client import AsyncTwilioHttpClient
from app.core.config import settings

# create client, make it so client can be passed to routes as a DI
async def get_twilio_client() -> Client:
    http_client = AsyncTwilioHttpClient()

    client = Client(
        settings.TWILIO_SID,
        settings.TWILIO_CLIENT_SECRET,
        http_client=http_client
    )
    return client

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