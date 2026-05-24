import json
import logging

from ai_router import generate_reply
from config import LLM_MAX_RETRIES, LLM_LOG_TRUNCATE
from utils import strip_json_fences

logger = logging.getLogger(__name__)

VALID_STATUSES = {"COMPLETE", "PARTIAL", "MISSING_DETAILS"}



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

    for attempt in range(1, LLM_MAX_RETRIES + 1):

        try:

            response = generate_reply(prompt)
            cleaned = strip_json_fences(response)
            parsed = json.loads(cleaned)

            if not _validate_entities(parsed):
                logger.warning(
                    "extract_entities schema invalid "
                    "[attempt=%d response=%s]",
                    attempt, cleaned[:LLM_LOG_TRUNCATE]
                )
                continue

            return parsed.get("entities", [])

        except json.JSONDecodeError:

            logger.warning(
                "extract_entities JSON parse failed "
                "[attempt=%d/%d response=%s]",
                attempt, LLM_MAX_RETRIES, response[:LLM_LOG_TRUNCATE]
            )

        except Exception:

            logger.exception(
                "extract_entities unexpected error "
                "[attempt=%d/%d message=%s]",
                attempt, LLM_MAX_RETRIES, message
            )
            break

    logger.error(
        "extract_entities failed after %d attempts "
        "— returning empty [message=%s]",
        LLM_MAX_RETRIES, message
    )

    return []
