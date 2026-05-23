import json

from ai_router import (
    generate_reply
)


def extract_entities(message):

    prompt = f"""

You are an entity extraction engine.

Your task:
Extract unresolved conversational entities.

Message:
{message}

Rules:
- Identify requests/tasks/entities
- Detect if details are missing
- Detect if partially complete
- Return ONLY valid JSON
- No explanations

Output format:

{{
    "entities": [
        {{
            "name": "...",
            "status": "MISSING_DETAILS"
        }}
    ]
}}

Statuses:
- COMPLETE
- PARTIAL
- MISSING_DETAILS

"""

    try:

        response = generate_reply(
            prompt
        )

        parsed = json.loads(
            response
        )

        return parsed.get(
            "entities",
            []
        )

    except Exception:

        return []