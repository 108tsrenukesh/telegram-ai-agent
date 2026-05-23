import json

from ai_router import (
    generate_reply
)


def resolve_entities(

    message,
    pending_entities

):

    prompt = f"""

You are an entity resolution engine.

Pending entities:
{json.dumps(pending_entities)}

Incoming message:
{message}

Determine which entities are now resolved.

Rules:
- Think conversationally
- Detect completed clarifications
- Detect partial completion
- Return ONLY valid JSON

Format:

{{
    "resolved": [
        "vegetables"
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
            "resolved",
            []
        )

    except Exception:

        return []