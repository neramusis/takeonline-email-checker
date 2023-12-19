import copy

import utils

PROMPT_ = """
User
I will provide you an order id, an email subject and a body from online shop . Please answer two questions:
- pick status from:
        0 – payment confirmation;
        1 – order confirmation or order is ready to be shipped;
        2 – order shipped;
        3 – order cancelation;
        4 – client service response;
- find tracking id/number. If you find two or more tracking ids, format it as a list;

order_id: {order_id};
subject: {subject};
body: {email_text}.

Only answer in json, without any explanation. JSON example:
{{
  "status": 2,
  "tracking_id": "54321",
}}
or
{{
  "status": 2,
  "tracking_id": ["12345", "23341"],
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
