"""
Nova Engine v100
Engineering Progress Engine

Calculates engineering progress across the autonomous engineering universe.

Completed modules remain part of the overall engineering universe,
while the autonomous roadmap contains only remaining work.
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
        """
        Calculate engineering progress.

        The active roadmap normally contains remaining work only.
        When the real EngineeringHistory exposes completed_modules(),
        completed modules are merged back into the engineering universe.

        Lightweight test doubles that only implement is_completed()
        remain supported.
        """

        roadmap = self.planner.generate()

        roadmap_modules = {
            item.module
            for item in roadmap
        }

        # Determine completed modules.
        #
        # Real EngineeringHistory provides completed_modules().
        # Lightweight test mocks may only provide is_completed().
        if hasattr(self.history, "completed_modules"):
            completed_modules = set(
                self.history.completed_modules()
            )
        else:
            completed_modules = {
                item.module
                for item in roadmap
                if self.history.is_completed(item.module)
            }

        # Complete engineering universe:
        # remaining roadmap + completed historical modules.
        all_modules = roadmap_modules | completed_modules

        total = len(all_modules)

        completed = len(
            completed_modules & all_modules
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