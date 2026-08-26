"""
Nova Engine v109
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
    ) -> None:
        self.nodes[module] = GraphNode(
            name=module,
            dependencies=sorted(dependencies),
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

            graph.add_module(
                module=module,
                dependencies=dependencies,
            )

        return graph