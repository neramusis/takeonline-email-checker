import copy
import logging

from openai import AsyncOpenAI

import config
import utils

logger = logging.getLogger(__name__)
settings = config.Settings()

PROMPT = """
I will provide you an email subject and body from online shop. Please answer three questions:
- find order id;
- pick status from:
	0 – payment confirmation;
	1 – order confirmation;
	2 – shipped / ready for shippment;
	3 – order cancelation;
	4 – client service response;
- find tracking id if exists, which sometimes is in tracking URL as a query parameter or path;

subject: {subject}
body: {email_text}

Only answer in json, without any explanation. JSON example:
{{
  "order_id": 12345,
  "status": 1,
  "tracking_id": 54321
}}

"""

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def get_openai_response(email: dict) -> str | None:
    prompt = copy.deepcopy(PROMPT)
    email_text = utils.prepare_email_text(email["body"]["content"])
    prompt = prompt.format(subject=email["subject"], email_text=email_text)
    response = await client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
    )
    if not response.choices:
        return None
    logger.info(f"OpenAI response: {response}.")
    return response.choices[0].message.content
