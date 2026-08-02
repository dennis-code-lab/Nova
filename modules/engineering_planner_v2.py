"""
Nova Engine v87
Autonomous Engineering Planner

Builds a prioritized engineering roadmap from live
engineering intelligence.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from modules.engineering_advisor import EngineeringAdvisor
from modules.engineering_graph import EngineeringGraph
from modules.engineering_score import EngineeringScoreEngine


# ==========================================================
# Data Model
# ==========================================================

@dataclass
class RoadmapItem:
    module: str
    priority: str
    engineering_score: float
    estimated_effort: str
    recommendation: str


# ==========================================================
# Planner
# ==========================================================

class AutonomousEngineeringPlanner:

    def __init__(
        self,
        graph: EngineeringGraph,
        score_engine: EngineeringScoreEngine,
        advisor: EngineeringAdvisor,
    ) -> None:

        self.graph = graph
        self.score_engine = score_engine
        self.advisor = advisor

    # ------------------------------------------------------

    def generate(self) -> List[RoadmapItem]:

        roadmap: List[RoadmapItem] = []

        ENGINEERING_MODULE_PREFIXES = (
            "modules.engineering",
            "modules.risk_engine",
            "modules.change_predictor",
            "modules.dependency_analyzer",
            "modules.impact_engine",
            "modules.refactor_planner",
            "modules.logger",
            "modules.orchestrator",
        )

        for module in self.graph.modules():

            if not module.startswith(ENGINEERING_MODULE_PREFIXES):
                continue

            score = self.score_engine.calculate(module)
            advice = self.advisor.advise(module)

            roadmap.append(
                RoadmapItem(
                    module=module,
                    priority=advice.priority,
                    engineering_score=score.score,
                    estimated_effort=advice.estimated_effort,
                    recommendation=advice.recommendation,
                )
            )

        priority_order = {
            "HIGH": 0,
            "MEDIUM": 1,
            "LOW": 2,
        }

        roadmap.sort(
            key=lambda item: (
                priority_order.get(item.priority, 3),
                item.engineering_score,
            )
        )

        return roadmap

    # ------------------------------------------------------

    def format_roadmap(
        self,
        limit: int = 10,
    ) -> str:

        roadmap = self.generate()

        lines = [
            "=" * 60,
            "AUTONOMOUS ENGINEERING ROADMAP",
            "=" * 60,
            "",
        ]

        for index, item in enumerate(roadmap[:limit], start=1):

            lines.extend(
                [
                    f"{index}. {item.module}",
                    f"   Priority : {item.priority}",
                    f"   Score    : {item.engineering_score}/10",
                    f"   Effort   : {item.estimated_effort}",
                    f"   Action   : {item.recommendation}",
                    "",
                ]
            )

        return "\n".join(lines)