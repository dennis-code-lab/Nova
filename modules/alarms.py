from datetime import datetime
import json
import os

ALARMS_FILE = "data/alarms.json"


def load_alarms():
    if not os.path.exists(ALARMS_FILE):
        return []
    try:
        with open(ALARMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_alarms(alarms):
    # Ensure directory exists before trying to write to a file inside it
    os.makedirs(os.path.dirname(ALARMS_FILE), exist_ok=True)
    with open(ALARMS_FILE, "w", encoding="utf-8") as f:
        json.dump(alarms, f, indent=4)


def add_alarm(alarm_time):
    alarms = load_alarms()
    if alarm_time in alarms:
        return "Alarm already exists."

    alarms.append(alarm_time)
    save_alarms(alarms)
    return f"Alarm set for {alarm_time}"


def list_alarms():
    alarms = load_alarms()
    if not alarms:
        return "No alarms set."
    return "Alarms:\n" + "\n".join(alarms)


def delete_alarm(alarm_time):
    alarms = load_alarms()
    if alarm_time not in alarms:
        return "Alarm not found."

    alarms.remove(alarm_time)
    save_alarms(alarms)
    return f"Alarm {alarm_time} deleted."


def check_alarms():
    now = datetime.now().strftime("%H:%M")
    alarms = load_alarms()

    if now in alarms:
        return f"ALARM! It is now {now}."
    return None