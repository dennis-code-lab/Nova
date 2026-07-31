"""
Nova Engine v84
Impact Analysis Engine - Test Suite

test_impact_engine.py
"""

import unittest

from modules.dependency_analyzer import DependencyGraph
from modules.impact_engine import ImpactEngine


class TestImpactEngine(unittest.TestCase):

    def setUp(self):
        self.graph = DependencyGraph()

        self.graph.add_dependency("main", "modules.memory")
        self.graph.add_dependency("router", "modules.memory")
        self.graph.add_dependency("planner", "modules.memory")
        self.graph.add_dependency("dashboard", "modules.router")

    def test_low_risk_analysis(self):
        engine = ImpactEngine(self.graph)

        result = engine.analyze("modules.router")

        self.assertEqual(result.estimated_risk, "LOW")
        self.assertEqual(result.complexity_score, 1.0)

    def test_affected_modules(self):
        engine = ImpactEngine(self.graph)

        result = engine.analyze("modules.memory")

        self.assertEqual(
            sorted(result.affected_modules),
            ["main", "planner", "router"]
        )

        self.assertEqual(result.complexity_score, 3.0)

    def test_engineering_score(self):
        engine = ImpactEngine(self.graph)

        result = engine.analyze("modules.memory")

        self.assertEqual(result.engineering_score, 7.0)


if __name__ == "__main__":
    unittest.main()