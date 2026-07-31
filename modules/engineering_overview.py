"""
Nova Engine v85
Engineering Overview Generator

Produces a project-wide engineering summary.

Author:
    Nova Engine
"""

from __future__ import annotations

from modules.engineering_graph import EngineeringGraph
from modules.engineering_health import EngineeringHealth
from modules.engineering_recommendation import EngineeringRecommendation
from modules.risk_engine import RiskEngine


class EngineeringOverview:

    def __init__(
        self,
        graph: EngineeringGraph,
        risk_engine: RiskEngine,
    ) -> None:

        self.graph = graph
        self.risk_engine = risk_engine
        self.health = EngineeringHealth(
            graph,
            risk_engine,
        )
        self.recommendation = EngineeringRecommendation(
            graph,
            risk_engine,
        )

    # ------------------------------------------------------

    def generate(self) -> str:

        report = self.health.analyze()

        lines = [
            "=" * 60,
            "NOVA ENGINEERING OVERVIEW",
            "=" * 60,
            "",
            f"Modules Analysed : {report.total_modules}",
            f"Engineering Health : {report.engineering_health:.1f}%",
            "",
            "Risk Summary",
            "-" * 60,
            f"LOW    : {report.low_risk}",
            f"MEDIUM : {report.medium_risk}",
            f"HIGH   : {report.high_risk}",
        ]

        lines.extend([
            "",
            "Top Refactor Candidates",
            "-" * 60,
        ])

        candidates = self.recommendation.top_candidates(5)

        if not candidates:
            lines.append("No recommendations available.")
        else:
            for i, candidate in enumerate(candidates, start=1):
                lines.append(
                    f"{i}. {candidate.module}"
                )
                lines.append(
                    f"   Risk: {candidate.risk}"
                )
                lines.append(
                    f"   Dependencies: {candidate.dependencies}"
                )
                lines.append(
                    f"   Engineering Score: "
                    f"{candidate.engineering_score}"
                )
                lines.append("")

        lines.extend([
            "=" * 60,
            "Engineering overview complete.",
            "=" * 60,
        ])

        return "\n".join(lines)