import logging
import re

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def extract_deadline(text):

    lower = text.lower()

    now = datetime.now()

    # =========================
    # Today X AM/PM
    # =========================

    match = re.search(
        r"(\d{1,2})\s*(am|pm)",
        lower
    )

    if match:

        try:

            hour = int(match.group(1))
            meridian = match.group(2)

            if meridian == "pm" and hour != 12:
                hour += 12

            if meridian == "am" and hour == 12:
                hour = 0

            if not 0 <= hour <= 23:
                logger.warning(
                    "extract_deadline: hour out of range "
                    "[hour=%d text=%s] — skipping time parse",
                    hour, text
                )

            else:

                deadline = now.replace(
                    hour=hour,
                    minute=0,
                    second=0,
                    microsecond=0
                )

                # If already passed today, move to tomorrow
                if deadline < now:
                    deadline += timedelta(days=1)

                return deadline.isoformat()

        except (ValueError, AttributeError):

            logger.exception(
                "extract_deadline: failed to parse time "
                "[text=%s]",
                text
            )

    # =========================
    # Tomorrow
    # =========================

    if "tomorrow" in lower:

        try:

            deadline = (now + timedelta(days=1)).replace(
                hour=9,
                minute=0,
                second=0,
                microsecond=0
            )

            return deadline.isoformat()

        except (ValueError, OverflowError):

            logger.exception(
                "extract_deadline: failed to parse 'tomorrow' "
                "[text=%s]",
                text
            )

    # =========================
    # Tonight
    # =========================

    if "tonight" in lower:

        try:

            deadline = now.replace(
                hour=20,
                minute=0,
                second=0,
                microsecond=0
            )

            return deadline.isoformat()

        except (ValueError, OverflowError):

            logger.exception(
                "extract_deadline: failed to parse 'tonight' "
                "[text=%s]",
                text
            )

    return None
