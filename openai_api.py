import copy
import logging

from openai import AsyncOpenAI

import config
import utils

logger = logging.getLogger(__name__)
settings = config.Settings()


client = AsyncOpenAI(api_key=settings.openai_api_key)


async def get_openai_response(prompt_text: str) -> str | None:
    response = await client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt_text}],
    )
    if not response.choices:
        return None
    logger.info(f"OpenAI response: {response}.")
    return response.choices[0].message.content
