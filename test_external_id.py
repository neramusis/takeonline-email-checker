import asyncio
import json
import logging
from logging.config import dictConfig

import click

import ms_api
from run import get_emails, process_email
from logger import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

DAYS_TO_CHECK_EMAIL = 30


async def run_external_id(external_id: str, save: int) -> None:
    access_token = await ms_api.get_access_token()
    order_id = str(external_id[:-3])
    emails = await get_emails(order_id, access_token, days=DAYS_TO_CHECK_EMAIL)
    for email in emails:
        logger.info(f"Processing email from date: `{email['receivedDateTime']}`")
        if save:
            with open(
                f"test/fixtures/{external_id}_{email['receivedDateTime']}.json",
                "w"
            ) as f:
                json.dump(email, f, indent=2)
        open_api_json = await process_email(order_id, email)
        logger.info(f"Response from openai: `{open_api_json}`.")


@click.command()
@click.option("--external_id", required=True)
@click.option("--save", required=False, type=int, default=0)
def main(external_id: str, save) -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_external_id(external_id, save))


if __name__ == "__main__":
    main()
