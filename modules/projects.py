import os
import json
from datetime import datetime
from modules.logger import log_info, log_error

PROJECTS_FILE = os.path.join("data", "projects.json")

def _load_projects_ledger() -> dict:
    """Safely reads the long-term projects state tracker from disk."""
    if not os.path.exists(PROJECTS_FILE):
        return {}
    try:
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_error("ProjectEngine", f"Failed to parse projects ledger: {e}")
        return {}

def _save_projects_ledger(data: dict):
    """Commits active long-term project updates securely to storage."""
    try:
        os.makedirs(os.path.dirname(PROJECTS_FILE), exist_ok=True)
        with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        log_error("ProjectEngine", f"Failed to write projects ledger: {e}")

def initialize_project(project_name: str, high_level_goal: str, milestones: list):
    """Registers a fresh multi-stage roadmap with localized tracking keys."""
    ledger = _load_projects_ledger()
    
    formatted_milestones = []
    for idx, milestone in enumerate(milestones):
        formatted_milestones.append({
            "id": idx + 1,
            "title": milestone,
            "status": "Pending",
            "completed_at": None,
            "execution_traces": []
        })
        
    ledger[project_name.lower().replace(" ", "_")] = {
        "project_name": project_name,
        "goal": high_level_goal,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "completion_percentage": 0.0,
        "milestones": formatted_milestones
    }
    
    _save_projects_ledger(ledger)
    log_info("ProjectEngine", f"Initialized tracking roadmap for project: '{project_name}'")
    return f"Project '{project_name}' successfully initialized with {len(milestones)} tracking milestones."

def get_next_active_milestone(project_key: str) -> dict:
    """Polls a project roadmap to find the immediate next unexecuted milestone phase."""
    ledger = _load_projects_ledger()
    key = project_key.lower().replace(" ", "_")
    
    if key not in ledger:
        return None
        
    for milestone in ledger[key]["milestones"]:
        if milestone["status"] == "Pending":
            return milestone
    return None

def mark_milestone_complete(project_key: str, milestone_id: int, traces: list = None):
    """Closes out a specific milestone phase and automatically recalculates project completion metrics."""
    ledger = _load_projects_ledger()
    key = project_key.lower().replace(" ", "_")
    
    if key not in ledger:
        return "Project not found."
        
    project = ledger[key]
    for milestone in project["milestones"]:
        if milestone["id"] == milestone_id:
            milestone["status"] = "Completed"
            milestone["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if traces:
                milestone["execution_traces"] = traces
            break
            
    # Recalculate total project fulfillment metrics
    completed_count = sum(1 for m in project["milestones"] if m["status"] == "Completed")
    project["completion_percentage"] = (completed_count / len(project["milestones"])) * 100
    
    _save_projects_ledger(ledger)
    log_info("ProjectEngine", f"Updated progress metrics for '{key}': {project['completion_percentage']:.1f}%")
    return f"Milestone #{milestone_id} closed out. Project is now {project['completion_percentage']:.1f}% complete."

def render_project_boards() -> str:
    """Formats all active tracked projects into an interactive text summary framework."""
    ledger = _load_projects_ledger()
    if not ledger:
        return "No long-term project lifecycles are currently tracked in active storage."
        
    output = "\n" + "="*60 + "\n"
    output += "          NOVA ACTIVE LONG-TERM ROADMAP DASHBOARD         \n"
    output += "="*60 + "\n"
    
    for key, data in ledger.items():
        output += f"\nPROJECT: {data['project_name'].upper()}\n"
        output += f"Goal   : {data['goal']}\n"
        output += f"Status : {data['completion_percentage']:.1f}% Fulfilled | Started: {data['created_at']}\n"
        output += "Milestones Track Layout:\n"
        for m in data["milestones"]:
            marker = "[✓]" if m["status"] == "Completed" else "[ ]"
            date_str = f" (Done: {m['completed_at']})" if m["completed_at"] else ""
            output += f"  {marker} Phase {m['id']}: {m['title']}{date_str}\n"
        output += "-"*40 + "\n"
    output += "="*60 + "\n"
    return output