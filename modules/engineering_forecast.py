"""
Nova Engine v117
Engineering Forecast

Builds project engineering-health forecasts from the
authoritative EngineeringHealth baseline and
EngineeringSimulator prediction model.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from modules.engineering_health import EngineeringHealth
from modules.engineering_planner_v2 import AutonomousEngineeringPlanner
from modules.engineering_simulator import EngineeringSimulator


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
    """
    Produces engineering-health forecasts using the authoritative
    project health baseline and evidence-based simulation model.
    """

    def __init__(
        self,
        planner: AutonomousEngineeringPlanner,
        health_engine: EngineeringHealth,
        simulator: EngineeringSimulator,
    ) -> None:
        self.planner = planner
        self.health_engine = health_engine
        self.simulator = simulator

    # ------------------------------------------------------

    def generate(self, limit: int = 5) -> List[ForecastItem]:
        """
        Generate forecasts for the highest-priority roadmap items.

        Each forecast starts from the same authoritative current
        engineering-health baseline and delegates prediction to
        EngineeringSimulator.
        """

        roadmap = self.planner.generate()[:limit]

        current_health = (
            self.health_engine.analyze().engineering_health
        )

        forecast: List[ForecastItem] = []

        for item in roadmap:
            simulation = self.simulator.simulate(item.module)

            predicted_health = simulation.predicted_health

            improvement = round(
                predicted_health - current_health,
                1,
            )

            forecast.append(
                ForecastItem(
                    module=item.module,
                    current_health=current_health,
                    predicted_health=predicted_health,
                    improvement=improvement,
                )
            )

        return forecast

    # ------------------------------------------------------

    def format_forecast(self) -> str:
        """Format forecast results for the CLI."""

        forecast = self.generate()

        lines = [
            "=" * 60,
            "ENGINEERING FORECAST",
            "=" * 60,
            "",
        ]

        for item in forecast:
            lines.extend(
                [
                    f"Module : {item.module}",
                    f"Current Health   : {item.current_health:.1f}%",
                    f"Predicted Health : {item.predicted_health:.1f}%",
                    f"Improvement      : +{item.improvement:.1f}%",
                    "",
                ]
            )

        lines.extend(
            [
                "=" * 60,
                "Forecast complete.",
                "=" * 60,
            ]
        )

        return "\n".join(lines)
