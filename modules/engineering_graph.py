"""
Nova Engine v84
Engineering Graph

Builds a graph representation combining dependency
relationships and engineering impact.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from modules.dependency_analyzer import DependencyGraph
from modules.impact_engine import ImpactAnalysis


@dataclass
class GraphNode:
    name: str
    dependencies: List[str] = field(default_factory=list)
    impact_score: float = 0.0
    risk: str = "LOW"


class EngineeringGraph:
    """
    High-level engineering graph built from
    dependency and impact analysis.
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}

    def add_module(
        self,
        module: str,
        dependencies: List[str],
        impact_score: float,
        risk: str,
    ) -> None:
        self.nodes[module] = GraphNode(
            name=module,
            dependencies=sorted(dependencies),
            impact_score=impact_score,
            risk=risk,
        )

    def get_node(self, module: str) -> Optional[GraphNode]:
        return self.nodes.get(module)

    def modules(self) -> List[str]:
        return sorted(self.nodes.keys())

    def total_modules(self) -> int:
        return len(self.nodes)


class EngineeringGraphBuilder:
    """
    Converts DependencyGraph +
    ImpactAnalysis into EngineeringGraph.
    """

    def __init__(self, dependency_graph: DependencyGraph):
        self.dependency_graph = dependency_graph

    def build(self, analyses: Dict[str, ImpactAnalysis]) -> EngineeringGraph:
        graph = EngineeringGraph()

        for module in self.dependency_graph.modules():
            analysis = analyses.get(module)

            if analysis is None:
                continue

            graph.add_module(
                module=module,
                dependencies=list(
                    self.dependency_graph.dependencies_of(module)
                ),
                impact_score=analysis.engineering_score,
                risk=analysis.estimated_risk,
            )

        return graph