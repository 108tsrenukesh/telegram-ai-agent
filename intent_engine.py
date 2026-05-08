TASK_KEYWORDS = [

    "bring",
    "buy",
    "remind",
    "call",
    "send",
    "share",
    "get",
    "pick",
    "collect"

]


STATUS_KEYWORDS = [

    "had lunch",
    "reached",
    "where are you",
    "available",
    "free",
    "busy"

]


def detect_intent(message):

    text = message.lower()

    for keyword in TASK_KEYWORDS:

        if keyword in text:

            return "TASK"

    for keyword in STATUS_KEYWORDS:

        if keyword in text:

            return "STATUS_CHECK"

    return "GENERAL"