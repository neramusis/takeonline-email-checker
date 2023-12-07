import json
import logging
import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup, Comment

logger = logging.getLogger(__name__)
MAX_EMAIL_TEXT_LENGTH = 3000


def parse_order_id(external_id: str) -> str:
    return external_id[:-3]


def parse_html_file(email_html):
    soup = BeautifulSoup(email_html, "lxml")
    text = soup.get_text(separator="\n", strip=True)
    return text


def prepare_email_text(email_html: str) -> str:
    text = parse_html_file(email_html)
    return text[:MAX_EMAIL_TEXT_LENGTH]


def parse_json(text: str) -> dict | None:
    cleaned_text = re.sub(r'^```json|```|"""', "", text, flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned_text)
        keys_to_check = ["order_id", "status", "tracking_id"]
        if all(key in data for key in keys_to_check):
            return data
        logger.error(
            f"Parsed response from openai does not contain all keys. "
            f"Parsed data: `{data}`."
        )
        return None
    except json.JSONDecodeError as exc:
        logger.error(f"Can't parse json. Text value: `{text}`. Error: `{exc!r}`.")
        return None


def convert_iso_to_mysql_datetime(iso_datetime_str: str) -> str:
    iso_datetime_str = re.sub(r"Z$", "", iso_datetime_str)
    dt = datetime.fromisoformat(iso_datetime_str)
    mysql_datetime_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    return mysql_datetime_str
