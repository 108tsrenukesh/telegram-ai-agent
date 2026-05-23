from datetime import datetime

from semantic_task_engine import (
    load_tasks
)

from relationship_memory import (
    load_relationship_memory
)


def generate_brain_summary():

    tasks = load_tasks()

    relationships = (
        load_relationship_memory()
    )

    pending = []
    completed = []

    for task in tasks:

        if task["status"] == "COMPLETED":

            completed.append(task)

        else:

            pending.append(task)

    summary = []

    summary.append(
        "🧠 Lucifer Daily Brain\n"
    )

    summary.append(
        f"Pending Tasks: {len(pending)}"
    )

    summary.append(
        f"Completed Tasks: {len(completed)}\n"
    )

    # =========================
    # Frequent Topics
    # =========================

    summary.append(
        "📌 Relationship Insights:\n"
    )

    for person, data in relationships.items():

        topics = data.get(
            "topics",
            []
        )[:3]

        interactions = data.get(
            "interaction_count",
            0
        )

        summary.append(

            f"- {person}: "
            f"{interactions} interactions"

        )

        if topics:

            summary.append(
                f"  Topics: "
                f"{', '.join(topics)}"
            )

    # =========================
    # Pending Important Tasks
    # =========================

    summary.append(
        "\n⚠️ Important Pending:\n"
    )

    for task in pending[:5]:

        task_type = task.get(
            "type",
            "GENERAL"
        )

        priority = task.get(
            "priority",
            "NORMAL"
        )

        items = task.get(
            "items",
            []
        )

        summary.append(

            f"- [{priority}] "
            f"{task_type}: "
            f"{', '.join(items[:3])}"

        )

    return "\n".join(summary)