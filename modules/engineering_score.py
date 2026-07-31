"""
Nova Engine v86
Engineering Score Engine

Calculates weighted engineering scores for modules.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.engineering_graph import EngineeringGraph
from modules.risk_engine import RiskEngine


# ==========================================================
# Data Model
# ==========================================================

@dataclass
class EngineeringScore:
    module: str
    score: float
    dependency_count: int
    risk: str


# ==========================================================
# Engineering Score Engine
# ==========================================================

class EngineeringScoreEngine:
    """
    Computes a normalized engineering score for modules.
    Higher scores indicate healthier modules.
    """

    def __init__(
        self,
        graph: EngineeringGraph,
        risk_engine: RiskEngine,
    ) -> None:

        self.graph = graph
        self.risk_engine = risk_engine

    # ------------------------------------------------------

    def calculate(self, module_name: str) -> EngineeringScore:

        node = self.graph.get_node(module_name)

        if node is None:
            raise ValueError(f"Unknown module: {module_name}")

        dependencies = len(node.dependencies)

        assessment = self.risk_engine.analyze(module_name)

        score = 10.0

        # Dependency penalty
        score -= dependencies * 0.3

        # Risk penalty
        if assessment.risk == "MEDIUM":
            score -= 2.0

        elif assessment.risk == "HIGH":
            score -= 4.0

        # Clamp score to the range [0.0, 10.0]
        score = max(0.0, min(10.0, score))

        return EngineeringScore(
            module=module_name,
            score=round(score, 1),
            dependency_count=dependencies,
            risk=assessment.risk,
        )