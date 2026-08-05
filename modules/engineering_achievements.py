"""
Nova Engine v94
Engineering Achievement Engine

Tracks and persists completed engineering milestones.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


class EngineeringAchievementEngine:

    def __init__(
        self,
        history: Any,
        milestone_engine: Any,
        memory: Any,
    ) -> None:
        self.history = history
        self.milestone_engine = milestone_engine
        self.memory = memory

    def achievements(self) -> List[Dict[str, str]]:
        for milestone in self.milestone_engine.milestone_progress():
            if milestone["completed"] == milestone["total"] and milestone["total"] > 0:
                achievement = {
                    "name": milestone["name"],
                    "completed_on": datetime.now().strftime("%Y-%m-%d"),
                }
                if not self.memory.has_achievement(achievement["name"]):
                    self.memory.add_achievement(achievement)

        return self.memory.achievements()

    def format_report(self) -> str:
        lines = [
            "=" * 60,
            "ENGINEERING ACHIEVEMENTS",
            "=" * 60,
            "",
        ]

        achievements = self.achievements()

        if not achievements:
            lines.append("No milestones completed yet.")
            return "\n".join(lines)

        for achievement in achievements:
            lines.extend(
                [
                    f"🏆 {achievement['name']}",
                    f"Completed: {achievement['completed_on']}",
                    "",
                ]
            )

        return "\n".join(lines)