import asyncio
import logging
import time
from logging.config import dictConfig

import database
import email_api
import ms_api
import openai_api
import prompt
import store
import tradeonline_api
import utils
from logger import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

TIME_BETWEEN_RUNS = 3600


async def get_emails(order_id: str, access_token: str, days: int = 1) -> list:
    logger.info(f"Querying emails API with order ID: `{order_id}`.")
    emails = await email_api.query_emails(
        access_token=access_token,
        order_id=order_id,
        days=days,
    )
    return emails


async def process_email(order_id: str, email: dict) -> dict:
    prompt_text = prompt.get_prompt(email, order_id=order_id)
    open_api_response = await openai_api.get_openai_response(prompt_text)
    open_api_json = await utils.parse_order_json(open_api_response)
    return open_api_json


async def run_batch() -> None:
    external_ids = await tradeonline_api.get_orders()
    unique_external_ids = set()
    for sub_dict in external_ids.values():
        unique_external_ids.update(sub_dict.keys())
    unique_external_ids = list(unique_external_ids)
    logger.info(f"Unique external ids to check count: `{len(unique_external_ids)}`.")
    access_token = await ms_api.get_access_token()
    for nr, external_id in enumerate(unique_external_ids):
        order_id = str(external_id[:-3])
        emails = await get_emails(order_id, access_token)
        logger.info(
            f"External id nr: `{nr}`, external id: `{external_id}`,"
            f" emails found: `{len(emails)}`.",
        )
        emails.reverse()
        for email in emails:
            logger.info("Checking if email needs processing.")
            if database.check_email_exists(email["id"]):
                logger.info("Email already checked. Skipping.")
                continue
            logger.info(
                f"Processing email with receive date: `{email['receivedDateTime']}`.",
            )
            open_api_json = await process_email(order_id, email)
            await store.store_response(
                open_api_json=open_api_json,
                external_id=external_id,
                email_date=utils.convert_iso_to_mysql_datetime(
                    email["receivedDateTime"]
                ),
                email_id=email["id"],
            )


def main() -> None:
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(run_batch())
        time.sleep(TIME_BETWEEN_RUNS)


if __name__ == "__main__":
    main()
