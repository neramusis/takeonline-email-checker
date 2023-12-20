import json
import logging
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import prompt
import openai_api

logger = logging.getLogger(__name__)
MAX_EMAIL_TEXT_LENGTH = 3000


def parse_order_id(external_id: str) -> str:
    return external_id[:-3]


def parse_html_file(email_html: str) -> str:
    soup = BeautifulSoup(email_html, "lxml")
    elements = []
    for element in soup.find_all():
        if not any(child for child in element.children if child.name is not None):
            if element.name in ("script", "style"):
                continue
            text = element.get_text(strip=True)
            if text:
                elements.append(text)
            url = element.get('href')
            if url:
                elements.append(url)
    return "\n".join(elements)


def prepare_email_text(email_html: str) -> str:
    text = parse_html_file(email_html)
    return text[:MAX_EMAIL_TEXT_LENGTH]


def parse_tracking_id(text: str) -> str | None:
    cleaned_text = re.sub(r'^```json|```|"""', "", text, flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned_text)
        if "tracking_id" not in data:
            data["tracking_id"] = None
            logger.warning(
                f"'tracking_id' is not in openai api JSON response. "
                f"Full response: `{data}`.",
            )
        return data["tracking_id"]
    except json.JSONDecodeError as exc:
        logger.error(f"Can't parse json. Text value: `{text}`. Error: `{exc!r}`.")
        return None


async def _get_tracking_id_from_url(url: str) -> str | None:
    logger.info(f"Getting tracking URL: `{url}`.")
    try:
        resp = requests.get(url, allow_redirects=True)
        logger.info(f"URL request responded with status: `{resp.status_code}`.")
        if resp.status_code != 200:
            return None
        html = resp.text
        if not html:
            return None
        prompt_text = prompt.get_html_prompt(html)
        openai_resp_text = await openai_api.get_openai_response(prompt_text)
        return parse_tracking_id(openai_resp_text)
    except Exception as exc:
        logger.error(
            f"Error while getting track id from url. URL: `{url}`, "
            f"error: `{exc!r}`."
        )


async def parse_order_json(text: str) -> dict:
    """Parse JSON from openai api response."""
    cleaned_text = re.sub(r'^```json|```|"""', "", text, flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned_text)
        if "status" not in data:
            data["status"] = None
            logger.warning(
                f"'status' is not in openai api JSON response. "
                f"Full response: `{data}`.",
            )
        if "tracking_id" not in data:
            data["tracking_id"] = None
            logger.warning(
                f"'tracking_id' is not in openai api JSON response. "
                f"Full response: `{data}`.",
            )
        if data.get("tracking_url") and not data["tracking_id"]:
            data["tracking_id"] = await _get_tracking_id_from_url(data["tracking_url"])
        return data
    except json.JSONDecodeError as exc:
        logger.error(f"Can't parse json. Text value: `{text}`. Error: `{exc!r}`.")
        return {
            "status": None,
            "tracking_id": None,
        }


def convert_iso_to_mysql_datetime(iso_datetime_str: str) -> str:
    iso_datetime_str = re.sub(r"Z$", "", iso_datetime_str)
    dt = datetime.fromisoformat(iso_datetime_str)
    mysql_datetime_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    return mysql_datetime_str
