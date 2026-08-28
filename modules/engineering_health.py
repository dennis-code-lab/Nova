"""
Nova Engine v114
Engineering Health Analyzer

Calculates project-wide engineering health metrics from the
authoritative EngineeringScoreEngine.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.engineering_graph import EngineeringGraph
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
        score_engine: EngineeringScoreEngine,
    ) -> None:
        self.graph = graph
        self.score_engine = score_engine

    # ------------------------------------------------------

    def analyze(self) -> HealthReport:
        low = 0
        medium = 0
        high = 0

        total_score = 0.0
        modules = self.graph.modules()

        for module in modules:
            score = self.score_engine.calculate(module)
            total_score += score.score

            if score.risk == "LOW":
                low += 1
            elif score.risk == "MEDIUM":
                medium += 1
            else:
                high += 1

        total = self.graph.total_modules()

        # ---------------------------------------------
        # Engineering Score Average
        # ---------------------------------------------

        if modules:
            average_score = total_score / len(modules)
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
