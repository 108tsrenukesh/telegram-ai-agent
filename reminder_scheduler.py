import logging

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def calculate_next_reminder(task):

    priority = task.get("priority", "NORMAL")

    created_at_raw = task.get("created_at")

    if not created_at_raw:

        logger.warning(
            "calculate_next_reminder: task missing 'created_at' "
            "[task_id=%s] — defaulting to now",
            task.get("id", "unknown")
        )

        created_at = datetime.now()

    else:

        try:

            created_at = datetime.fromisoformat(created_at_raw)

        except Exception:

            logger.exception(
                "calculate_next_reminder: failed to parse 'created_at' "
                "[task_id=%s created_at=%s] — defaulting to now",
                task.get("id", "unknown"), created_at_raw
            )

            created_at = datetime.now()

    if priority in ("CRITICAL", "URGENT"):

        return created_at + timedelta(hours=1)

    return created_at + timedelta(hours=2)
