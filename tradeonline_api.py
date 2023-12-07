import logging

import aiohttp

from config import Settings

logger = logging.getLogger(__name__)
GET_ENDPOINT = "https://admin.takeonline.eu/api/get_external_ids"
UPDATE_ENDPOINT = "https://admin.takeonline.eu/api/update_external_ids"


settings = Settings()


async def get_orders() -> dict:
    session = aiohttp.ClientSession()
    try:
        resp = await session.get(
            GET_ENDPOINT, headers={"auth-key": settings.takeonline_auth_key}
        )
        body = await resp.json()
        return body
    except Exception as exc:
        logger.error(f"An error while gathering external ids. `{exc}`.")
        raise exc
    finally:
        await session.close()


async def update_order(
    external_id: str,
    status: int,
    tracking_id: str | None = None,
) -> None:
    session = aiohttp.ClientSession()
    logger.info(
        f"Sending data to tradeonline API. External ID: `{external_id}`, status: "
        f"`{status}`, tracking_id: `{tracking_id}`."
    )
    data = {
        "external_id": external_id,
        "status": status,
    }
    if tracking_id:
        data.update({"tracking_id": tracking_id})
    try:
        resp = await session.post(
            UPDATE_ENDPOINT,
            json=[data],
            headers={"auth-key": settings.takeonline_auth_key},
        )
        body = await resp.text()
        logger.info(
            f"Response from tradeonline API. Status code: `{resp.status}`, "
            f"body: `{body}`.",
        )
    except Exception as exc:
        logger.error(f"Error while sending data to tradeonline API. Error: `{exc!r}`.")
    finally:
        await session.close()
