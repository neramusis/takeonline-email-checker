import copy

import utils

PROMPT_ = """
User
I will provide you an order id, an email subject and a body from online shop . Please answer three questions:
- pick status from:
        0 – payment confirmation;
        1 – order confirmation or order is ready to be shipped;
        2 – order shipped;
        3 – order cancelation;
        4 – client service response;
- find tracking id/number. If you find two or more tracking ids, format it as a list;
- find tracking URL if exists.;

order_id: {order_id};
subject: {subject};
body: {email_text}.

Only answer in JSON, without any explanation. Copy tracking URL from provided body. JSON example:
{{
  "status": 2,
  "tracking_id": "54321",
  "tracking_url": null
}}
or
{{
  "status": 2,
  "tracking_id": ["12345", "23341"],
  "tracking_url": null
}}

"""

HTML_PROMPT_ = """
I will provide you a text which is from items delivery page. Find from provided text:
- tracking id.

text: {text}

Only answer in json, without any explanation. JSON example:
{{
    "tracking_id": "202391023"
}}
or
{{
    "tracking_id": null
}}
null is set when you can not find tracking id.
"""


def get_prompt(email: dict, order_id: str) -> str:
    prompt_ = copy.deepcopy(PROMPT_)
    email_text = utils.prepare_email_text(email["body"]["content"])
    prompt_ = prompt_.format(
        subject=email["subject"],
        email_text=email_text,
        order_id=order_id,
    )
    return prompt_


def get_html_prompt(html: str) -> str:
    prompt_ = copy.deepcopy(HTML_PROMPT_)
    text = utils.parse_html_file(html)
    prompt_ = prompt_.format(text=text)
    return prompt_
