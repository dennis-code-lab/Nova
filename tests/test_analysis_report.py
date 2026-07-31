"""
Nova Engine v84
Analysis Report Generator - Test Suite

test_analysis_report.py
"""

import unittest

from modules.analysis_report import AnalysisReport
from modules.engineering_graph import EngineeringGraph


class TestAnalysisReport(unittest.TestCase):

    def test_report_generation(self):
        graph = EngineeringGraph()

        graph.add_module(
            module="main",
            dependencies=["modules.memory"],
            impact_score=9,
            risk="LOW",
        )

        report = AnalysisReport(graph).generate()

        self.assertIn("ENGINEERING IMPACT REPORT", report)
        self.assertIn("main", report)
        self.assertIn("modules.memory", report)
        self.assertIn("LOW", report)


if __name__ == "__main__":
    unittest.main()