import copy

import utils

PROMPT_ = """
User
I will provide you an order_id, an email subject and a body from online shop . Please answer two questions:
- pick status from:
        0 – payment confirmation;
        1 – order confirmation or order is ready to be shipped;
        2 – order shipped;
        3 – order cancelation;
        4 – client service response;
- find tracking id/number. If you find two or more tracking ids/numbers, format it as a list. Consider these rules when picking tracking id/number:
  - tracking id/number can also be named as 'sent package number';
  - tracking id/number can also be named as 'shipment number';
  - tracking id/number should NOT be a number which you provide for delivery man for security;
  - tracking id/number should NOT be the same as provided order_id;
  - tracking id/number should NOT be a words about tracking link. It must be an ID or a number;
  - tracking id/number should NOT be words like 'SEGUI LA SPEDIZIONE'.

order_id: {order_id};
subject: {subject};
body: {email_text}.

Only answer in JSON, without any explanation. Copy tracking URL from provided body. JSON example:
{{
  "status": 2,
  "tracking_id": "TW 54321384923",
}}
or
{{
  "status": 2,
  "tracking_id": "227798I047590",
}}
or
{{
  "status": 2,
  "tracking_id": ["227798I047590", "227798I047591"],
}}

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
