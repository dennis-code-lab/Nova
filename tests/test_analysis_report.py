"""
Nova Engine v106
Analysis Report Generator - Test Suite

Verifies that AnalysisReport exposes the authoritative
EngineeringScoreEngine score.
"""

from __future__ import annotations

import unittest

from modules.analysis_report import AnalysisReport
from modules.engineering_graph import EngineeringGraph
from modules.engineering_score import EngineeringScoreEngine
from modules.risk_engine import RiskEngine


class TestAnalysisReport(unittest.TestCase):

    def setUp(self) -> None:
        graph = EngineeringGraph()

        graph.add_module(
            module="main",
            dependencies=["modules.memory"],
        )

        self.graph = graph

    def test_report_generation(self) -> None:
        report = AnalysisReport(self.graph).generate()

        self.assertIn(
            "ENGINEERING IMPACT REPORT",
            report,
        )
        self.assertIn(
            "main",
            report,
        )
        self.assertIn(
            "modules.memory",
            report,
        )
        self.assertIn(
            "LOW",
            report,
        )

    def test_report_uses_authoritative_engineering_score(self) -> None:
        report = AnalysisReport(self.graph).generate()

        risk_engine = RiskEngine(self.graph)
        score_engine = EngineeringScoreEngine(
            self.graph,
            risk_engine,
        )

        expected = score_engine.calculate("main")

        self.assertIn(
            f"Engineering Score: {expected.score}",
            report,
        )


if __name__ == "__main__":
    unittest.main()