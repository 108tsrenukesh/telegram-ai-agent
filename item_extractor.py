import json

from ai_router import (
    generate_reply
)


def extract_items_semantically(
    text
):

    prompt = f"""

You are an item extraction engine.

Extract actionable task items.

Message:
{text}

Rules:
- Return ONLY actionable items
- Remove conversational text
- Normalize items
- Return ONLY valid JSON

Format:

{{
    "items": [
        "milk 2L",
        "chips",
        "baby medicine - with name"
    ]
}}

"""

    try:

        response = generate_reply(
            prompt
        )

        parsed = json.loads(
            response
        )

        return parsed.get(
            "items",
            []
        )

    except Exception:

        return []