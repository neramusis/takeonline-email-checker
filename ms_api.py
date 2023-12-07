import logging

import aiohttp

from config import Settings

logger = logging.getLogger(__name__)

settings = Settings()

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "*/*",
}
ENDPOINT = f"https://login.microsoftonline.com/{settings.tenant_id}/oauth2/v2.0/token"
params = {
    "client_id": settings.client_id,
    "scope": "offline_access Mail.ReadWrite Mail.send",
    "grant_type": "refresh_token",
    "client_secret": settings.client_secret,
    "refresh_token": settings.refresh_token,
}


async def get_access_token() -> str:
    session = aiohttp.ClientSession()
    try:
        resp = await session.post(ENDPOINT, data=params, headers=HEADERS)
        body = await resp.json()
        return body["access_token"]
    except Exception as exc:
        logger.error(f"Error while getting access token: `{exc}`.")
        raise exc
    finally:
        await session.close()
