from modules.alarms import list_alarms
from modules.reminders import list_reminders
from modules.tasks import show_tasks


def plan_day():
    result = []

    result.append("=== DAILY PLAN ===")
    result.append("")

    result.append("TASKS:")
    result.append(show_tasks())
    result.append("")

    result.append("REMINDERS:")
    result.append(list_reminders())
    result.append("")

    result.append("ALARMS:")
    result.append(list_alarms())

    return "\n".join(result)