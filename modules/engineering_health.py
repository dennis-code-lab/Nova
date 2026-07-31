"""
Nova Engine v86
Engineering Health Analyzer

Calculates project-wide engineering health metrics based on average engineering scores.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.engineering_graph import EngineeringGraph
from modules.risk_engine import RiskEngine
from modules.engineering_score import EngineeringScoreEngine


# ==========================================================
# Data Model
# ==========================================================

@dataclass
class HealthReport:
    total_modules: int
    low_risk: int
    medium_risk: int
    high_risk: int
    engineering_health: float


# ==========================================================
# Health Analyzer
# ==========================================================

class EngineeringHealth:

    def __init__(
        self,
        graph: EngineeringGraph,
        risk_engine: RiskEngine,
    ) -> None:

        self.graph = graph
        self.risk_engine = risk_engine

        self.score_engine = EngineeringScoreEngine(
            graph,
            risk_engine,
        )

    # ------------------------------------------------------

    def analyze(self) -> HealthReport:

        low = 0
        medium = 0
        high = 0

        for module in self.graph.modules():

            result = self.risk_engine.analyze(module)

            if result.risk == "LOW":
                low += 1

            elif result.risk == "MEDIUM":
                medium += 1

            else:
                high += 1

        total = self.graph.total_modules()

        # ---------------------------------------------
        # Engineering Score Average
        # ---------------------------------------------
        total_score = 0.0
        for module in self.graph.modules():
            score = self.score_engine.calculate(module)
            total_score += score.score

        if self.graph.modules():
            average_score = (
                total_score /
                len(self.graph.modules())
            )
        else:
            average_score = 10.0

        health = round(
            average_score * 10,
            1,
        )

        return HealthReport(
            total_modules=total,
            low_risk=low,
            medium_risk=medium,
            high_risk=high,
            engineering_health=health,
        )