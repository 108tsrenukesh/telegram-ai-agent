import logging

from ai_router import generate_reply

logger = logging.getLogger(__name__)


# =====================================
# CLARIFICATION DETECTION
# =====================================

def needs_clarification(message):

    prompt = f"""
You are an intelligent conversational reasoning engine.

Determine whether the following request lacks enough clarity
for Renukesh to properly act on it.

Rules:
- Think like a human assistant
- Only ask clarification if truly necessary
- Avoid over-asking questions
- If task is reasonably understandable, say NO
- If critical details are missing, say YES
- Behave conversationally, not rigidly

Examples needing clarification:
- bring medicines
- buy items
- get something
- pick something
- bring dress
- get groceries for baby
- someone is coming
- you remember something ?
- guess something
- clarify something
- come early
- today we have a event

Examples NOT needing clarification:
- bring Crocin and flowers
- buy milk and bread
- call me at 5 PM
- buy baby diapers and snacks
- get vegetables and fruits
- bring chocolates and chips
- my friends <names> are coming
- today we have cricket match between RCB and GT

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

        logger.exception(
            "needs_clarification failed [message=%s]",
            message
        )

        return False


# =====================================
# CLARIFICATION REPLY
# =====================================

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

Conversation Context:
{conversation_context}

Incoming Request:
{task}

The request lacks some important details.

Your task:
Ask a natural conversational follow-up question.

Rules:
- Sound warm and human
- Never sound robotic
- Keep reply concise
- Avoid over-explaining
- Ask only what is genuinely missing
- Behave like a smart executive assistant
- Maintain conversational continuity
- Avoid generic "please provide details"
- Use relationship-aware tone
- Do not repeat the full task unnecessarily
- Sound emotionally natural
- Understand the tone of the human conversation and reply accordingly in a respectful manner

Tone Guidance:
- Wife → warm, caring, natural, romantic
- Boss → concise, professional
- Friend → casual
- Family → supportive, natural

Good Examples:
- Which medicines should I note down?
- Sure ❤️ What all should I add to the grocery list?
- Got it. Which sarees would she prefer?
- Okay, what time should I remind him?
- Sure ❤️ Which baby medicines are needed?
- Got it — what all should I add apart from vegetables?

Generate ONLY the reply message.
"""

    try:

        reply = generate_reply(
            prompt
        ).strip()

        return reply

    except Exception:

        logger.exception(
            "generate_clarification_reply failed "
            "[relationship=%s task=%s]",
            relationship, task
        )

        return (
            "Could you share a few more details "
            "so I can inform Renukesh properly?"
        )
