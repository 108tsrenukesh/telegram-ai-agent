from datetime import (
    datetime,
    timedelta
)


def calculate_next_reminder(
    task
):

    priority = task.get(
        "priority",
        "NORMAL"
    )

    created_at = datetime.fromisoformat(
        task["created_at"]
    )

    if priority == "CRITICAL":

        return (
            created_at
            + timedelta(hours=1)
        )

    if priority == "URGENT":

        return (
            created_at
            + timedelta(hours=1)
        )

    return (
        created_at
        + timedelta(hours=2)
    )