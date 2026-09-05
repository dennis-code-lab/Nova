"""
Nova Engine v132
Engineering Explainer Tests
Verifies that EngineeringExplainer:

Uses the authoritative engineering score.
Uses the risk engine correctly.
Uses the evidence engine correctly.
Applies the correct recommendation thresholds.
Preserves module and score information.
Includes risk and engineering evidence.
Produces the expected human-readable explanation.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from modules.engineering_evidence import EngineeringEvidence
from modules.engineering_explainer import EngineeringExplainer
from modules.engineering_score import EngineeringScore


class TestEngineeringExplainer(unittest.TestCase):

    def setUp(self) -> None:
        self.score_engine = Mock()
        self.risk_engine = Mock()
        self.evidence_engine = Mock()

        self.explainer = EngineeringExplainer(
            self.score_engine,
            self.risk_engine,
            self.evidence_engine,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def configure(
        self,
        score: float,
        risk: str = "LOW",
        evidence_items: list[str] | None = None,
        module: str = "modules.example",
    ) -> None:
        self.score_engine.calculate.return_value = EngineeringScore(
            module=module,
            score=score,
            dependency_count=5,
            risk=risk,
        )

        assessment = Mock()
        assessment.risk = risk
        self.risk_engine.analyze.return_value = assessment

        self.evidence_engine.collect.return_value = EngineeringEvidence(
            module=module,
            dependency_count=5,
            affected_modules=2,
            risk=risk,
            evidence=evidence_items or [
                "Direct dependencies: 5",
                "Affected modules: 2",
                f"Risk classification: {risk}",
            ],
        )

    # ==========================================================
    # Return value
    # ==========================================================

    def test_explain_returns_string(self) -> None:
        self.configure(score=5.0)

        result = self.explainer.explain("modules.example")

        self.assertIsInstance(result, str)

    def test_explain_returns_non_empty_string(self) -> None:
        self.configure(score=5.0)

        result = self.explainer.explain("modules.example")

        self.assertTrue(result)

    # ==========================================================
    # HIGH recommendation
    # ==========================================================

    def test_score_three_recommends_refactoring(self) -> None:
        self.configure(score=3.0)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Consider refactoring into smaller modules.",
            result,
        )

    def test_score_below_three_recommends_refactoring(self) -> None:
        self.configure(score=2.5)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Consider refactoring into smaller modules.",
            result,
        )

    # ==========================================================
    # MEDIUM recommendation
    # ==========================================================

    def test_score_six_recommends_monitoring(self) -> None:
        self.configure(score=6.0)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Monitor architectural complexity.",
            result,
        )

    def test_score_between_three_and_six_recommends_monitoring(self) -> None:
        self.configure(score=4.5)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Monitor architectural complexity.",
            result,
        )

    # ==========================================================
    # LOW recommendation
    # ==========================================================

    def test_score_above_six_requires_no_immediate_refactoring(self) -> None:
        self.configure(score=6.1)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "No immediate refactoring required.",
            result,
        )

    def test_score_ten_requires_no_immediate_refactoring(self) -> None:
        self.configure(score=10.0)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "No immediate refactoring required.",
            result,
        )

    # ==========================================================
    # Module and score output
    # ==========================================================

    def test_explanation_contains_module_name(self) -> None:
        self.configure(
            score=5.0,
            module="modules.engineering_runtime",
        )

        result = self.explainer.explain(
            "modules.engineering_runtime"
        )

        self.assertIn(
            "Module : modules.engineering_runtime",
            result,
        )

    def test_explanation_contains_engineering_score(self) -> None:
        self.configure(score=5.5)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Engineering Score : 5.5/10",
            result,
        )

    def test_explanation_contains_low_score(self) -> None:
        self.configure(score=2.5)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Engineering Score : 2.5/10",
            result,
        )

    def test_explanation_contains_perfect_score(self) -> None:
        self.configure(score=10.0)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Engineering Score : 10.0/10",
            result,
        )

    # ==========================================================
    # Risk output
    # ==========================================================

    def test_explanation_contains_low_risk(self) -> None:
        self.configure(
            score=8.0,
            risk="LOW",
        )

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Risk : LOW",
            result,
        )

    def test_explanation_contains_medium_risk(self) -> None:
        self.configure(
            score=5.0,
            risk="MEDIUM",
        )

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Risk : MEDIUM",
            result,
        )

    def test_explanation_contains_high_risk(self) -> None:
        self.configure(
            score=2.0,
            risk="HIGH",
        )

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Risk : HIGH",
            result,
        )

    # ==========================================================
    # Evidence output
    # ==========================================================

    def test_explanation_contains_dependency_evidence(self) -> None:
        self.configure(
            score=5.0,
            evidence_items=[
                "Direct dependencies: 7",
                "Affected modules: 4",
                "Risk classification: LOW",
            ],
        )

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "• Direct dependencies: 7",
            result,
        )

    def test_explanation_contains_affected_modules_evidence(self) -> None:
        self.configure(
            score=5.0,
            evidence_items=[
                "Direct dependencies: 7",
                "Affected modules: 12",
                "Risk classification: LOW",
            ],
        )

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "• Affected modules: 12",
            result,
        )

    def test_explanation_contains_risk_evidence(self) -> None:
        self.configure(
            score=5.0,
            risk="HIGH",
            evidence_items=[
                "Direct dependencies: 7",
                "Affected modules: 12",
                "Risk classification: HIGH",
            ],
        )

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "• Risk classification: HIGH",
            result,
        )

    def test_all_evidence_items_are_included(self) -> None:
        evidence = [
            "Direct dependencies: 9",
            "Affected modules: 14",
            "Risk classification: MEDIUM",
        ]

        self.configure(
            score=5.0,
            risk="MEDIUM",
            evidence_items=evidence,
        )

        result = self.explainer.explain("modules.example")

        for item in evidence:
            with self.subTest(item=item):
                self.assertIn(
                    f"• {item}",
                    result,
                )

    def test_evidence_items_are_formatted_with_bullet(self) -> None:
        self.configure(
            score=5.0,
            evidence_items=[
                "First evidence",
                "Second evidence",
            ],
        )

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "• First evidence",
            result,
        )
        self.assertIn(
            "• Second evidence",
            result,
        )

    def test_empty_evidence_is_supported(self) -> None:
        self.configure(
            score=5.0,
            evidence_items=[],
        )

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Evidence",
            result,
        )

    # ==========================================================
    # Engine integration
    # ==========================================================

    def test_score_engine_is_called_with_module(self) -> None:
        self.configure(score=5.0)

        self.explainer.explain("modules.example")

        self.score_engine.calculate.assert_called_once_with(
            "modules.example"
        )

    def test_risk_engine_is_called_with_module(self) -> None:
        self.configure(score=5.0)

        self.explainer.explain("modules.example")

        self.risk_engine.analyze.assert_called_once_with(
            "modules.example"
        )

    def test_evidence_engine_is_called_with_module(self) -> None:
        self.configure(score=5.0)

        self.explainer.explain("modules.example")

        self.evidence_engine.collect.assert_called_once_with(
            "modules.example"
        )

    def test_all_engines_are_called_once(self) -> None:
        self.configure(score=5.0)

        self.explainer.explain("modules.example")

        self.assertEqual(
            self.score_engine.calculate.call_count,
            1,
        )
        self.assertEqual(
            self.risk_engine.analyze.call_count,
            1,
        )
        self.assertEqual(
            self.evidence_engine.collect.call_count,
            1,
        )

    # ==========================================================
    # Different module names
    # ==========================================================

    def test_explainer_supports_different_module_names(self) -> None:
        module_names = [
            "modules.simple",
            "modules.engineering_score",
            "modules.engineering_runtime",
        ]

        for module_name in module_names:
            with self.subTest(module=module_name):
                self.configure(
                    score=5.0,
                    module=module_name,
                )

                result = self.explainer.explain(module_name)

                self.assertIn(
                    f"Module : {module_name}",
                    result,
                )

    # ==========================================================
    # Recommendation independence
    # ==========================================================

    def test_low_score_with_low_risk_still_recommends_refactoring(
        self,
    ) -> None:
        self.configure(
            score=2.0,
            risk="LOW",
        )

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Consider refactoring into smaller modules.",
            result,
        )

    def test_high_score_with_high_risk_still_uses_score_recommendation(
        self,
    ) -> None:
        self.configure(
            score=9.0,
            risk="HIGH",
        )

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "No immediate refactoring required.",
            result,
        )

    # ==========================================================
    # Formatting
    # ==========================================================

    def test_explanation_contains_title(self) -> None:
        self.configure(score=5.0)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "ENGINEERING EXPLANATION",
            result,
        )

    def test_explanation_contains_evidence_heading(self) -> None:
        self.configure(score=5.0)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Evidence",
            result,
        )

    def test_explanation_contains_recommendation_heading(self) -> None:
        self.configure(score=5.0)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "Recommendation",
            result,
        )

    def test_explanation_contains_section_separators(self) -> None:
        self.configure(score=5.0)

        result = self.explainer.explain("modules.example")

        self.assertIn(
            "=" * 50,
            result,
        )
        self.assertIn(
            "-" * 50,
            result,
        )

    def test_explanation_contains_all_major_sections(self) -> None:
        self.configure(
            score=5.0,
            risk="MEDIUM",
            evidence_items=[
                "Direct dependencies: 5",
                "Affected modules: 2",
                "Risk classification: MEDIUM",
            ],
        )

        result = self.explainer.explain("modules.example")

        sections = [
            "ENGINEERING EXPLANATION",
            "Module : modules.example",
            "Engineering Score : 5.0/10",
            "Risk : MEDIUM",
            "Evidence",
            "• Direct dependencies: 5",
            "• Affected modules: 2",
            "• Risk classification: MEDIUM",
            "Recommendation",
            "Monitor architectural complexity.",
        ]

        for section in sections:
            with self.subTest(section=section):
                self.assertIn(
                    section,
                    result,
                )

    # ==========================================================
    # End-to-end scenarios
    # ==========================================================

    def test_high_risk_refactor_scenario(self) -> None:
        self.configure(
            score=2.5,
            risk="HIGH",
            evidence_items=[
                "Direct dependencies: 16",
                "Affected modules: 15",
                "Risk classification: HIGH",
            ],
        )

        result = self.explainer.explain("modules.high_risk")

        self.assertIn(
            "Module : modules.high_risk",
            result,
        )
        self.assertIn(
            "Engineering Score : 2.5/10",
            result,
        )
        self.assertIn(
            "Risk : HIGH",
            result,
        )
        self.assertIn(
            "• Direct dependencies: 16",
            result,
        )
        self.assertIn(
            "• Affected modules: 15",
            result,
        )
        self.assertIn(
            "Consider refactoring into smaller modules.",
            result,
        )

    def test_medium_complexity_scenario(self) -> None:
        self.configure(
            score=5.5,
            risk="MEDIUM",
            evidence_items=[
                "Direct dependencies: 10",
                "Affected modules: 8",
                "Risk classification: MEDIUM",
            ],
        )

        result = self.explainer.explain("modules.coupled")

        self.assertIn(
            "Module : modules.coupled",
            result,
        )
        self.assertIn(
            "Engineering Score : 5.5/10",
            result,
        )
        self.assertIn(
            "Risk : MEDIUM",
            result,
        )
        self.assertIn(
            "• Direct dependencies: 10",
            result,
        )
        self.assertIn(
            "• Affected modules: 8",
            result,
        )
        self.assertIn(
            "Monitor architectural complexity.",
            result,
        )

    def test_healthy_module_scenario(self) -> None:
        self.configure(
            score=9.0,
            risk="LOW",
            evidence_items=[
                "Direct dependencies: 2",
                "Affected modules: 1",
                "Risk classification: LOW",
            ],
        )

        result = self.explainer.explain("modules.healthy")

        self.assertIn(
            "Module : modules.healthy",
            result,
        )
        self.assertIn(
            "Engineering Score : 9.0/10",
            result,
        )
        self.assertIn(
            "Risk : LOW",
            result,
        )
        self.assertIn(
            "• Direct dependencies: 2",
            result,
        )
        self.assertIn(
            "• Affected modules: 1",
            result,
        )
        self.assertIn(
            "No immediate refactoring required.",
            result,
        )


if __name__ == "__main__":
    unittest.main()