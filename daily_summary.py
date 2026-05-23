from datetime import datetime

from semantic_task_engine import (
    load_tasks
)


def generate_daily_summary():

    tasks = load_tasks()

    pending = []
    completed = []

    for task in tasks:

        if task["status"] == "COMPLETED":

            completed.append(task)

        else:

            pending.append(task)

    summary = (
        "📋 Daily Summary\n\n"
    )

    summary += (
        f"✅ Completed: "
        f"{len(completed)}\n"
    )

    summary += (
        f"📌 Pending: "
        f"{len(pending)}\n\n"
    )

    if pending:

        summary += (
            "Pending Tasks:\n"
        )

        for task in pending[:5]:

            summary += (
                f"- {task['type']} "
                f"({task['priority']})\n"
            )

    return summary