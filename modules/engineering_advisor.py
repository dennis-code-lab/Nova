"""
Nova Engine v86
Engineering Advisor

Generates actionable engineering recommendations.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.engineering_evidence import EngineeringEvidenceEngine
from modules.engineering_score import EngineeringScoreEngine


# ==========================================================
# Data Model
# ==========================================================

@dataclass
class EngineeringAdvice:
    module: str
    priority: str
    estimated_effort: str
    expected_score: float
    recommendation: str


# ==========================================================
# Engineering Advisor
# ==========================================================

class EngineeringAdvisor:

    def __init__(
        self,
        score_engine: EngineeringScoreEngine,
        evidence_engine: EngineeringEvidenceEngine,
    ) -> None:

        self.score_engine = score_engine
        self.evidence_engine = evidence_engine

    # ------------------------------------------------------

    def advise(self, module_name: str) -> EngineeringAdvice:

        score = self.score_engine.calculate(module_name)
        evidence = self.evidence_engine.collect(module_name)

        # ---------------------------------------------
        # Priority
        # ---------------------------------------------

        if score.score <= 3:
            priority = "HIGH"
            effort = "2-3 engineering hours"

        elif score.score <= 6:
            priority = "MEDIUM"
            effort = "1-2 engineering hours"

        else:
            priority = "LOW"
            effort = "No immediate work required"

        # ---------------------------------------------
        # Recommendation
        # ---------------------------------------------

        if evidence.dependency_count >= 15:
            recommendation = (
                "Split this module into smaller feature-specific modules."
            )

        elif evidence.dependency_count >= 8:
            recommendation = (
                "Reduce coupling and simplify dependencies."
            )

        else:
            recommendation = (
                "Maintain current architecture."
            )

        expected_score = min(
            10.0,
            round(score.score + 3.0, 1)
        )

        return EngineeringAdvice(
            module=module_name,
            priority=priority,
            estimated_effort=effort,
            expected_score=expected_score,
            recommendation=recommendation,
        )

    # ------------------------------------------------------

    def format_advice(self, module_name: str) -> str:

        advice = self.advise(module_name)

        lines = [
            "=" * 50,
            "ENGINEERING ADVISOR",
            "=" * 50,
            "",
            f"Module : {advice.module}",
            f"Priority : {advice.priority}",
            f"Estimated Effort : {advice.estimated_effort}",
            "",
            "Recommendation",
            "-" * 50,
            advice.recommendation,
            "",
            f"Estimated Engineering Score After Refactor : {advice.expected_score}/10",
        ]

        return "\n".join(lines)