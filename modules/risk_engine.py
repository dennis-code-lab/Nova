"""
Nova Engine v84
Risk Engine

Computes engineering risk levels for every module in the
Engineering Graph.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from modules.engineering_graph import EngineeringGraph


# ==========================================================
# Data Model
# ==========================================================

@dataclass
class RiskAssessment:
    module: str
    engineering_score: float
    dependency_count: int
    risk: str
    reasons: List[str]


# ==========================================================
# Risk Engine
# ==========================================================

class RiskEngine:
    """
    Computes engineering risk for modules.
    """

    def __init__(self, graph: EngineeringGraph) -> None:
        self.graph = graph

    def analyze(self, module_name: str) -> RiskAssessment:
        node = self.graph.get_node(module_name)

        if node is None:
            raise ValueError(f"Unknown module: {module_name}")

        dependency_count = len(node.dependencies)
        score = node.impact_score

        reasons: List[str] = []

        # --------------------------------------------------
        # Risk Rules
        # --------------------------------------------------

        if dependency_count >= 10:
            reasons.append("Large dependency surface")

        elif dependency_count >= 5:
            reasons.append("Moderate dependency surface")

        if score <= 3:
            reasons.append("Low engineering score")

        elif score <= 6:
            reasons.append("Medium engineering score")

        # --------------------------------------------------
        # Overall Risk
        # --------------------------------------------------

        if dependency_count >= 10 or score <= 3:
            risk = "HIGH"

        elif dependency_count >= 5 or score <= 6:
            risk = "MEDIUM"

        else:
            risk = "LOW"

        if not reasons:
            reasons.append("Healthy engineering profile")

        return RiskAssessment(
            module=module_name,
            engineering_score=score,
            dependency_count=dependency_count,
            risk=risk,
            reasons=reasons,
        )

    # ------------------------------------------------------

    def analyze_all(self) -> Dict[str, RiskAssessment]:
        results: Dict[str, RiskAssessment] = {}

        for module in self.graph.modules():
            results[module] = self.analyze(module)

        return results