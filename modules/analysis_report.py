"""
Nova Engine v84
Analysis Report Generator

Generates human-readable engineering reports from
an EngineeringGraph.
"""

from __future__ import annotations

from modules.engineering_graph import EngineeringGraph


class AnalysisReport:

    def __init__(self, graph: EngineeringGraph):
        self.graph = graph

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

            lines.append(f"Module: {node.name}")
            lines.append(f"Risk: {node.risk}")
            lines.append(f"Engineering Score: {node.impact_score}")

            if node.dependencies:
                lines.append("Dependencies:")
                for dep in node.dependencies:
                    lines.append(f"  - {dep}")
            else:
                lines.append("Dependencies: None")

            lines.append("")

        return "\n".join(lines)