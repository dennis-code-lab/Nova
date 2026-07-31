import json
import os
from typing import Dict, List, Optional

class EngineeringPlanner:
    def __init__(self, roadmap_path: str = 'data/roadmap.json'):
        self.roadmap_path = roadmap_path

    def load_roadmap(self) -> Dict:
        if not os.path.exists(self.roadmap_path):
            return {"milestone": "v83-beta", "sprints": {}, "tasks": []}
        with open(self.roadmap_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_roadmap(self, data: Dict):
        with open(self.roadmap_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def estimate_task(self, task_id: str) -> str:
        roadmap = self.load_roadmap()
        for t in roadmap.get("tasks", []):
            if t["id"].upper() == task_id.upper():
                effort = t.get("effort", "Medium")
                time_map = {"Low": "1-2 hours", "Medium": "4-6 hours", "High": "8-12 hours"}
                risk_map = {"Low": "Low", "Medium": "Moderate - Needs review", "High": "Critical"}
                return (
                    f"\n[ESTIMATE] Task {t['id']}: {t['title']}\n"
                    f"Effort:       {effort}\n"
                    f"Est. Time:    {time_map.get(effort, '4-6 hours')}\n"
                    f"Risk:         {risk_map.get(t.get('risk', 'Low'), 'Low')}\n"
                    f"Dependencies: {', '.join(t.get('dependencies', ['None']))}\n"
                )
        return f"Task {task_id} not found."

    def get_intelligent_priority(self, task_id: str) -> str:
        roadmap = self.load_roadmap()
        for t in roadmap.get("tasks", []):
            if t["id"].upper() == task_id.upper():
                reasons = t.get("priority_reasons", [
                    "Core dependency for downstream modules",
                    "Maintains operational stability",
                    "Reduces system technical debt"
                ])
                out = [f"\n[INTELLIGENT PRIORITY] {t['id']} (Priority: {t.get('priority', 'P1')})"]
                out.append("Highest priority because:")
                for r in reasons:
                    out.append(f" • {r}")
                return "\n".join(out)
        return f"Task {task_id} not found."

    def format_sprint_roadmap(self) -> str:
        roadmap = self.load_roadmap()
        sprints = roadmap.get("sprints", {
            "Sprint 1": "? Patch System & Auto-Git",
            "Sprint 2": "? Rollback Engine & Release Notes",
            "Sprint 3": "? Planner & Decision Engine (Active)",
            "Sprint 4": "Documentation & Regression Testing"
        })
        out = ["\n==================================================",
               "               ENGINEERING ROADMAP                ",
               "=================================================="]
        for name, desc in sprints.items():
            out.append(f"{name:<12} | {desc}")
        out.append("==================================================")
        return "\n".join(out)

    def format_plan_dashboard(self) -> str:
        roadmap = self.load_roadmap()
        tasks = roadmap.get("tasks", [])
        total = len(tasks)
        done = sum(1 for t in tasks if t.get("status") == "DONE")
        pct = int((done / total) * 100) if total > 0 else 0
        bar = "¦" * (pct // 10) + "¦" * (10 - (pct // 10))

        out = ["\n==================================================",
               f"   NOVA ENGINE ROADMAP [{roadmap.get('milestone', 'v83')}]",
               "==================================================",
               f"Progress: [{bar}] {pct}% ({done}/{total} Tasks Completed)\n"]
        for t in tasks:
            status_icon = "?" if t["status"] == "DONE" else "?"
            out.append(f"{status_icon} [{t['id']}] {t['title']} ({t['status']})")
        out.append("==================================================")
        return "\n".join(out)

    def get_next_task(self) -> Optional[Dict]:
        roadmap = self.load_roadmap()
        for t in roadmap.get("tasks", []):
            if t.get("status") != "DONE":
                return t
        return None

    def add_task(self, title: str) -> Dict:
        roadmap = self.load_roadmap()
        tasks = roadmap.get("tasks", [])
        next_num = 101 + len(tasks)
        new_task = {
            "id": f"TASK-{next_num}",
            "title": title,
            "status": "BACKLOG",
            "priority": "P1",
            "effort": "Medium",
            "risk": "Low",
            "dependencies": ["TASK-103"]
        }
        tasks.append(new_task)
        roadmap["tasks"] = tasks
        self.save_roadmap(roadmap)
        return new_task
