import logging
from datetime import datetime, timedelta

import aiohttp

logger = logging.getLogger(__name__)

endpoint = "https://graph.microsoft.com/v1.0/me/messages"


async def query_emails(order_id: str, access_token: str, days: int) -> list:
    session = aiohttp.ClientSession()
    params = {
        "$top": 10,
        "$select": "id, subject ,body, receivedDateTime",
        "$search": f'"{order_id}"',
    }
    try:
        resp = await session.get(
            endpoint,
            params=params,
            headers={"Authorization": "Bearer " + access_token},
        )
        body = await resp.json()
        twenty_four_hours_ago = datetime.utcnow() - timedelta(days=days)
        return [
            email
            for email in body.get("value", [])
            if datetime.fromisoformat(email["receivedDateTime"].rstrip("Z"))
            > twenty_four_hours_ago
        ]
    except Exception as exc:
        logger.error(f"Error while doing query to emails. `{exc}`.")
        return []
    finally:
        await session.close()
