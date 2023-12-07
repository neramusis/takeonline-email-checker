import asyncio
import json
import logging
import time
from logging.config import dictConfig

import database
import email_api
import ms_api
import openai_api
import tradeonline_api
import utils
from logger import LOGGING_CONFIG

PROMPT = """
I will provide you an email subject and body from online shop. Please answer three questions:
- find order id;
- pick status from:
	0 – payment confirmation;
	1 – order confirmation;
	2 – shipped / ready for shippment;
	3 – order cancelation;
	4 – client service response;
- find tracking id if exists, which sometimes is in tracking URL as a query parameter or path. If you find two or more tracking ids, format it as a list;
- if you can not find tracking id, then try to find tracking URL.

subject: {subject}
body: {email_text}

Only answer in json, without any explanation. JSON example:
{{
  "order_id": "12345",
  "status": 2,
  "tracking_id": "54321",
  "tracking_url": null
}}
or 
{{
  "order_id": "12345",
  "status": 2,
  "tracking_id": null,
  "tracking_url": "http://track.com/823901823984"
}}
or
{{
  "order_id": "12345",
  "status": 2,
  "tracking_id": ["12345", "23341"],
  "tracking_url": null
}}

"""

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


async def _get_emails(order_id: str, access_token: str) -> list:
    logger.info(f"Querying emails API with order ID: `{order_id}`.")
    emails = await email_api.query_emails(
        access_token=access_token,
        order_id=order_id,
    )
    return emails


async def _process_email(external_id: str, email: dict) -> dict | None:
    logger.info("Checking if email needs processing.")
    if database.check_email_exists(email["id"]):
        logger.info("Email already checked. Skipping.")
        return
    logger.info(
        f"Processing email with receive date: `{email['receivedDateTime']}`.",
    )
    open_api_response = await openai_api.get_openai_response(email)
    open_api_json = utils.parse_json(open_api_response)
    logger.info(
        f"External id: `{external_id}`, response from openai: " f"`{open_api_json}`.",
    )
    return open_api_json


async def run_batch(external_id: str | None = None) -> None:
    if not external_id:
        external_ids = await tradeonline_api.get_orders()
        unique_external_ids = set()
        for sub_dict in external_ids.values():
            unique_external_ids.update(sub_dict.keys())
        unique_external_ids = list(unique_external_ids)
    else:
        unique_external_ids = [external_id]
    logger.info(f"Unique external ids to check count: `{len(unique_external_ids)}`.")
    access_token = await ms_api.get_access_token()
    for nr, external_id in enumerate(unique_external_ids):
        order_id = str(external_id[:-3])
        emails = await _get_emails(order_id, access_token)
        logger.info(
            f"External id nr: `{nr}`, external id: `{external_id}`,"
            f" emails found: `{len(emails)}`.",
        )
        for email in emails:
            open_api_json = await _process_email(external_id, email)
            if (
                open_api_json
                and str(open_api_json["order_id"]).replace(" ", "") == order_id
            ):
                database.store_response(
                    order_id=order_id,
                    open_api_json=open_api_json,
                    external_id=external_id,
                    email_date=utils.convert_iso_to_mysql_datetime(
                        email["receivedDateTime"]
                    ),
                    email_id=email["id"],
                )
                await tradeonline_api.update_order(
                    external_id=external_id,
                    status=open_api_json["status"],
                    tracking_id=open_api_json["tracking_id"],
                )


def main() -> None:
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(run_batch())
        time.sleep(3600)


if __name__ == "__main__":
    main()
