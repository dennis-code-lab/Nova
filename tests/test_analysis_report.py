"""
Nova Engine v106
Analysis Report Generator - Test Suite

Verifies that AnalysisReport exposes the authoritative
EngineeringScoreEngine score rather than legacy impact_score.
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
            impact_score=9.0,
            risk="LOW",
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

    def test_report_does_not_use_legacy_impact_score_as_engineering_score(
        self,
    ) -> None:
        report = AnalysisReport(self.graph).generate()

        risk_engine = RiskEngine(self.graph)
        score_engine = EngineeringScoreEngine(
            self.graph,
            risk_engine,
        )

        authoritative_score = score_engine.calculate("main").score
        node = self.graph.get_node("main")
        self.assertIsNotNone(node)
        legacy_score = node.impact_score

        self.assertNotEqual(
            authoritative_score,
            legacy_score,
        )

        self.assertNotIn(
            f"Engineering Score: {legacy_score}",
            report,
        )


if __name__ == "__main__":
    unittest.main()