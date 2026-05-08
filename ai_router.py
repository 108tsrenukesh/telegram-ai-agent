import os
import random

from dotenv import load_dotenv

from groq import Groq

from google import genai

from templates import TEMPLATES


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

            print("Reply generated using GROQ")

            return reply.strip()

    except Exception as e:

        print("GROQ FAILED")
        print(e)

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

            print("Reply generated using GEMINI")

            return reply.strip()

    except Exception as e:

        print("GEMINI FAILED")
        print(e)

    # =====================================
    # FINAL FALLBACK → TEMPLATE
    # =====================================

    print("Using template fallback")

    return random.choice(TEMPLATES)