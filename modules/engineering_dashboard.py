"""
Nova Engine v91
Engineering Dashboard

Provides a unified engineering dashboard for Nova.

Author:
    Nova Engine
"""

from __future__ import annotations

from modules.engineering_decision_engine import EngineeringDecisionEngine
from modules.engineering_forecast import EngineeringForecastEngine
from modules.engineering_health import EngineeringHealth
from modules.engineering_history import EngineeringHistory


class EngineeringDashboard:

    def __init__(
        self,
        health: EngineeringHealth,
        forecast: EngineeringForecastEngine,
        decision: EngineeringDecisionEngine,
        history: EngineeringHistory,
    ) -> None:

        self.health = health
        self.forecast = forecast
        self.decision = decision
        self.history = history

    def _bar(self, percent: float) -> str:
        """Generates a 10-block progress bar clamped between 0% and 100%."""
        clamped = max(0.0, min(100.0, percent))
        blocks = int(clamped / 10)
        return "█" * blocks + "░" * (10 - blocks)

    def generate(self) -> str:

        report = self.health.analyze()
        decision = self.decision.decide()

        completed = self.history.completed_count()
        remaining = max(0, report.total_modules - completed)

        lines = [
            "=" * 60,
            "NOVA ENGINEERING DASHBOARD",
            "=" * 60,
            "",
            f"Engineering Health : {report.engineering_health:.1f}%",
            self._bar(report.engineering_health),
            "",
            f"Completed Improvements : {completed}",
            f"Remaining Improvements : {remaining}",
            "",
            f"Highest Priority : {decision.module}",
            f"Priority         : {decision.priority}",
            "",
            f"Projected Health : {decision.projected_health:.1f}%",
            f"Confidence       : {decision.confidence}%",
            "",
            "=" * 60,
        ]

        return "\n".join(lines)