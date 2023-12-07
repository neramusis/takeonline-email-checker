import asyncio
import logging
import time
from logging.config import dictConfig

import database
import email_api
import ms_api
import openai_api
import prompt
import tradeonline_api
import utils
from logger import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

TIME_BETWEEN_RUNS = 3600


async def _get_emails(order_id: str, access_token: str) -> list:
    logger.info(f"Querying emails API with order ID: `{order_id}`.")
    emails = await email_api.query_emails(
        access_token=access_token,
        order_id=order_id,
    )
    return emails


async def _process_email(external_id: str, prompt_text: str) -> dict | None:
    open_api_response = await openai_api.get_openai_response(prompt_text)
    open_api_json = utils.parse_json(open_api_response)
    logger.info(
        f"External id: `{external_id}`, response from openai: " f"`{open_api_json}`.",
    )
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
        emails = await _get_emails(order_id, access_token)
        logger.info(
            f"External id nr: `{nr}`, external id: `{external_id}`,"
            f" emails found: `{len(emails)}`.",
        )
        for email in emails:
            logger.info("Checking if email needs processing.")
            if database.check_email_exists(email["id"]):
                logger.info("Email already checked. Skipping.")
                continue
            logger.info(
                f"Processing email with receive date: `{email['receivedDateTime']}`.",
            )
            prompt_text = prompt.get_prompt(email)
            open_api_json = await _process_email(external_id, prompt_text)
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
        time.sleep(TIME_BETWEEN_RUNS)


if __name__ == "__main__":
    main()
