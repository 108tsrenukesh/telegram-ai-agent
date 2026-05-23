import re

from datetime import (
    datetime,
    timedelta
)


def extract_deadline(text):

    lower = text.lower()

    now = datetime.now()

    # =========================
    # Today 7 PM
    # =========================

    match = re.search(
        r"(\d{1,2})\s*(am|pm)",
        lower
    )

    if match:

        hour = int(
            match.group(1)
        )

        meridian = match.group(2)

        if meridian == "pm" and hour != 12:

            hour += 12

        if meridian == "am" and hour == 12:

            hour = 0

        deadline = now.replace(

            hour=hour,
            minute=0,
            second=0,
            microsecond=0

        )

        # If already passed today
        # move to tomorrow

        if deadline < now:

            deadline += timedelta(days=1)

        return deadline.isoformat()

    # =========================
    # Tomorrow
    # =========================

    if "tomorrow" in lower:

        deadline = now + timedelta(days=1)

        deadline = deadline.replace(

            hour=9,
            minute=0,
            second=0,
            microsecond=0

        )

        return deadline.isoformat()

    # =========================
    # Tonight
    # =========================

    if "tonight" in lower:

        deadline = now.replace(

            hour=20,
            minute=0,
            second=0,
            microsecond=0

        )

        return deadline.isoformat()

    return None