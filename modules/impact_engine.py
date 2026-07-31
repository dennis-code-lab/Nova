"""
Nova Engine v84
Impact Analysis Engine

Calculates engineering impact based on a DependencyGraph.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from modules.dependency_analyzer import DependencyGraph


@dataclass
class ImpactAnalysis:
    affected_modules: List[str]
    complexity_score: float
    engineering_score: float
    estimated_risk: str


class ImpactEngine:
    """
    Computes engineering impact from a DependencyGraph.
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
        engineering_score = max(0.0, 10.0 - complexity)

        if complexity >= 10:
            risk = "HIGH"
        elif complexity >= 5:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return ImpactAnalysis(
            affected_modules=sorted(affected),
            complexity_score=complexity,
            engineering_score=engineering_score,
            estimated_risk=risk,
        )