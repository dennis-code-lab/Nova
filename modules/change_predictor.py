"""
Nova Engine v84
Change Predictor

Predicts which modules are affected when another module changes.
"""

from __future__ import annotations

from typing import Any, Dict, List

from modules.engineering_graph import EngineeringGraph


class ChangePredictor:

    def __init__(self, graph: EngineeringGraph) -> None:
        self.graph = graph

    def predict(self, module_name: str) -> Dict[str, Any]:
        """
        Predict downstream modules affected by changing one module.
        """
        if self.graph.get_node(module_name) is None:
            return {
                "module": module_name,
                "found": False,
                "affected_modules": [],
                "affected_count": 0,
            }

        affected: List[str] = []

        # Search every module in the graph.
        # If it imports the requested module, it will be affected.
        for node in self.graph.nodes.values():
            if module_name in node.dependencies:
                affected.append(node.name)

        affected.sort()

        return {
            "module": module_name,
            "found": True,
            "affected_modules": affected,
            "affected_count": len(affected),
        }