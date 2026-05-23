from ai_router import generate_reply


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

Examples needing clarification:
- bring medicines
- buy items
- get groceries
- pick something
- bring dress
- pick something
- get something
- people came
- people will come
- today is match

Examples NOT needing clarification:
- bring Crocin and flowers
- buy milk and bread
- call me at 5 PM
- buy baby diapers and snacks
- get vegetables and fruits
- my friends <friend_names> will come
- my friends <friend_names> came
- today is RCB vs GT match

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

Tone Guidance:
- Wife → warm, caring, natural
- Boss → concise, professional
- Friend → casual
- Family → supportive

Examples:
- Which medicines should I note down?
- Sure ❤️ What all should I add to the grocery list?
- Got it. Which sarees would she prefer?
- Okay, what time should I remind him?

Generate ONLY the reply message.
"""

    try:

        reply = generate_reply(
            prompt
        ).strip()

        return reply

    except Exception:

        return (
            "Could you share a few more details "
            "so I can inform Renukesh properly?"
        )