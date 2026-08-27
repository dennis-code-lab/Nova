"""
Nova Engine v109
Impact Analysis Engine

Calculates engineering impact based on a DependencyGraph.

Important:
- ImpactEngine owns impact analysis only.
- It does NOT own the authoritative engineering score.
- Authoritative engineering scoring belongs to EngineeringScoreEngine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from modules.dependency_analyzer import DependencyGraph


@dataclass
class ImpactAnalysis:
    affected_modules: List[str]
    complexity_score: float


class ImpactEngine:
    """
    Computes engineering impact from a DependencyGraph.

    This engine intentionally does not calculate or expose
    the authoritative engineering score.
    """

    def __init__(self, graph: DependencyGraph):
        self.graph = graph

    def analyze(self, module: str) -> ImpactAnalysis:
        """
        Analyze the engineering impact of modifying a module.
        """
        affected = []

        for mod in self.graph.modules():
            deps = self.graph.dependencies_of(mod)

            if module in deps:
                affected.append(mod)

        complexity = float(len(affected))

        return ImpactAnalysis(
            affected_modules=sorted(affected),
            complexity_score=complexity,
        )