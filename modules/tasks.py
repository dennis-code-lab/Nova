import json
import os

TASKS_FILE = "data/tasks.json"

def _load_tasks_raw():
    """Helper utility to read data persistently from file safely."""
    # Ensure database directory exists
    os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
    
    if not os.path.exists(TASKS_FILE):
        # Seed an initial mock list if empty to match your previous chat transcript
        initial_tasks = ["Study Python", "Finish Nova GUI", "Study Python"]
        _save_tasks_raw(initial_tasks)
        return initial_tasks
        
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def _save_tasks_raw(tasks_list):
    """Helper utility to save structural updates to disk safely."""
    os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks_list, f, indent=4, ensure_ascii=False)


def add_task(task_text):
    """Appends a new string entry payload down into the persistent tasks array."""
    if not task_text.strip():
        return "Task content cannot be empty."
        
    tasks = _load_tasks_raw()
    tasks.append(task_text.strip())
    _save_tasks_raw(tasks)
    return f"Task added: {task_text}"


def show_tasks():
    """Formats and builds a cleaner view layout sequence string of current entries."""
    tasks = _load_tasks_raw()
    if not tasks:
        return "You have no pending tasks on your list! All done. 🎉"
        
    formatted_lines = []
    for idx, task in enumerate(tasks, 1):
        formatted_lines.append(f"{idx}. {task}")
        
    return "\n".join(formatted_lines)


def complete_task(identity):
    """
    Nova v42 Dual-Path Target Completion Engine.
    Accepts index strings ('1'), word translations, or fuzzy/exact name matches.
    """
    tasks = _load_tasks_raw()
    if not tasks:
        return "Your task list is already completely empty!"

    identity_str = str(identity).strip()

    # --- Path A: Index-Based Match ---
    if identity_str.isdigit():
        idx = int(identity_str) - 1
        if 0 <= idx < len(tasks):
            completed_text = tasks.pop(idx)
            _save_tasks_raw(tasks)
            return f"Task completed: {completed_text}"
        return f"Invalid task number. You have {len(tasks)} tasks remaining."

    # --- Path B: Name/Text Matching ---
    else:
        identity_lower = identity_str.lower()
        
        # Look for a case-insensitive match anywhere inside the description string
        for idx, task in enumerate(tasks):
            if identity_lower in task.lower():
                completed_text = tasks.pop(idx)
                _save_tasks_raw(tasks)
                return f"Task completed: {completed_text}"
                
        return f"Could not find any pending task matching: '{identity_str}'"