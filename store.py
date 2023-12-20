import logging

import tradeonline_api
from database import store_order_stats


logger = logging.getLogger(__name__)


async def store_response(
    open_api_json: dict,
    external_id: str,
    email_date: str,
    email_id: str,
) -> None:
    try:
        logger.info(f"Store for order id: `{external_id}`.")
        if isinstance(open_api_json["tracking_id"], list):
            for tracking_id in open_api_json["tracking_id"]:
                store_order_stats(
                    external_id=external_id,
                    email_date=email_date,
                    email_id=email_id,
                    status=open_api_json["status"],
                    tracking_id=str(tracking_id),
                )
                if open_api_json["status"]:
                    await tradeonline_api.update_order(
                        external_id=external_id,
                        status=open_api_json["status"],
                        tracking_id=open_api_json["tracking_id"],
                    )
        else:
            store_order_stats(
                external_id=external_id,
                email_date=email_date,
                email_id=email_id,
                status=open_api_json["status"],
                tracking_id=(
                    str(open_api_json["tracking_id"])
                    if open_api_json["tracking_id"]
                    else None
                ),
            )
            if open_api_json["status"]:
                await tradeonline_api.update_order(
                    external_id=external_id,
                    status=open_api_json["status"],
                    tracking_id=open_api_json["tracking_id"],
                )
    except Exception as exc:
        logger.error(f"Error storing order stats. Error: `{exc!r}`.")
