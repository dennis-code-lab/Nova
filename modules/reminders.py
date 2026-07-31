import json
import os
from datetime import datetime
from plyer import notification

REMINDER_FILE = "data/reminders.json"


def load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return []

    with open(REMINDER_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_reminders(reminders):
    os.makedirs("data", exist_ok=True)

    with open(REMINDER_FILE, "w", encoding="utf-8") as file:
        json.dump(reminders, file, indent=4)


def add_reminder(task, reminder_time=None):
    reminders = load_reminders()
    reminders.append({"task": task, "time": reminder_time})
    save_reminders(reminders)
    return "Reminder saved."


def list_reminders():
    reminders = load_reminders()
    if not reminders:
        return "No reminders."

    result = ""
    for i, reminder in enumerate(reminders, start=1):
        task = reminder["task"]
        reminder_time = reminder["time"]

        if reminder_time:
            result += f"{i}. {task} (at {reminder_time})\n"
        else:
            result += f"{i}. {task}\n"

    return result


def check_reminders():
    reminders = load_reminders()
    current_time = datetime.now().strftime("%H:%M")

    for reminder in reminders:
        reminder_time = reminder.get("time")

        if reminder_time == current_time:
            notification.notify(
                title="Nova Reminder", message=reminder["task"], timeout=10
            )
            return f"Reminder: {reminder['task']}"

    return None