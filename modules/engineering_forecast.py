"""
Nova Engine v87.1
Engineering Forecast

Predicts engineering health improvements if roadmap items
are completed.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from modules.engineering_health import EngineeringHealth
from modules.engineering_planner_v2 import AutonomousEngineeringPlanner


# ==========================================================
# Data Model
# ==========================================================

@dataclass
class ForecastItem:
    module: str
    current_health: float
    predicted_health: float
    improvement: float


# ==========================================================
# Forecast Engine
# ==========================================================

class EngineeringForecastEngine:

    def __init__(
        self,
        planner: AutonomousEngineeringPlanner,
        health_engine: EngineeringHealth,
    ) -> None:

        self.planner = planner
        self.health_engine = health_engine

    # ------------------------------------------------------

    def generate(self, limit: int = 5) -> List[ForecastItem]:

        roadmap = self.planner.generate()[:limit]

        current_health = self.health_engine.analyze().engineering_health

        predicted = current_health

        forecast: List[ForecastItem] = []

        for item in roadmap:

            # Estimated improvement based on priority
            if item.priority == "HIGH":
                delta = 2.0
            elif item.priority == "MEDIUM":
                delta = 1.0
            else:
                delta = 0.5

            predicted = min(100.0, round(predicted + delta, 1))

            forecast.append(
                ForecastItem(
                    module=item.module,
                    current_health=current_health,
                    predicted_health=predicted,
                    improvement=delta,
                )
            )

            current_health = predicted

        return forecast

    # ------------------------------------------------------

    def format_forecast(self) -> str:

        forecast = self.generate()

        lines = [
            "=" * 60,
            "ENGINEERING FORECAST",
            "=" * 60,
            "",
        ]

        for item in forecast:

            lines.extend([
                f"Module : {item.module}",
                f"Current Health   : {item.current_health:.1f}%",
                f"Predicted Health : {item.predicted_health:.1f}%",
                f"Improvement      : +{item.improvement:.1f}%",
                "",
            ])

        lines.extend([
            "=" * 60,
            "Forecast complete.",
            "=" * 60,
        ])

        return "\n".join(lines)