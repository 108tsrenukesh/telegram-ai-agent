import logging
import os
import random

from dotenv import load_dotenv

from groq import Groq

from google import genai

from templates import TEMPLATES

logger = logging.getLogger(__name__)


# =====================================
# LOAD ENV VARIABLES FIRST
# =====================================

load_dotenv()


# =====================================
# GROQ CLIENT
# =====================================

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# =====================================
# GEMINI CLIENT
# =====================================

gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# =====================================
# MAIN AI ROUTER
# =====================================

def generate_reply(message_text):

    prompt = f"""
You are a helpful personal assistant.

Generate a short natural conversational reply.

Keep the reply:
- concise
- human sounding
- polite
- realistic

Message:
"{message_text}"
"""

    # =====================================
    # PRIMARY AI → GROQ
    # =====================================

    try:

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        reply = response.choices[0].message.content

        if reply:

            logger.info("Reply generated via Groq")

            return reply.strip()

    except Exception:

        logger.exception(
            "Groq failed [prompt_length=%d]",
            len(prompt)
        )

    # =====================================
    # SECONDARY AI → GEMINI
    # =====================================

    try:

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        reply = response.text

        if reply:

            logger.info("Reply generated via Gemini (Groq fallback)")

            return reply.strip()

    except Exception:

        logger.exception(
            "Gemini failed [prompt_length=%d]",
            len(prompt)
        )

    # =====================================
    # FINAL FALLBACK → TEMPLATE
    # =====================================

    logger.warning(
        "Both Groq and Gemini failed — using template fallback "
        "[prompt_length=%d]",
        len(prompt)
    )

    return random.choice(TEMPLATES)
