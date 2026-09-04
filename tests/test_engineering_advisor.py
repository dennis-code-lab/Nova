"""
Nova Engine v130
Engineering Advisor Tests

Verifies that EngineeringAdvisor:

- Calculates advice from the authoritative engineering score.
- Applies the correct priority and effort thresholds.
- Applies dependency-based recommendations.
- Calculates and caps the expected score.
- Preserves the requested module name.
- Calls the score and evidence engines correctly.
- Formats the advice into a readable CLI report.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from modules.engineering_advisor import EngineeringAdvice, EngineeringAdvisor
from modules.engineering_evidence import EngineeringEvidence
from modules.engineering_score import EngineeringScore


class TestEngineeringAdvisor(unittest.TestCase):

    def setUp(self) -> None:
        self.score_engine = Mock()
        self.evidence_engine = Mock()

        self.advisor = EngineeringAdvisor(
            self.score_engine,
            self.evidence_engine,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def configure(
        self,
        score: float,
        dependency_count: int,
        risk: str = "LOW",
        module: str = "modules.example",
    ) -> None:
        self.score_engine.calculate.return_value = EngineeringScore(
            module=module,
            score=score,
            dependency_count=dependency_count,
            risk=risk,
        )

        self.evidence_engine.collect.return_value = EngineeringEvidence(
            module=module,
            dependency_count=dependency_count,
            affected_modules=0,
            risk=risk,
            evidence=[],
        )

    # ==========================================================
    # Advice data model
    # ==========================================================

    def test_advice_returns_engineering_advice(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertIsInstance(result, EngineeringAdvice)

    def test_advice_preserves_module_name(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.module, "modules.example")

    # ==========================================================
    # HIGH priority
    # ==========================================================

    def test_score_three_is_high_priority(self) -> None:
        self.configure(
            score=3.0,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.priority, "HIGH")

    def test_score_below_three_is_high_priority(self) -> None:
        self.configure(
            score=2.9,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.priority, "HIGH")

    def test_high_priority_effort(self) -> None:
        self.configure(
            score=3.0,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(
            result.estimated_effort,
            "2-3 engineering hours",
        )

    # ==========================================================
    # MEDIUM priority
    # ==========================================================

    def test_score_six_is_medium_priority(self) -> None:
        self.configure(
            score=6.0,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.priority, "MEDIUM")

    def test_score_between_three_and_six_is_medium_priority(self) -> None:
        self.configure(
            score=4.5,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.priority, "MEDIUM")

    def test_medium_priority_effort(self) -> None:
        self.configure(
            score=6.0,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(
            result.estimated_effort,
            "1-2 engineering hours",
        )

    # ==========================================================
    # LOW priority
    # ==========================================================

    def test_score_above_six_is_low_priority(self) -> None:
        self.configure(
            score=6.1,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.priority, "LOW")

    def test_score_ten_is_low_priority(self) -> None:
        self.configure(
            score=10.0,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.priority, "LOW")

    def test_low_priority_effort(self) -> None:
        self.configure(
            score=10.0,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(
            result.estimated_effort,
            "No immediate work required",
        )

    # ==========================================================
    # Dependency recommendations
    # ==========================================================

    def test_fifteen_dependencies_recommends_splitting(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=15,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(
            result.recommendation,
            "Split this module into smaller feature-specific modules.",
        )

    def test_more_than_fifteen_dependencies_recommends_splitting(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=20,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(
            result.recommendation,
            "Split this module into smaller feature-specific modules.",
        )

    def test_fourteen_dependencies_recommends_reducing_coupling(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=14,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(
            result.recommendation,
            "Reduce coupling and simplify dependencies.",
        )

    def test_eight_dependencies_recommends_reducing_coupling(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=8,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(
            result.recommendation,
            "Reduce coupling and simplify dependencies.",
        )

    def test_seven_dependencies_recommends_maintaining_architecture(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=7,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(
            result.recommendation,
            "Maintain current architecture.",
        )

    def test_zero_dependencies_recommends_maintaining_architecture(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=0,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(
            result.recommendation,
            "Maintain current architecture.",
        )

    # ==========================================================
    # Expected score
    # ==========================================================

    def test_expected_score_adds_three(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.expected_score, 8.0)

    def test_expected_score_handles_decimal_score(self) -> None:
        self.configure(
            score=5.5,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.expected_score, 8.5)

    def test_expected_score_is_capped_at_ten(self) -> None:
        self.configure(
            score=8.0,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.expected_score, 10.0)

    def test_expected_score_remains_ten_for_perfect_score(self) -> None:
        self.configure(
            score=10.0,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.expected_score, 10.0)

    def test_expected_score_rounds_to_one_decimal_place(self) -> None:
        self.configure(
            score=5.25,
            dependency_count=5,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.expected_score, 8.2)

    def test_expected_score_never_exceeds_ten(self) -> None:
        for score in (7.1, 8.0, 8.5, 9.0, 10.0):
            with self.subTest(score=score):
                self.configure(
                    score=score,
                    dependency_count=5,
                )

                result = self.advisor.advise("modules.example")

                self.assertLessEqual(result.expected_score, 10.0)

    # ==========================================================
    # Engine integration
    # ==========================================================

    def test_score_engine_is_called_with_module(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=5,
        )

        self.advisor.advise("modules.example")

        self.score_engine.calculate.assert_called_once_with(
            "modules.example"
        )

    def test_evidence_engine_is_called_with_module(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=5,
        )

        self.advisor.advise("modules.example")

        self.evidence_engine.collect.assert_called_once_with(
            "modules.example"
        )

    def test_both_engines_are_called_once(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=5,
        )

        self.advisor.advise("modules.example")

        self.assertEqual(
            self.score_engine.calculate.call_count,
            1,
        )
        self.assertEqual(
            self.evidence_engine.collect.call_count,
            1,
        )

    # ==========================================================
    # Different module names
    # ==========================================================

    def test_advisor_supports_different_module_names(self) -> None:
        module_names = [
            "modules.simple",
            "modules.engineering_score",
            "modules.engineering_runtime",
        ]

        for module_name in module_names:
            with self.subTest(module=module_name):
                self.configure(
                    score=5.0,
                    dependency_count=5,
                    module=module_name,
                )

                result = self.advisor.advise(module_name)

                self.assertEqual(
                    result.module,
                    module_name,
                )

    # ==========================================================
    # Recommendation branch independence
    # ==========================================================

    def test_high_score_can_still_have_split_recommendation(self) -> None:
        self.configure(
            score=9.0,
            dependency_count=15,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.priority, "LOW")
        self.assertEqual(
            result.recommendation,
            "Split this module into smaller feature-specific modules.",
        )

    def test_low_score_can_have_maintain_recommendation(self) -> None:
        self.configure(
            score=2.0,
            dependency_count=2,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.priority, "HIGH")
        self.assertEqual(
            result.recommendation,
            "Maintain current architecture.",
        )

    def test_medium_score_can_have_split_recommendation(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=15,
        )

        result = self.advisor.advise("modules.example")

        self.assertEqual(result.priority, "MEDIUM")
        self.assertEqual(
            result.recommendation,
            "Split this module into smaller feature-specific modules.",
        )

    # ==========================================================
    # Formatting
    # ==========================================================

    def test_format_advice_contains_title(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=5,
        )

        report = self.advisor.format_advice("modules.example")

        self.assertIn(
            "ENGINEERING ADVISOR",
            report,
        )

    def test_format_advice_contains_module(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=5,
        )

        report = self.advisor.format_advice("modules.example")

        self.assertIn(
            "modules.example",
            report,
        )

    def test_format_advice_contains_priority(self) -> None:
        self.configure(
            score=3.0,
            dependency_count=5,
        )

        report = self.advisor.format_advice("modules.example")

        self.assertIn(
            "Priority : HIGH",
            report,
        )

    def test_format_advice_contains_effort(self) -> None:
        self.configure(
            score=3.0,
            dependency_count=5,
        )

        report = self.advisor.format_advice("modules.example")

        self.assertIn(
            "Estimated Effort : 2-3 engineering hours",
            report,
        )

    def test_format_advice_contains_recommendation_heading(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=5,
        )

        report = self.advisor.format_advice("modules.example")

        self.assertIn(
            "Recommendation",
            report,
        )

    def test_format_advice_contains_recommendation(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=5,
        )

        report = self.advisor.format_advice("modules.example")

        self.assertIn(
            "Maintain current architecture.",
            report,
        )

    def test_format_advice_contains_expected_score(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=5,
        )

        report = self.advisor.format_advice("modules.example")

        self.assertIn(
            "Estimated Engineering Score After Refactor : 8.0/10",
            report,
        )

    def test_format_advice_formats_expected_score_with_one_decimal(self) -> None:
        self.configure(
            score=5.5,
            dependency_count=5,
        )

        report = self.advisor.format_advice("modules.example")

        self.assertIn(
            "Estimated Engineering Score After Refactor : 8.5/10",
            report,
        )

    def test_format_advice_contains_all_major_sections(self) -> None:
        self.configure(
            score=5.0,
            dependency_count=5,
        )

        report = self.advisor.format_advice("modules.example")

        sections = [
            "ENGINEERING ADVISOR",
            "Module : modules.example",
            "Priority : MEDIUM",
            "Estimated Effort : 1-2 engineering hours",
            "Recommendation",
            "Maintain current architecture.",
            "Estimated Engineering Score After Refactor : 8.0/10",
        ]

        for section in sections:
            with self.subTest(section=section):
                self.assertIn(section, report)

    # ==========================================================
    # End-to-end scenarios
    # ==========================================================

    def test_high_risk_refactor_scenario(self) -> None:
        self.configure(
            score=2.5,
            dependency_count=16,
            risk="HIGH",
        )

        result = self.advisor.advise("modules.high_risk")

        self.assertEqual(result.module, "modules.high_risk")
        self.assertEqual(result.priority, "HIGH")
        self.assertEqual(
            result.estimated_effort,
            "2-3 engineering hours",
        )
        self.assertEqual(result.expected_score, 5.5)
        self.assertEqual(
            result.recommendation,
            "Split this module into smaller feature-specific modules.",
        )

    def test_medium_coupling_scenario(self) -> None:
        self.configure(
            score=5.5,
            dependency_count=10,
            risk="MEDIUM",
        )

        result = self.advisor.advise("modules.coupled")

        self.assertEqual(result.module, "modules.coupled")
        self.assertEqual(result.priority, "MEDIUM")
        self.assertEqual(
            result.estimated_effort,
            "1-2 engineering hours",
        )
        self.assertEqual(result.expected_score, 8.5)
        self.assertEqual(
            result.recommendation,
            "Reduce coupling and simplify dependencies.",
        )

    def test_healthy_module_scenario(self) -> None:
        self.configure(
            score=9.0,
            dependency_count=3,
            risk="LOW",
        )

        result = self.advisor.advise("modules.healthy")

        self.assertEqual(result.module, "modules.healthy")
        self.assertEqual(result.priority, "LOW")
        self.assertEqual(
            result.estimated_effort,
            "No immediate work required",
        )
        self.assertEqual(result.expected_score, 10.0)
        self.assertEqual(
            result.recommendation,
            "Maintain current architecture.",
        )


if __name__ == "__main__":
    unittest.main()