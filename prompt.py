import copy

import utils

PROMPT_ = """
I will provide you an email subject and body from online shop. Please answer four questions:
- find order id;
- pick status from:
	0 – payment confirmation;
	1 – order confirmation;
	2 – shipped / ready for shippment;
	3 – order cancelation;
	4 – client service response;
- find tracking id if exists, which sometimes is in tracking URL as a query parameter or path. If you find two or more tracking ids, format it as a list;
- find tracking id if you can not find tracking id, then try to find tracking URL.

subject: {subject}
body: {email_text}

Only answer in json, without any explanation. JSON example:
{{
  "order_id": "12345",
  "status": 2,
  "tracking_id": "54321",
  "tracking_url": null
}}
or 
{{
  "order_id": "12345",
  "status": 2,
  "tracking_id": null,
  "tracking_url": "http://track.com/823901823984"
}}
or
{{
  "order_id": "12345",
  "status": 2,
  "tracking_id": ["12345", "23341"],
  "tracking_url": null
}}

"""


def get_prompt(email: dict) -> str:
    prompt_ = copy.deepcopy(PROMPT_)
    email_text = utils.prepare_email_text(email["body"]["content"])
    prompt_ = prompt_.format(subject=email["subject"], email_text=email_text)
    return prompt_
