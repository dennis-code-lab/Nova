"""
Nova Engine v86
Engineering Evidence Engine

Collects factual engineering evidence for modules.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from modules.change_predictor import ChangePredictor
from modules.engineering_graph import EngineeringGraph
from modules.risk_engine import RiskEngine


# ==========================================================
# Data Model
# ==========================================================

@dataclass
class EngineeringEvidence:
    module: str
    dependency_count: int
    affected_modules: int
    risk: str
    evidence: List[str]


# ==========================================================
# Evidence Engine
# ==========================================================

class EngineeringEvidenceEngine:
    """
    Collects engineering facts without making decisions.
    """

    def __init__(
        self,
        graph: EngineeringGraph,
        predictor: ChangePredictor,
        risk_engine: RiskEngine,
    ) -> None:

        self.graph = graph
        self.predictor = predictor
        self.risk_engine = risk_engine

    # ------------------------------------------------------

    def collect(self, module_name: str) -> EngineeringEvidence:

        node = self.graph.get_node(module_name)

        if node is None:
            raise ValueError(f"Unknown module: {module_name}")

        prediction = self.predictor.predict(module_name)
        assessment = self.risk_engine.analyze(module_name)

        dependency_count = len(node.dependencies)
        affected_count = prediction["affected_count"]

        evidence = [
            f"Direct dependencies: {dependency_count}",
            f"Affected modules: {affected_count}",
            f"Risk classification: {assessment.risk}",
        ]

        return EngineeringEvidence(
            module=module_name,
            dependency_count=dependency_count,
            affected_modules=affected_count,
            risk=assessment.risk,
            evidence=evidence,
        )