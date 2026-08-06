"""
Nova Engine v98
Engineering Milestone Engine

Groups engineering modules into milestones and reports progress.
"""

from __future__ import annotations

from typing import Any, Dict, List


class EngineeringMilestoneEngine:

    def __init__(self, history: Any) -> None:
        self.history = history

        self.milestones: Dict[str, List[str]] = {
            "Foundation": [
                "modules.engineering_runtime",
                "modules.engineering_memory",
                "modules.engineering_history",
            ],
            "Engineering Intelligence": [
                "modules.engineering_graph",
                "modules.engineering_score",
                "modules.risk_engine",
                "modules.change_predictor",
                "modules.engineering_decision_engine",
            ],
            "Automation": [
                "modules.engineering_controller",
                "modules.engineering_progress",
                "modules.engineering_forecast",
                "modules.engineering_dashboard",
            ],
        }

    def milestone_progress(self) -> List[Dict[str, Any]]:
        results = []

        for name, modules in self.milestones.items():
            completed = sum(
                1
                for module in modules
                if self.history.is_completed(module)
            )

            total = len(modules)
            percent = (completed / total * 100) if total else 0.0

            results.append(
                {
                    "name": name,
                    "completed": completed,
                    "total": total,
                    "percent": percent,
                }
            )

        return results

    def completed(self) -> List[Dict[str, Any]]:
        """
        Returns only milestones that are fully completed.
        """
        return [
            milestone
            for milestone in self.milestone_progress()
            if milestone["completed"] == milestone["total"]
        ]

    def format_report(self) -> str:
        lines = [
            "=" * 60,
            "ENGINEERING MILESTONES",
            "=" * 60,
            "",
        ]

        for milestone in self.milestone_progress():
            bars = int(round(milestone["percent"] / 10))
            bar = "█" * bars + "░" * (10 - bars)

            lines.extend(
                [
                    milestone["name"],
                    f"{bar} {milestone['percent']:.0f}%",
                    f"Completed: {milestone['completed']}/{milestone['total']}",
                    "",
                ]
            )

        return "\n".join(lines)