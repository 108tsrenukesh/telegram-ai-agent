import json
import logging

from ai_router import generate_reply

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


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


def _validate_items(parsed):
    """
    Validate schema:
    {
        "items": ["str", ...]
    }
    Returns True if valid, False otherwise.
    """
    if not isinstance(parsed, dict):
        return False
    items = parsed.get("items")
    if not isinstance(items, list):
        return False
    if not all(isinstance(item, str) for item in items):
        return False
    return True


def extract_items_semantically(text):

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
- No markdown fences
- No explanation

Format:

{{
    "items": [
        "milk 2L",
        "chips",
        "baby medicine - with name"
    ]
}}

"""

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = generate_reply(prompt)
            cleaned = _strip_json_fences(response)
            parsed = json.loads(cleaned)

            if not _validate_items(parsed):
                logger.warning(
                    "extract_items_semantically schema invalid "
                    "[attempt=%d response=%s]",
                    attempt, cleaned[:200]
                )
                continue

            items = parsed.get("items", [])

            # Filter out empty strings
            return [item for item in items if item.strip()]

        except json.JSONDecodeError:

            logger.warning(
                "extract_items_semantically JSON parse failed "
                "[attempt=%d/%d response=%s]",
                attempt, MAX_RETRIES, response[:200]
            )

        except Exception:

            logger.exception(
                "extract_items_semantically unexpected error "
                "[attempt=%d/%d text=%s]",
                attempt, MAX_RETRIES, text
            )
            break

    logger.error(
        "extract_items_semantically failed after %d attempts "
        "— returning empty [text=%s]",
        MAX_RETRIES, text
    )

    return []
