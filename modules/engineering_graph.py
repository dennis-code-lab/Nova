"""
Nova Engine v109
Engineering Graph

Builds a graph representation combining dependency
relationships and engineering impact.

Note:
GraphNode.impact_score is retained as legacy graph metadata.
It is NOT the authoritative engineering score.
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
    ) -> None:
        self.nodes[module] = GraphNode(
            name=module,
            dependencies=sorted(dependencies),
            impact_score=impact_score,
        )

    def get_node(self, module: str) -> Optional[GraphNode]:
        return self.nodes.get(module)

    def modules(self) -> List[str]:
        return sorted(self.nodes.keys())

    def total_modules(self) -> int:
        return len(self.nodes)


class EngineeringGraphBuilder:
    """
    Converts DependencyGraph + ImpactAnalysis into EngineeringGraph.

    The legacy GraphNode.impact_score is derived from impact complexity
    for compatibility. It is not the authoritative engineering score.
    """

    def __init__(self, dependency_graph: DependencyGraph):
        self.dependency_graph = dependency_graph

    def build(
        self,
        analyses: Dict[str, ImpactAnalysis],
    ) -> EngineeringGraph:
        graph = EngineeringGraph()

        for module in self.dependency_graph.modules():
            analysis = analyses.get(module)

            if analysis is None:
                continue

            dependencies = list(
                self.dependency_graph.dependencies_of(module)
            )

            # Legacy graph metadata only.
            # The authoritative engineering score belongs to
            # EngineeringScoreEngine.
            legacy_impact_score = max(
                0.0,
                10.0 - analysis.complexity_score,
            )

            graph.add_module(
                module=module,
                dependencies=dependencies,
                impact_score=legacy_impact_score,
            )

        return graph