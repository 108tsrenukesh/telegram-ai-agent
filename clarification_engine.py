from ai_router import generate_reply


def needs_clarification(message):

    prompt = f"""
You are an AI assistant.

Determine whether this request lacks enough clarity.

Examples needing clarification:
- bring medicines
- buy items
- get groceries
- pick something

Examples NOT needing clarification:
- bring Crocin and flowers
- buy milk and bread
- call me at 5 PM

Message:
{message}

Reply ONLY:
YES
or
NO
"""

    try:

        result = generate_reply(
            prompt
        ).strip().upper()

        return result == "YES"

    except Exception:

        return False


def generate_clarification_reply(

    relationship,
    task,
    conversation_context=None

):

    prompt = f"""
You are Lucifer,
Renukesh's personal AI assistant.

Relationship:
{relationship}

Message:
{message}

The request lacks clarity.

Ask a polite follow-up question.

Rules:
- Sound human
- Sound warm
- Ask concise questions
- Ask for missing details naturally
- Mention Lucifer naturally
- Never sound robotic

Generate ONLY the reply.
"""

    try:

        return generate_reply(
            prompt
        ).strip()

    except Exception:

        return (
            "Could you please share "
            "a few more details so I "
            "can inform Renukesh properly?"
        )