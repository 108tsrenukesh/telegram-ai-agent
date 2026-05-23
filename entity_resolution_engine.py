import json
import logging

from ai_router import generate_reply

logger = logging.getLogger(__name__)


def resolve_entities(message, pending_entities):

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

        response = generate_reply(prompt)

        parsed = json.loads(response)

        return parsed.get("resolved", [])

    except json.JSONDecodeError:

        logger.exception(
            "resolve_entities JSON parse failed "
            "[message=%s pending=%s]",
            message, pending_entities
        )

        return []

    except Exception:

        logger.exception(
            "resolve_entities failed "
            "[message=%s pending=%s]",
            message, pending_entities
        )

        return []
