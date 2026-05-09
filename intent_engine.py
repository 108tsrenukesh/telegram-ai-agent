from ai_router import generate_reply


def detect_intent(message):

    prompt = f"""
You are an AI intent classifier.

Classify this Telegram message into ONLY one category:

- TASK
- STATUS_CHECK
- GENERAL
- ACKNOWLEDGEMENT
- TASK_COMPLETION
- EMOTIONAL
- FOLLOWUP_TASK
- CLOSURE

Rules:

TASK:
- Requests
- Actions
- Reminders
- Demands
- Ordering
- Asking Renukesh to do something

STATUS_CHECK:
- Asking where he is
- Asking availability
- Asking status updates

ACKNOWLEDGEMENT:
- Thanks
- Okay
- Done
- Fine
- Emojis only
- Reactions
- Greetings
- Small talk

GENERAL:
- Everything else

TASK_COMPLETION:
- done grocery
- completed medicines
- task finished
- bought items
- finished report

EMOTIONAL:
- love you
- miss you
- take care
- ❤️
- good night

FOLLOWUP_TASK:
- add chips also
- one more item
- also buy milk
- dont forget my favourite

CLOSURE:
- bye
- thank you
- thats all
- okay thanks
- good night

Message:
{message}

Reply ONLY with category name.
"""

    try:

        result = generate_reply(
            prompt
        ).strip().upper()

        allowed = [

            "TASK",
            "STATUS_CHECK",
            "GENERAL",
            "ACKNOWLEDGEMENT",
	    "TASK_COMPLETION",
	    "EMOTIONAL",
	    "FOLLOWUP_TASK",
	    "CLOSURE"

        ]

        if result in allowed:

            return result

    except Exception:

        pass

    return "GENERAL"