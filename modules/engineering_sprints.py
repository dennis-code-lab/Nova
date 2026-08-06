"""
Nova Engine v96
Engineering Sprint Manager
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class EngineeringSprintManager:

    def __init__(self, history: Any) -> None:
        self.history = history

        self.sprints = [
            {
                "name": "Sprint 1",
                "goal": "Foundation",
                "modules": [
                    "modules.engineering_runtime",
                    "modules.engineering_memory",
                    "modules.engineering_history",
                ],
            },
            {
                "name": "Sprint 2",
                "goal": "Engineering Intelligence",
                "modules": [
                    "modules.engineering_score",
                    "modules.risk_engine",
                    "modules.change_predictor",
                    "modules.engineering_decision_engine",
                    "modules.engineering_forecast",
                ],
            },
            {
                "name": "Sprint 3",
                "goal": "Automation",
                "modules": [
                    "modules.engineering_controller",
                    "modules.orchestrator",
                    "modules.refactor_planner",
                    "modules.engineering_runtime",
                ],
            },
        ]

    def active_sprint(self) -> Optional[Dict[str, Any]]:
        """Returns the first sprint that has incomplete modules."""
        for sprint in self.sprints:
            completed = sum(
                self.history.is_completed(module)
                for module in sprint["modules"]
            )

            if completed < len(sprint["modules"]):
                return sprint

        return None

    def progress(self) -> Optional[Dict[str, Any]]:
        """Calculates and returns progress metrics for the currently active sprint."""
        sprint = self.active_sprint()

        if sprint is None:
            return None

        completed_modules = []
        remaining_modules = []

        for module in sprint["modules"]:
            if self.history.is_completed(module):
                completed_modules.append(module)
            else:
                remaining_modules.append(module)

        completed = len(completed_modules)
        total = len(sprint["modules"])

        return {
            "name": sprint["name"],
            "goal": sprint["goal"],
            "completed": completed,
            "remaining": len(remaining_modules),
            "total": total,
            "percent": round((completed / total) * 100),
            "completed_modules": completed_modules,
            "remaining_modules": remaining_modules,
        }

    def format_report(self) -> str:
        """Formats the active sprint status into a CLI report string."""
        sprint = self.progress()

        if sprint is None:
            return (
                "=" * 60 + "\n"
                "ALL SPRINTS COMPLETE\n"
                + "=" * 60
            )

        bar = "█" * (sprint["percent"] // 10)
        bar += "░" * (10 - len(bar))

        completed_text = "\n".join(
            f"✓ {module}"
            for module in sprint["completed_modules"]
        )
        remaining_text = "\n".join(
            f"• {module}"
            for module in sprint["remaining_modules"]
        )

        if not completed_text:
            completed_text = "None"
        if not remaining_text:
            remaining_text = "None"

        estimated = sprint["remaining"]

        return f"""
============================================================
{sprint['name']}
============================================================

Goal

{sprint['goal']}

Progress

{bar} {sprint['percent']}%

Completed

{completed_text}

Remaining

{remaining_text}

Estimated Completion

{estimated} engineering session(s)
"""