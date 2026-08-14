"""
Nova Engine v106
Analysis Report Generator

Generates human-readable engineering reports from
the authoritative EngineeringScoreEngine.

Legacy impact_score remains graph metadata and is not
used as the displayed engineering health score.
"""

from __future__ import annotations

from modules.engineering_graph import EngineeringGraph
from modules.engineering_score import EngineeringScoreEngine
from modules.risk_engine import RiskEngine


class AnalysisReport:

    def __init__(self, graph: EngineeringGraph) -> None:
        self.graph = graph

        # AnalysisReport owns a scoring service for backward
        # compatibility with the existing constructor.
        self.risk_engine = RiskEngine(graph)
        self.score_engine = EngineeringScoreEngine(
            graph,
            self.risk_engine,
        )

    def generate(self) -> str:
        lines = []

        lines.append("=" * 50)
        lines.append("ENGINEERING IMPACT REPORT")
        lines.append("=" * 50)
        lines.append("")

        lines.append(f"Modules Analyzed : {self.graph.total_modules()}")
        lines.append("")

        for module in self.graph.modules():
            node = self.graph.get_node(module)

            if node is None:
                continue

            score = self.score_engine.calculate(module)

            lines.append(f"Module: {node.name}")
            lines.append(f"Risk: {score.risk}")
            lines.append(f"Engineering Score: {score.score}")

            if node.dependencies:
                lines.append("Dependencies:")
                for dep in node.dependencies:
                    lines.append(f"  - {dep}")
            else:
                lines.append("Dependencies: None")

            lines.append("")

        return "\n".join(lines)