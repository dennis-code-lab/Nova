"""
Nova Engine v92
Engineering Progress Engine

Calculates engineering progress across the autonomous roadmap.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.engineering_history import EngineeringHistory
from modules.engineering_planner_v2 import AutonomousEngineeringPlanner


@dataclass
class EngineeringProgress:
    total_modules: int
    completed_modules: int
    remaining_modules: int
    progress_percent: float


class EngineeringProgressEngine:

    def __init__(
        self,
        planner: AutonomousEngineeringPlanner,
        history: EngineeringHistory,
    ) -> None:
        self.planner = planner
        self.history = history

    def calculate(self) -> EngineeringProgress:
        roadmap = self.planner.generate()
        total = len(roadmap)

        completed = sum(
            1
            for item in roadmap
            if self.history.is_completed(item.module)
        )

        remaining = total - completed

        if total == 0:
            percent = 100.0
        else:
            percent = round(
                (completed / total) * 100,
                1,
            )

        return EngineeringProgress(
            total_modules=total,
            completed_modules=completed,
            remaining_modules=remaining,
            progress_percent=percent,
        )

    def format_progress(self) -> str:
        progress = self.calculate()

        lines = [
            "=" * 60,
            "ENGINEERING PROGRESS",
            "=" * 60,
            "",
            f"Overall Progress : {progress.progress_percent:.1f}%",
            "",
            f"Completed Modules : {progress.completed_modules}",
            f"Remaining Modules : {progress.remaining_modules}",
            f"Total Modules     : {progress.total_modules}",
            "",
            "=" * 60,
        ]

        return "\n".join(lines)