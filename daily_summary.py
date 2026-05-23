import logging

from semantic_task_engine import load_tasks

logger = logging.getLogger(__name__)


def generate_daily_summary():

    tasks = load_tasks()

    pending = []
    completed = []

    for task in tasks:

        if task.get("status") == "COMPLETED":
            completed.append(task)
        else:
            pending.append(task)

    summary = "📋 Daily Summary\n\n"
    summary += f"✅ Completed: {len(completed)}\n"
    summary += f"📌 Pending: {len(pending)}\n\n"

    if pending:

        summary += "Pending Tasks:\n"

        for task in pending[:5]:

            task_type = task.get("type", "GENERAL")
            priority = task.get("priority", "NORMAL")

            summary += f"- {task_type} ({priority})\n"

    return summary
