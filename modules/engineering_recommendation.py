"""
Nova Engine v114
Engineering Recommendation Engine

Ranks modules that should be refactored first based on dependency
complexity and engineering health scores.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from modules.engineering_graph import EngineeringGraph
from modules.engineering_score import EngineeringScoreEngine


# ==========================================================
# Data Model
# ==========================================================

@dataclass
class Recommendation:
    module: str
    risk: str
    dependencies: int
    engineering_score: float


# ==========================================================
# Recommendation Engine
# ==========================================================

class EngineeringRecommendation:

    def __init__(
        self,
        graph: EngineeringGraph,
        score_engine: EngineeringScoreEngine,
    ) -> None:
        self.graph = graph
        self.score_engine = score_engine

    # ------------------------------------------------------

    def top_candidates(
        self,
        limit: int = 5,
    ) -> List[Recommendation]:
        recommendations: List[Recommendation] = []

        for module in self.graph.modules():
            node = self.graph.get_node(module)

            if node is None:
                continue

            score = self.score_engine.calculate(module)

            recommendations.append(
                Recommendation(
                    module=module,
                    risk=score.risk,
                    dependencies=score.dependency_count,
                    engineering_score=score.score,
                )
            )

        # Sort by:
        # 1. Highest dependency count
        # 2. Lowest engineering score
        recommendations.sort(
            key=lambda r: (
                -r.dependencies,
                r.engineering_score,
            )
        )

        return recommendations[:limit]
