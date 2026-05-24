# =====================================
# FALLBACK TEMPLATES
# =====================================
# Used when both Groq and Gemini fail.
# Neutral, non-robotic, no "Hello !" prefix.
# Relationship-aware templates are handled
# by the reply generator — these are
# last-resort safety nets only.

TEMPLATES = [
    "Got it, noted.",
    "Sure, I'll pass this on to Renukesh.",
    "Understood. I'll make sure Renukesh sees this.",
    "On it. I'll let Renukesh know.",
    "Noted. I'll follow up on this.",
    "I'll make sure this gets Renukesh's attention.",
    "Sorry for the slow reply — I'll get back to you shortly.",
]
