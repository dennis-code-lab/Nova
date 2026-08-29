"""
Nova Engine v89
Engineering Decision Engine

Combines Nova's engineering intelligence subsystems into a
single prioritized recommendation while filtering completed items.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.engineering_advisor import EngineeringAdvisor
from modules.engineering_history import EngineeringHistory
from modules.engineering_planner_v2 import AutonomousEngineeringPlanner
from modules.engineering_simulator import EngineeringSimulator


# ==========================================================
# Data Model
# ==========================================================

@dataclass
class EngineeringDecision:
    module: str
    priority: str
    effort: str
    recommendation: str
    projected_health: float
    confidence: int


# ==========================================================
# Decision Engine
# ==========================================================

class EngineeringDecisionEngine:
    """
    Produces Nova's single highest-priority engineering decision.
    """

    def __init__(
        self,
        planner: AutonomousEngineeringPlanner,
        advisor: EngineeringAdvisor,
        simulator: EngineeringSimulator,
        history: EngineeringHistory,
    ) -> None:

        self.planner = planner
        self.advisor = advisor
        self.simulator = simulator
        self.history = history

    # ------------------------------------------------------

    def decide(self) -> EngineeringDecision:

        roadmap = self.planner.generate()

        remaining = [
            item
            for item in roadmap
            if not self.history.is_completed(item.module)
        ]

        if not remaining:
            raise RuntimeError(
                "All roadmap items have been completed."
            )

        target = remaining[0]

        advice = self.advisor.advise(target.module)
        simulation = self.simulator.simulate(target.module)

        return EngineeringDecision(
            module=target.module,
            priority=advice.priority,
            effort=advice.estimated_effort,
            recommendation=advice.recommendation,
            projected_health=simulation.predicted_health,
            confidence=simulation.confidence,
        )

    # ------------------------------------------------------

    def format_decision(self) -> str:

        decision = self.decide()

        lines = [
            "=" * 60,
            "ENGINEERING DECISION",
            "=" * 60,
            "",
            f"Highest Priority Module : {decision.module}",
            f"Priority                : {decision.priority}",
            f"Estimated Effort        : {decision.effort}",
            "",
            "Recommendation",
            "-" * 60,
            decision.recommendation,
            "",
            f"Projected Engineering Health : {decision.projected_health:.1f}%",
            f"Decision Confidence          : {decision.confidence}%",
            "",
            "=" * 60,
            "Decision complete.",
            "=" * 60,
        ]

        return "\n".join(lines)