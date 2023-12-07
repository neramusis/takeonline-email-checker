import asyncio
import logging
from logging.config import dictConfig

import click

import database
import email_api
import ms_api
import openai_api
import prompt
import utils
from logger import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


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


async def run_batch(external_id: str) -> None:
    access_token = await ms_api.get_access_token()
    order_id = str(external_id[:-3])
    emails = await _get_emails(order_id, access_token)
    for email in emails:
        prompt_text = prompt.get_prompt(email)
        with open(
            f"test/fixtures/{external_id}_{email['receivedDateTime']}.txt", "w"
        ) as f:
            f.write(prompt_text)
        open_api_json = await _process_email(external_id, prompt_text)
        logger.info(f"Response from openai: `{open_api_json}`.")


@click.command()
@click.option("--external_id", required=True)
def main(external_id: str) -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_batch(external_id))


if __name__ == "__main__":
    main()
