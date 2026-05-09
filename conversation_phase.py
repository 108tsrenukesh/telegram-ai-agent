def determine_phase(
    intent,
    message
):

    text = message.lower()

    # =========================
    # Closure Signals
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
        "take care"

    ]

    emotional_words = [

        "love you",
        "miss you",
        "❤️",
        "😘"

    ]

    if any(
        word in text
        for word in closure_words
    ):

        return "closing"

    if any(
        word in text
        for word in emotional_words
    ):

        return "emotional"

    if intent == "FOLLOWUP_TASK":

        return "confirming"

    if intent == "TASK":

        return "collecting"

    return "normal"