"""
Nova Engine v123
Engineering Overview Tests

Verifies that EngineeringOverview:
- delegates health analysis correctly,
- displays project-wide engineering health,
- displays risk distribution,
- requests the top five refactor candidates,
- formats candidate information correctly,
- handles an empty recommendation list,
- produces a complete overview report.
"""

from __future__ import annotations

import unittest

from modules.engineering_overview import EngineeringOverview


class MockHealthReport:

    def __init__(
        self,
        total_modules=25,
        engineering_health=82.5,
        low_risk=10,
        medium_risk=8,
        high_risk=7,
    ):
        self.total_modules = total_modules
        self.engineering_health = engineering_health
        self.low_risk = low_risk
        self.medium_risk = medium_risk
        self.high_risk = high_risk


class MockHealth:

    def __init__(self, report):
        self.report = report
        self.calls = 0

    def analyze(self):
        self.calls += 1
        return self.report


class MockCandidate:

    def __init__(
        self,
        module,
        risk,
        dependencies,
        engineering_score,
    ):
        self.module = module
        self.risk = risk
        self.dependencies = dependencies
        self.engineering_score = engineering_score


class MockRecommendation:

    def __init__(self, candidates):
        self.candidates = candidates
        self.calls = []

    def top_candidates(self, limit):
        self.calls.append(limit)
        return list(self.candidates)


class MockGraph:
    pass


class MockScoreEngine:
    pass


class TestEngineeringOverview(unittest.TestCase):

    def setUp(self):
        self.report = MockHealthReport()

        self.candidates = [
            MockCandidate(
                module="modules.alpha",
                risk="HIGH",
                dependencies=15,
                engineering_score=2.5,
            ),
            MockCandidate(
                module="modules.beta",
                risk="MEDIUM",
                dependencies=9,
                engineering_score=4.0,
            ),
            MockCandidate(
                module="modules.gamma",
                risk="LOW",
                dependencies=3,
                engineering_score=7.5,
            ),
        ]

        self.overview = EngineeringOverview(
            MockGraph(),
            MockScoreEngine(),
        )

        self.health = MockHealth(self.report)
        self.recommendation = MockRecommendation(
            self.candidates
        )

        self.overview.health = self.health
        self.overview.recommendation = self.recommendation

    # ------------------------------------------------------
    # Health delegation
    # ------------------------------------------------------

    def test_generate_calls_health_analysis(self):
        self.overview.generate()

        self.assertEqual(
            self.health.calls,
            1,
        )

    # ------------------------------------------------------
    # Basic report information
    # ------------------------------------------------------

    def test_report_contains_title(self):
        result = self.overview.generate()

        self.assertIn(
            "NOVA ENGINEERING OVERVIEW",
            result,
        )

    def test_report_contains_module_count(self):
        result = self.overview.generate()

        self.assertIn(
            "Modules Analysed   : 25",
            result,
        )

    def test_report_contains_engineering_health(self):
        result = self.overview.generate()

        self.assertIn(
            "Engineering Health : 82.5%",
            result,
        )

    # ------------------------------------------------------
    # Risk summary
    # ------------------------------------------------------

    def test_report_contains_low_risk_count(self):
        result = self.overview.generate()

        self.assertIn(
            "LOW    : 10",
            result,
        )

    def test_report_contains_medium_risk_count(self):
        result = self.overview.generate()

        self.assertIn(
            "MEDIUM : 8",
            result,
        )

    def test_report_contains_high_risk_count(self):
        result = self.overview.generate()

        self.assertIn(
            "HIGH   : 7",
            result,
        )

    # ------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------

    def test_requests_top_five_candidates(self):
        self.overview.generate()

        self.assertEqual(
            self.recommendation.calls,
            [5],
        )

    def test_report_contains_candidate_module_names(self):
        result = self.overview.generate()

        self.assertIn(
            "1. modules.alpha",
            result,
        )

        self.assertIn(
            "2. modules.beta",
            result,
        )

        self.assertIn(
            "3. modules.gamma",
            result,
        )

    def test_report_contains_candidate_risks(self):
        result = self.overview.generate()

        self.assertIn(
            "Risk: HIGH",
            result,
        )

        self.assertIn(
            "Risk: MEDIUM",
            result,
        )

        self.assertIn(
            "Risk: LOW",
            result,
        )

    def test_report_contains_candidate_dependencies(self):
        result = self.overview.generate()

        self.assertIn(
            "Dependencies: 15",
            result,
        )

        self.assertIn(
            "Dependencies: 9",
            result,
        )

        self.assertIn(
            "Dependencies: 3",
            result,
        )

    def test_report_contains_candidate_engineering_scores(self):
        result = self.overview.generate()

        self.assertIn(
            "Engineering Score: 2.5",
            result,
        )

        self.assertIn(
            "Engineering Score: 4.0",
            result,
        )

        self.assertIn(
            "Engineering Score: 7.5",
            result,
        )

    # ------------------------------------------------------
    # Empty recommendations
    # ------------------------------------------------------

    def test_empty_candidates_display_no_recommendations(self):
        self.overview.recommendation = MockRecommendation([])

        result = self.overview.generate()

        self.assertIn(
            "No recommendations available.",
            result,
        )

    def test_empty_candidates_do_not_display_candidate_entries(self):
        self.overview.recommendation = MockRecommendation([])

        result = self.overview.generate()

        self.assertNotIn(
            "1. modules.",
            result,
        )

    # ------------------------------------------------------
    # Report completion
    # ------------------------------------------------------

    def test_report_contains_completion_message(self):
        result = self.overview.generate()

        self.assertIn(
            "Engineering overview complete.",
            result,
        )

    def test_report_has_expected_section_headers(self):
        result = self.overview.generate()

        self.assertIn(
            "Risk Summary",
            result,
        )

        self.assertIn(
            "Top Refactor Candidates",
            result,
        )

    # ------------------------------------------------------
    # Candidate ordering
    # ------------------------------------------------------

    def test_candidates_preserve_recommendation_order(self):
        result = self.overview.generate()

        alpha_position = result.index(
            "1. modules.alpha"
        )
        beta_position = result.index(
            "2. modules.beta"
        )
        gamma_position = result.index(
            "3. modules.gamma"
        )

        self.assertLess(
            alpha_position,
            beta_position,
        )

        self.assertLess(
            beta_position,
            gamma_position,
        )


if __name__ == "__main__":
    unittest.main()