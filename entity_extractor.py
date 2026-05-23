import json
import logging

from ai_router import generate_reply

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

VALID_STATUSES = {"COMPLETE", "PARTIAL", "MISSING_DETAILS"}


def _strip_json_fences(text):
    """Strip markdown code fences LLMs sometimes wrap JSON in."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:] if lines[0].startswith("```") else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _validate_entities(parsed):
    """
    Validate schema:
    {
        "entities": [
            {"name": "str", "status": "MISSING_DETAILS|PARTIAL|COMPLETE"}
        ]
    }
    Returns True if valid, False otherwise.
    """
    if not isinstance(parsed, dict):
        return False
    entities = parsed.get("entities")
    if not isinstance(entities, list):
        return False
    for entity in entities:
        if not isinstance(entity, dict):
            return False
        if not isinstance(entity.get("name"), str):
            return False
        if entity.get("status") not in VALID_STATUSES:
            return False
    return True


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
- No markdown fences

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

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = generate_reply(prompt)
            cleaned = _strip_json_fences(response)
            parsed = json.loads(cleaned)

            if not _validate_entities(parsed):
                logger.warning(
                    "extract_entities schema invalid "
                    "[attempt=%d response=%s]",
                    attempt, cleaned[:200]
                )
                continue

            return parsed.get("entities", [])

        except json.JSONDecodeError:

            logger.warning(
                "extract_entities JSON parse failed "
                "[attempt=%d/%d response=%s]",
                attempt, MAX_RETRIES, response[:200]
            )

        except Exception:

            logger.exception(
                "extract_entities unexpected error "
                "[attempt=%d/%d message=%s]",
                attempt, MAX_RETRIES, message
            )
            break

    logger.error(
        "extract_entities failed after %d attempts "
        "— returning empty [message=%s]",
        MAX_RETRIES, message
    )

    return []
