import json
import logging

from ai_router import generate_reply

logger = logging.getLogger(__name__)


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

Return ONLY valid JSON.

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

    try:

        response = generate_reply(prompt)

        parsed = json.loads(response)

        return parsed.get("windows", [])

    except json.JSONDecodeError:

        logger.exception(
            "build_conversation_windows JSON parse failed "
            "[messages=%s]",
            messages
        )

        return [{"messages": messages}]

    except Exception:

        logger.exception(
            "build_conversation_windows failed "
            "[messages=%s]",
            messages
        )

        return [{"messages": messages}]
