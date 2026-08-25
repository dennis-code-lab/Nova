"""
Nova Engine v84
Engineering Graph - Test Suite

test_engineering_graph.py
"""

import unittest

from modules.dependency_analyzer import DependencyGraph
from modules.engineering_graph import EngineeringGraphBuilder
from modules.impact_engine import ImpactAnalysis


class TestEngineeringGraph(unittest.TestCase):

    def setUp(self):
        self.dep = DependencyGraph()

        self.dep.add_dependency(
            "main",
            "modules.memory",
        )

        self.dep.add_dependency(
            "router",
            "modules.memory",
        )

        self.analyses = {
            "main": ImpactAnalysis(
                affected_modules=["router"],
                complexity_score=1,
                estimated_risk="LOW",
            ),
            "router": ImpactAnalysis(
                affected_modules=[],
                complexity_score=0,
                estimated_risk="LOW",
            ),
        }

    def test_graph_creation(self):
        builder = EngineeringGraphBuilder(self.dep)
        graph = builder.build(self.analyses)

        self.assertEqual(
            graph.total_modules(),
            2,
        )

    def test_node_lookup(self):
        builder = EngineeringGraphBuilder(self.dep)
        graph = builder.build(self.analyses)

        node = graph.get_node("main")

        self.assertIsNotNone(node)
        self.assertEqual(node.impact_score, 9)
        self.assertFalse(hasattr(node, "risk"))


if __name__ == "__main__":
    unittest.main()