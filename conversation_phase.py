def determine_phase(intent, message):

    text = message.lower()

    # =========================
    # Emotional Signals
    # Check FIRST — takes priority
    # over closure for phrases like
    # "take care ❤️" or "miss you, tc"
    # =========================

    emotional_words = [
        "love you",
        "miss you",
        "❤️",
        "😘",
        "take care",
    ]

    if any(word in text for word in emotional_words):

        return "emotional"

    # =========================
    # Closure Signals
    # Checked AFTER emotional —
    # "take care" alone is emotional,
    # pure goodbyes land here
    # =========================

    closure_words = [
        "bye",
        "good night",
        "that's all",
        "thats all",
        "okay thanks",
        "thank you",
        "thanks",
        "tc",
        "see you",
        "cya",
        "ttyl",
        "talk later",
        "got to go",
    ]

    if any(word in text for word in closure_words):

        return "closing"

    # =========================
    # Task Phases
    # =========================

    if intent == "FOLLOWUP_TASK":

        return "confirming"

    if intent == "TASK":

        return "collecting"

    return "normal"
