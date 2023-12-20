import json
import logging
import re
from datetime import datetime

from bs4 import BeautifulSoup

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
    return "\n".join(elements)


def prepare_email_text(email_html: str) -> str:
    text = parse_html_file(email_html)
    return text[:MAX_EMAIL_TEXT_LENGTH]


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
