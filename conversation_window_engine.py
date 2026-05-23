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
        # Remove opening fence (```json or ```)
        lines = lines[1:] if lines[0].startswith("```") else lines
        # Remove closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _validate_windows(parsed):
    """
    Validate schema:
    {
        "windows": [
            {"messages": ["str", ...]}
        ]
    }
    Returns True if valid, False otherwise.
    """
    if not isinstance(parsed, dict):
        return False
    windows = parsed.get("windows")
    if not isinstance(windows, list):
        return False
    for window in windows:
        if not isinstance(window, dict):
            return False
        msgs = window.get("messages")
        if not isinstance(msgs, list):
            return False
        if not all(isinstance(m, str) for m in msgs):
            return False
    return True


def build_conversation_windows(messages):

    prompt = f"""

You are a conversational cognition engine.

Your task:
Group Telegram messages into natural conversational windows.

Rules:
- Humans often send fragmented messages
- Merge semantically connected messages
- Separate unrelated intents
- Detect emotional continuity
- Detect corrections
- Detect follow-up thoughts
- Think like a human reading chat

Messages:
{json.dumps(messages, indent=2)}

Return ONLY valid JSON. No explanation. No markdown fences.

Format:

{{
    "windows": [
        {{
            "messages": [
                "msg1",
                "msg2"
            ]
        }}
    ]
}}

"""

    fallback = [{"messages": messages}]

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = generate_reply(prompt)
            cleaned = _strip_json_fences(response)
            parsed = json.loads(cleaned)

            if not _validate_windows(parsed):
                logger.warning(
                    "build_conversation_windows schema invalid "
                    "[attempt=%d response=%s]",
                    attempt, cleaned[:200]
                )
                continue

            return parsed.get("windows", fallback)

        except json.JSONDecodeError:

            logger.warning(
                "build_conversation_windows JSON parse failed "
                "[attempt=%d/%d response=%s]",
                attempt, MAX_RETRIES, response[:200]
            )

        except Exception:

            logger.exception(
                "build_conversation_windows unexpected error "
                "[attempt=%d/%d messages=%s]",
                attempt, MAX_RETRIES, messages
            )
            break

    logger.error(
        "build_conversation_windows failed after %d attempts "
        "— using fallback single window [messages=%s]",
        MAX_RETRIES, messages
    )

    return fallback
