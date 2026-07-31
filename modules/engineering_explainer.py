"""
Nova Engine v86
Engineering Explainer

Explains engineering decisions in human-readable form.

Author:
    Nova Engine
"""

from __future__ import annotations

from modules.engineering_evidence import EngineeringEvidenceEngine
from modules.engineering_score import EngineeringScoreEngine
from modules.risk_engine import RiskEngine


class EngineeringExplainer:

    def __init__(
        self,
        score_engine: EngineeringScoreEngine,
        risk_engine: RiskEngine,
        evidence_engine: EngineeringEvidenceEngine,
    ) -> None:

        self.score_engine = score_engine
        self.risk_engine = risk_engine
        self.evidence_engine = evidence_engine

    # --------------------------------------------------

    def explain(self, module_name: str) -> str:

        score = self.score_engine.calculate(module_name)
        assessment = self.risk_engine.analyze(module_name)
        evidence = self.evidence_engine.collect(module_name)

        if score.score <= 3:
            recommendation = (
                "Consider refactoring into smaller modules."
            )

        elif score.score <= 6:
            recommendation = (
                "Monitor architectural complexity."
            )

        else:
            recommendation = (
                "No immediate refactoring required."
            )

        lines = [
            "=" * 50,
            "ENGINEERING EXPLANATION",
            "=" * 50,
            "",
            f"Module : {module_name}",
            f"Engineering Score : {score.score}/10",
            f"Risk : {assessment.risk}",
            "",
            "Evidence",
            "-" * 50,
        ]

        for item in evidence.evidence:
            lines.append(f"• {item}")

        lines.extend([
            "",
            "Recommendation",
            "-" * 50,
            recommendation,
        ])

        return "\n".join(lines)