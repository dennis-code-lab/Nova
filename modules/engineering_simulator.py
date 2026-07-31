"""
Nova Engine v87.2
Engineering Simulator

Simulates engineering improvements without modifying
the project.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.engineering_forecast import EngineeringForecastEngine
from modules.engineering_score import EngineeringScoreEngine
from modules.risk_engine import RiskEngine


# ==========================================================
# Data Model
# ==========================================================

@dataclass
class SimulationResult:
    module: str
    current_score: float
    predicted_score: float
    current_risk: str
    predicted_risk: str
    predicted_health: float
    confidence: int


# ==========================================================
# Simulator
# ==========================================================

class EngineeringSimulator:

    def __init__(
        self,
        score_engine: EngineeringScoreEngine,
        risk_engine: RiskEngine,
        forecast_engine: EngineeringForecastEngine,
    ) -> None:

        self.score_engine = score_engine
        self.risk_engine = risk_engine
        self.forecast_engine = forecast_engine

    # ------------------------------------------------------

    def simulate(self, module: str) -> SimulationResult:

        score = self.score_engine.calculate(module)
        risk = self.risk_engine.analyze(module)

        predicted_score = min(10.0, round(score.score + 3.0, 1))

        if predicted_score >= 7:
            predicted_risk = "LOW"
        elif predicted_score >= 4:
            predicted_risk = "MEDIUM"
        else:
            predicted_risk = "HIGH"

        health = self.forecast_engine.generate(1)[0].predicted_health

        return SimulationResult(
            module=module,
            current_score=score.score,
            predicted_score=predicted_score,
            current_risk=risk.risk,
            predicted_risk=predicted_risk,
            predicted_health=health,
            confidence=85,
        )

    # ------------------------------------------------------

    def format_simulation(self, module: str) -> str:

        result = self.simulate(module)

        lines = [
            "=" * 60,
            "ENGINEERING SIMULATION",
            "=" * 60,
            "",
            f"Module : {result.module}",
            "",
            f"Current Score   : {result.current_score}/10",
            f"Predicted Score : {result.predicted_score}/10",
            "",
            f"Risk : {result.current_risk} -> {result.predicted_risk}",
            "",
            f"Predicted Health : {result.predicted_health:.1f}%",
            f"Confidence       : {result.confidence}%",
            "",
            "=" * 60,
            "Simulation complete.",
            "=" * 60,
        ]

        return "\n".join(lines)