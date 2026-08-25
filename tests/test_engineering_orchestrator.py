"""
Nova Engine v84
Unit Tests - Engineering Orchestrator

Verifies pipeline orchestration, report assembly, text output formatting,
and unknown target handling.
"""

from __future__ import annotations

import unittest

from modules.change_predictor import ChangePredictor
from modules.engineering_graph import EngineeringGraph
from modules.engineering_orchestrator import EngineeringOrchestrator
from modules.refactor_planner import RefactorPlanner
from modules.risk_engine import RiskEngine


class TestEngineeringOrchestrator(unittest.TestCase):

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
            impact_score=4.0,
        )

        graph.add_module(
            module="modules.dialogue",
            dependencies=["modules.ai"],
            impact_score=8.0,
        )

        graph.add_module(
            module="nova_gui",
            dependencies=["modules.ai"],
            impact_score=9.0,
        )

        predictor = ChangePredictor(graph)
        risk_engine = RiskEngine(graph)
        planner = RefactorPlanner(
            predictor,
            risk_engine,
        )

        self.orchestrator = EngineeringOrchestrator(
            predictor,
            risk_engine,
            planner,
        )

    def test_report_generation(self) -> None:
        report = self.orchestrator.analyze_request("modules.ai")

        self.assertEqual(report.target, "modules.ai")
        self.assertEqual(report.risk, "MEDIUM")
        self.assertEqual(len(report.affected_modules), 2)

    def test_formatted_report(self) -> None:
        text = self.orchestrator.format_report("modules.ai")

        self.assertIn("NOVA ENGINEERING REPORT", text)
        self.assertIn("modules.ai", text)
        self.assertIn("Execution Workflow", text)

    def test_unknown_module(self) -> None:
        with self.assertRaises(ValueError):
            self.orchestrator.analyze_request("modules.fake")


if __name__ == "__main__":
    unittest.main()
