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


def _validate_resolved(parsed, pending_entities):
    """
    Validate schema:
    {
        "resolved": ["entity_name", ...]
    }
    - must be a dict
    - "resolved" must be a list of strings
    - each resolved item must be in pending_entities
    Returns True if valid, False otherwise.
    """
    if not isinstance(parsed, dict):
        return False
    resolved = parsed.get("resolved")
    if not isinstance(resolved, list):
        return False
    if not all(isinstance(r, str) for r in resolved):
        return False
    # Warn (not fail) if LLM hallucinates entities not in pending list
    hallucinated = [r for r in resolved if r not in pending_entities]
    if hallucinated:
        logger.warning(
            "resolve_entities: LLM returned entities not in pending list "
            "[hallucinated=%s pending=%s]",
            hallucinated, pending_entities
        )
    return True


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
- No markdown fences
- Only return entities from the pending list

Format:

{{
    "resolved": [
        "vegetables"
    ]
}}

"""

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = generate_reply(prompt)
            cleaned = _strip_json_fences(response)
            parsed = json.loads(cleaned)

            if not _validate_resolved(parsed, pending_entities):
                logger.warning(
                    "resolve_entities schema invalid "
                    "[attempt=%d response=%s]",
                    attempt, cleaned[:200]
                )
                continue

            # Filter to only entities actually in the pending list
            resolved = parsed.get("resolved", [])
            safe_resolved = [r for r in resolved if r in pending_entities]

            return safe_resolved

        except json.JSONDecodeError:

            logger.warning(
                "resolve_entities JSON parse failed "
                "[attempt=%d/%d response=%s]",
                attempt, MAX_RETRIES, response[:200]
            )

        except Exception:

            logger.exception(
                "resolve_entities unexpected error "
                "[attempt=%d/%d message=%s]",
                attempt, MAX_RETRIES, message
            )
            break

    logger.error(
        "resolve_entities failed after %d attempts "
        "— returning empty [message=%s pending=%s]",
        MAX_RETRIES, message, pending_entities
    )

    return []
