from datetime import date, datetime
import random

# Nova v45 Systems
from modules.logger import log_info, log_error

# Nova v46/v47: Dynamic Plugin & Event Bus Architecture
from modules.plugins import get_plugin_routes
from modules.bus import publish  # <-- Nova v47 Global Communication Bus Line

# Standard Core Components
from modules.alarms import add_alarm, delete_alarm, list_alarms
from modules.apps import open_app
from modules.context import get_context
from modules.filesearch import find_file
from modules.help_system import show_help
from modules.note_search import search_notes
from modules.planner import plan_day
from modules.reminders import add_reminder, list_reminders
from modules.stopwatch import (
    start_stopwatch,
    stop_stopwatch,
    stopwatch_time,
)
from modules.systemcontrol import (
    lock_computer,
    restart_computer,
    shutdown_computer,
    sleep_computer,
)
from modules.systeminfo import (
    get_battery_status,
    get_computer_name,
    get_current_user,
    get_disk_space,
    get_ip_address,
)
from modules.tasks import (
    add_task,
    complete_task,
    show_tasks,
)
from modules.timers import start_timer
from modules.weather import get_weather
from modules.websearch import web_search

# Nova v90 Engineering Runtime Type
from modules.engineering_runtime import EngineeringRuntime


def handle_command(
    text: str,
    engineering: EngineeringRuntime,
    intent_payload: dict = None,
) -> str | None:
    lower = text.lower().strip()

    if intent_payload is None:
        intent_payload = {"intent": "CHAT", "parameter": None}

    intent = intent_payload.get("intent")
    parameter = intent_payload.get("parameter")

    # --- Context Commands & Action Chaining ---
    cleaned_text = text.strip().rstrip("?")
    lower_clean = cleaned_text.lower()

    if lower_clean.startswith("what about ") or lower_clean.startswith("how about "):
        next_item = cleaned_text[11:].strip()
        last_action = get_context("last_action_type")

        if not last_action or last_action == "weather":
            return get_weather(next_item)
        if last_action == "search":
            return web_search(next_item)
        if last_action == "find_note":
            return search_notes(next_item)

    if lower_clean.startswith("and "):
        next_item = cleaned_text[4:].strip()
        last_action = get_context("last_action_type")

        if last_action == "weather":
            return get_weather(next_item)
        if last_action == "search":
            return web_search(next_item)
        if last_action == "find_note":
            return search_notes(next_item)

    # --- Nova v46/v47: Dynamic Plugin & Event Bus Routing ---
    plugin_routes = get_plugin_routes()
    if intent in plugin_routes:
        try:
            plugin_module = plugin_routes[intent]["module"]
            log_info("PluginEngine", f"Routing runtime control to dynamic plugin for intent: {intent}")

            publish("intent_triggered", {"intent": intent, "parameter": parameter})
            result = plugin_module.execute(parameter)
            publish("intent_success", {"intent": intent, "result": result})
            return result
        except Exception as e:
            log_error("PluginEngine", f"Dynamic execution crash on intent [{intent}]: {e}")
            publish("intent_failure", {"intent": intent, "error": str(e)})
            return f"Runtime Notice: The dynamic skill plugin for '{intent}' encountered a fatal exception."

    # --- Nova v45: Supervised Runtime Core Routing ---
    if intent == "WEATHER" and parameter:
        try:
            log_info("RuntimeCore", f"Executing WEATHER intent for parameter: {parameter}")
            return get_weather(str(parameter).rstrip("?"))
        except Exception as e:
            log_error("WEATHER_MODULE", f"Execution failed: {e}")
            return f"Runtime Notice: The weather subsystem encountered an unexpected issue processing '{parameter}'."

    if intent == "SEARCH" and parameter:
        try:
            log_info("RuntimeCore", f"Executing SEARCH intent for query: {parameter}")
            return web_search(str(parameter).rstrip("?"))
        except Exception as e:
            log_error("SEARCH_MODULE", f"Execution failed: {e}")
            return "Runtime Notice: Web search execution was interrupted due to a connectivity or module failure."

    if intent == "FIND_NOTE" and parameter:
        try:
            log_info("RuntimeCore", f"Executing FIND_NOTE intent for keyword: {parameter}")
            return search_notes(str(parameter).rstrip("?"))
        except Exception as e:
            log_error("NOTE_MODULE", f"Execution failed: {e}")
            return "Runtime Notice: Failed to index or read local notes database safely."

    if intent == "ADD_TASK" and parameter:
        try:
            log_info("RuntimeCore", f"Executing ADD_TASK intent: {parameter}")
            return add_task(str(parameter))
        except Exception as e:
            log_error("TASK_MODULE", f"Failed to append task: {e}")
            return "Runtime Notice: Could not commit your new task to disk storage."

    if intent == "SHOW_TASKS":
        try:
            log_info("RuntimeCore", "Executing SHOW_TASKS intent")
            return show_tasks()
        except Exception as e:
            log_error("TASK_MODULE", f"Failed to retrieve tasks: {e}")
            return "Runtime Notice: Unable to open task registry file."

    if intent == "COMPLETE_TASK" and parameter:
        try:
            log_info("RuntimeCore", f"Executing COMPLETE_TASK intent for parameter: {parameter}")
            task_identity = str(parameter).lower().replace("task", "").replace("number", "").strip()

            word_to_num = {
                "the first one": "1", "first": "1",
                "the second one": "2", "second": "2",
                "the third one": "3", "third": "3",
            }
            clean_phrase = task_identity.replace("one", "").strip()

            if task_identity in word_to_num:
                task_identity = word_to_num[task_identity]
            elif clean_phrase in word_to_num:
                task_identity = word_to_num[clean_phrase]

            return complete_task(task_identity)
        except Exception as e:
            log_error("TASK_MODULE", f"Failed to finalize completion state: {e}")
            return "Runtime Notice: Complete action aborted due to a database access failure."

    # =====================================================
    # Nova v90 Engineering Runtime Commands
    # =====================================================

    if lower.startswith("engineering report "):
        module = text[len("engineering report "):].strip()
        try:
            return engineering.report(module)
        except Exception as e:
            return f"Engineering Error: {e}"

    if lower.startswith("engineering plan "):
        module = text[len("engineering plan "):].strip()
        try:
            return engineering.plan(module)
        except Exception as e:
            return f"Engineering Error: {e}"

    if lower.startswith("engineering predict "):
        module = text[len("engineering predict "):].strip()
        try:
            result = engineering.predict(module)
            if not result.get("found"):
                return f"Module '{module}' was not found."

            lines = [
                f"Module: {module}",
                "",
                f"Affected Modules ({result['affected_count']}):",
            ]
            if result.get("affected_modules"):
                for m in result["affected_modules"]:
                    lines.append(f" • {m}")
            else:
                lines.append(" None")
            return "\n".join(lines)
        except Exception as e:
            return f"Engineering Error: {e}"

    if lower.startswith("engineering risk "):
        module = text[len("engineering risk "):].strip()
        try:
            risk = engineering.risk(module)
            lines = [
                f"Module: {risk.module}",
                f"Risk: {risk.risk}",
                f"Engineering Score: {risk.engineering_score}",
                f"Dependencies: {risk.dependency_count}",
                "",
                "Reasons:",
            ]
            for reason in risk.reasons:
                lines.append(f" • {reason}")
            return "\n".join(lines)
        except Exception as e:
            return f"Engineering Error: {e}"

    if lower == "engineering overview":
        try:
            return engineering.overview()
        except Exception as e:
            return f"Engineering Error: {e}"

    if lower.startswith("engineering explain "):
        module = text[len("engineering explain "):].strip()
        try:
            return engineering.explain(module)
        except Exception as e:
            return f"Engineering Error: {e}"

    if lower.startswith("engineering advise "):
        module = text[len("engineering advise "):].strip()
        try:
            return engineering.advise(module)
        except Exception as e:
            return f"Engineering Error: {e}"

    if lower == "engineering roadmap":
        try:
            return engineering.roadmap()
        except Exception as e:
            return f"Engineering Error: {e}"

    if lower == "engineering forecast":
        try:
            return engineering.forecast()
        except Exception as e:
            return f"Engineering Error: {e}"

    if lower.startswith("engineering simulate "):
        module = text[len("engineering simulate "):].strip()
        try:
            return engineering.simulate(module)
        except Exception as e:
            return f"Engineering Error: {e}"

    if lower == "engineering decision":
        try:
            return engineering.decision()
        except Exception as e:
            return f"Engineering Error: {e}"

    if lower.startswith("engineering complete "):
        module = text[len("engineering complete "):].strip()
        try:
            engineering.complete(module)
            return f"Module '{module}' successfully recorded as completed."
        except Exception as e:
            return f"Engineering Error: {e}"

    # --- Legacy Hardcoded Rules (Fallback Utilities) ---
    if lower == "today":
        return datetime.now().strftime("%A, %d %B %Y")
    if lower == "what day is it":
        return datetime.now().strftime("%A")
    if lower == "what is today's date":
        return datetime.now().strftime("%d %B %Y")
    if lower == "what month is it":
        return datetime.now().strftime("%B")
    if lower == "what year is it":
        return datetime.now().strftime("%Y")

    # --- Countdowns ---
    if lower == "how many days until christmas":
        today = date.today()
        christmas = date(today.year, 12, 25)
        if today > christmas:
            christmas = date(today.year + 1, 12, 25)
        return f"{(christmas - today).days} days until Christmas."

    if lower == "how many days until new year":
        today = date.today()
        new_year = date(today.year + 1, 1, 1)
        return f"{(new_year - today).days} days until New Year."

    # --- Utilities ---
    if lower == "flip a coin":
        return random.choice(["Heads", "Tails"])
    if lower == "roll a dice":
        return f"You rolled a {random.randint(1, 6)}"
    if lower == "random number":
        return str(random.randint(1, 100))

    # --- Timers & Stopwatches ---
    if lower.startswith("set timer "):
        timer_text = text[10:].strip().lower()
        try:
            if timer_text.endswith(" seconds") or timer_text.endswith(" second"):
                return start_timer(int(timer_text.split()[0]))
            if timer_text.endswith(" minutes") or timer_text.endswith(" minute"):
                return start_timer(int(timer_text.split()[0]) * 60)
            if timer_text.endswith(" hours") or timer_text.endswith(" hour"):
                return start_timer(int(timer_text.split()[0]) * 3600)
            return "Use: set timer 10 seconds, 5 minutes, or 1 hour."
        except ValueError:
            return "Invalid timer value."

    if lower == "start stopwatch":
        return start_stopwatch()
    if lower == "stopwatch time":
        return stopwatch_time()
    if lower == "stop stopwatch":
        return stop_stopwatch()

    # --- Alarms ---
    if lower.startswith("set alarm for "):
        return add_alarm(text[14:].strip())
    if lower == "show alarms":
        return list_alarms()
    if lower.startswith("delete alarm "):
        return delete_alarm(text[13:].strip())

    # --- Application Launching ---
    if "notepad" in lower and any(x in lower for x in ["open", "launch", "start"]):
        return open_app("notepad")
    if "calculator" in lower and any(x in lower for x in ["open", "launch", "start"]):
        return open_app("calculator")
    if "chrome" in lower and any(x in lower for x in ["open", "launch", "start"]):
        return open_app("chrome")
    if "paint" in lower and any(x in lower for x in ["open", "launch", "start"]):
        return open_app("paint")

    # --- File Search ---
    if lower.startswith("find file "):
        return find_file(text[10:].strip())

    # --- System Information & Control ---
    if lower == "battery status":
        return get_battery_status()
    if lower == "disk space":
        return get_disk_space()
    if lower == "computer name":
        return get_computer_name()
    if lower == "current user":
        return get_current_user()
    if lower == "ip address":
        return get_ip_address()
    if lower == "lock computer":
        return lock_computer()
    if lower == "restart computer":
        return restart_computer()
    if lower == "shutdown computer":
        return shutdown_computer()
    if lower == "sleep computer":
        return sleep_computer()

    # --- Reminders ---
    if lower.startswith("remind me to "):
        reminder_text = text[13:].strip()
        if " at " in reminder_text:
            task, reminder_time = reminder_text.rsplit(" at ", 1)
            return add_reminder(task.strip(), reminder_time.strip())
        return add_reminder(reminder_text)
    if lower == "show reminders":
        return list_reminders()

    if lower == "plan my day":
        return plan_day()
    if lower == "help":
        return show_help()

    return None