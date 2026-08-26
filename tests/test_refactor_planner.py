"""
Nova Engine v84
Unit Tests - Refactor Planner

Verifies generation and formatting of refactoring execution plans,
time estimation, and handling of unknown targets.
"""

from __future__ import annotations

import unittest

from modules.change_predictor import ChangePredictor
from modules.engineering_graph import EngineeringGraph
from modules.refactor_planner import RefactorPlanner
from modules.risk_engine import RiskEngine


class TestRefactorPlanner(unittest.TestCase):

    def setUp(self) -> None:
        graph = EngineeringGraph()

        graph.add_module(
            module="modules.ai",
            dependencies=[
                "json",
                "os",
                "typing",
                "requests",
                "math",
                "re",
            ],
        )

        graph.add_module(
            module="modules.dialogue",
            dependencies=["modules.ai"],
        )

        graph.add_module(
            module="nova_gui",
            dependencies=["modules.ai"],
        )

        predictor = ChangePredictor(graph)
        risk_engine = RiskEngine(graph)

        self.planner = RefactorPlanner(
            predictor,
            risk_engine,
        )

    def test_create_plan(self) -> None:
        plan = self.planner.create_plan("modules.ai")

        self.assertEqual(plan.target, "modules.ai")
        self.assertEqual(plan.risk, "MEDIUM")
        self.assertGreaterEqual(plan.estimated_minutes, 5)
        self.assertEqual(len(plan.affected_modules), 2)

    def test_format_plan(self) -> None:
        report = self.planner.format_plan("modules.ai")

        self.assertIn("SAFE REFACTOR PLAN", report)
        self.assertIn("modules.ai", report)
        self.assertIn("Execution Plan", report)

    def test_unknown_module(self) -> None:
        with self.assertRaises(ValueError):
            self.planner.create_plan("modules.fake")


if __name__ == "__main__":
    unittest.main()