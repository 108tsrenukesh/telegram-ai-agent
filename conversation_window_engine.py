import json
import logging

from ai_router import generate_reply
from config import LLM_MAX_RETRIES, LLM_LOG_TRUNCATE
from utils import strip_json_fences

logger = logging.getLogger(__name__)


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

    for attempt in range(1, LLM_MAX_RETRIES + 1):

        try:

            response = generate_reply(prompt)
            cleaned = strip_json_fences(response)
            parsed = json.loads(cleaned)

            if not _validate_windows(parsed):
                logger.warning(
                    "build_conversation_windows schema invalid "
                    "[attempt=%d response=%s]",
                    attempt, cleaned[:LLM_LOG_TRUNCATE]
                )
                continue

            return parsed.get("windows", fallback)

        except json.JSONDecodeError:

            logger.warning(
                "build_conversation_windows JSON parse failed "
                "[attempt=%d/%d response=%s]",
                attempt, LLM_MAX_RETRIES, response[:LLM_LOG_TRUNCATE]
            )

        except Exception:

            logger.exception(
                "build_conversation_windows unexpected error "
                "[attempt=%d/%d messages=%s]",
                attempt, LLM_MAX_RETRIES, messages
            )
            break

    logger.error(
        "build_conversation_windows failed after %d attempts "
        "— using fallback single window [messages=%s]",
        LLM_MAX_RETRIES, messages
    )

    return fallback
