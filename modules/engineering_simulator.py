"""
Nova Engine v103
Engineering Simulator

Evidence-based simulation of engineering improvements.

The simulator does not modify the project. It estimates how a module's
engineering score and risk could improve using observable engineering
evidence already available to Nova.
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.change_predictor import ChangePredictor
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
    """
    Simulates engineering improvements without modifying
    the project.

    Predictions are based on existing engineering evidence:
    - current engineering score
    - dependency count
    - affected-module count
    - current risk
    """

    def __init__(
        self,
        score_engine: EngineeringScoreEngine,
        risk_engine: RiskEngine,
        forecast_engine: EngineeringForecastEngine,
        predictor: ChangePredictor | None = None,
    ) -> None:
        self.score_engine = score_engine
        self.risk_engine = risk_engine
        self.forecast_engine = forecast_engine
        self.predictor = predictor

    # ------------------------------------------------------

    def simulate(self, module: str) -> SimulationResult:
        """
        Simulate a potential engineering improvement.

        The simulation is deliberately conservative and
        evidence-based rather than using a fixed score bonus.
        """

        score = self.score_engine.calculate(module)
        risk = self.risk_engine.analyze(module)

        dependency_count = getattr(score, "dependency_count", 0)

        # --------------------------------------------------
        # Determine affected-module evidence
        # --------------------------------------------------

        affected_count = 0

        if self.predictor is not None:
            prediction = self.predictor.predict(module)

            if isinstance(prediction, dict) and prediction.get("found"):
                affected_count = prediction.get("affected_count", 0)

        # --------------------------------------------------
        # Estimate improvement
        # --------------------------------------------------

        improvement = 0.5

        # Modules with larger dependency surfaces have
        # greater potential for improvement.
        if dependency_count >= 10:
            improvement += 1.5
        elif dependency_count >= 5:
            improvement += 1.0
        elif dependency_count >= 2:
            improvement += 0.5

        # High-impact modules receive a smaller additional
        # improvement opportunity based on their blast radius.
        if affected_count >= 10:
            improvement += 1.0
        elif affected_count >= 5:
            improvement += 0.5
        elif affected_count >= 2:
            improvement += 0.25

        predicted_score = min(
            10.0,
            round(score.score + improvement, 1),
        )

        # --------------------------------------------------
        # Predict risk from predicted score
        # --------------------------------------------------

        if predicted_score >= 7:
            predicted_risk = "LOW"
        elif predicted_score >= 4:
            predicted_risk = "MEDIUM"
        else:
            predicted_risk = "HIGH"

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        confidence = 60

        if dependency_count > 0:
            confidence += 10

        if affected_count > 0:
            confidence += 10

        if getattr(risk, "risk", "") in {"MEDIUM", "HIGH"}:
            confidence += 5

        confidence = min(95, confidence)

        # --------------------------------------------------
        # Project health forecast
        # --------------------------------------------------

        forecast = self.forecast_engine.generate(1)

        if forecast:
            predicted_health = forecast[0].predicted_health
        else:
            predicted_health = 100.0

        return SimulationResult(
            module=module,
            current_score=score.score,
            predicted_score=predicted_score,
            current_risk=risk.risk,
            predicted_risk=predicted_risk,
            predicted_health=predicted_health,
            confidence=confidence,
        )

    # ------------------------------------------------------

    def format_simulation(self, module: str) -> str:
        """Format simulation results for the CLI."""

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