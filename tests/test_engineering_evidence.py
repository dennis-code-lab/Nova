"""
Nova Engine v131
Engineering Evidence Engine Tests
Verifies that EngineeringEvidenceEngine:

Returns the correct EngineeringEvidence data model.
Preserves the requested module name.
Rejects unknown modules.
Counts direct dependencies correctly.
Uses ChangePredictor affected-module evidence.
Uses RiskEngine risk classification.
Builds the expected evidence messages.
Calls the predictor and risk engine correctly.
Handles different modules and evidence scenarios.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from modules.engineering_evidence import (
    EngineeringEvidence,
    EngineeringEvidenceEngine,
)


class TestEngineeringEvidenceEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.graph = Mock()
        self.predictor = Mock()
        self.risk_engine = Mock()

        self.engine = EngineeringEvidenceEngine(
            self.graph,
            self.predictor,
            self.risk_engine,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    def configure(
        self,
        dependency_count: int,
        affected_count: int,
        risk: str = "LOW",
        module: str = "modules.example",
    ) -> None:
        node = Mock()
        node.dependencies = [
            f"dependency_{index}"
            for index in range(dependency_count)
        ]

        self.graph.get_node.return_value = node

        self.predictor.predict.return_value = {
            "affected_count": affected_count,
        }

        assessment = Mock()
        assessment.risk = risk
        self.risk_engine.analyze.return_value = assessment

    # ==========================================================
    # Data model
    # ==========================================================

    def test_collect_returns_engineering_evidence(self) -> None:
        self.configure(
            dependency_count=5,
            affected_count=3,
        )

        result = self.engine.collect("modules.example")

        self.assertIsInstance(result, EngineeringEvidence)

    def test_collect_preserves_module_name(self) -> None:
        self.configure(
            dependency_count=5,
            affected_count=3,
        )

        result = self.engine.collect("modules.example")

        self.assertEqual(
            result.module,
            "modules.example",
        )

    # ==========================================================
    # Unknown modules
    # ==========================================================

    def test_unknown_module_raises_value_error(self) -> None:
        self.graph.get_node.return_value = None

        with self.assertRaises(ValueError):
            self.engine.collect("modules.unknown")

    def test_unknown_module_does_not_call_predictor(self) -> None:
        self.graph.get_node.return_value = None

        with self.assertRaises(ValueError):
            self.engine.collect("modules.unknown")

        self.predictor.predict.assert_not_called()

    def test_unknown_module_does_not_call_risk_engine(self) -> None:
        self.graph.get_node.return_value = None

        with self.assertRaises(ValueError):
            self.engine.collect("modules.unknown")

        self.risk_engine.analyze.assert_not_called()

    # ==========================================================
    # Dependency evidence
    # ==========================================================

    def test_dependency_count_is_calculated_from_node(self) -> None:
        self.configure(
            dependency_count=7,
            affected_count=2,
        )

        result = self.engine.collect("modules.example")

        self.assertEqual(
            result.dependency_count,
            7,
        )

    def test_zero_dependencies_are_supported(self) -> None:
        self.configure(
            dependency_count=0,
            affected_count=2,
        )

        result = self.engine.collect("modules.example")

        self.assertEqual(
            result.dependency_count,
            0,
        )

    def test_large_dependency_count_is_preserved(self) -> None:
        self.configure(
            dependency_count=25,
            affected_count=2,
        )

        result = self.engine.collect("modules.example")

        self.assertEqual(
            result.dependency_count,
            25,
        )

    # ==========================================================
    # Affected-module evidence
    # ==========================================================

    def test_affected_module_count_comes_from_predictor(self) -> None:
        self.configure(
            dependency_count=5,
            affected_count=12,
        )

        result = self.engine.collect("modules.example")

        self.assertEqual(
            result.affected_modules,
            12,
        )

    def test_zero_affected_modules_are_supported(self) -> None:
        self.configure(
            dependency_count=5,
            affected_count=0,
        )

        result = self.engine.collect("modules.example")

        self.assertEqual(
            result.affected_modules,
            0,
        )

    def test_large_affected_module_count_is_preserved(self) -> None:
        self.configure(
            dependency_count=5,
            affected_count=100,
        )

        result = self.engine.collect("modules.example")

        self.assertEqual(
            result.affected_modules,
            100,
        )

    # ==========================================================
    # Risk evidence
    # ==========================================================

    def test_low_risk_is_preserved(self) -> None:
        self.configure(
            dependency_count=5,
            affected_count=3,
            risk="LOW",
        )

        result = self.engine.collect("modules.example")

        self.assertEqual(
            result.risk,
            "LOW",
        )

    def test_medium_risk_is_preserved(self) -> None:
        self.configure(
            dependency_count=5,
            affected_count=3,
            risk="MEDIUM",
        )

        result = self.engine.collect("modules.example")

        self.assertEqual(
            result.risk,
            "MEDIUM",
        )

    def test_high_risk_is_preserved(self) -> None:
        self.configure(
            dependency_count=5,
            affected_count=3,
            risk="HIGH",
        )

        result = self.engine.collect("modules.example")

        self.assertEqual(
            result.risk,
            "HIGH",
        )

    # ==========================================================
    # Evidence messages
    # ==========================================================

    def test_evidence_contains_dependency_count(self) -> None:
        self.configure(
            dependency_count=7,
            affected_count=3,
        )

        result = self.engine.collect("modules.example")

        self.assertIn(
            "Direct dependencies: 7",
            result.evidence,
        )

    def test_evidence_contains_affected_module_count(self) -> None:
        self.configure(
            dependency_count=7,
            affected_count=11,
        )

        result = self.engine.collect("modules.example")

        self.assertIn(
            "Affected modules: 11",
            result.evidence,
        )

    def test_evidence_contains_risk_classification(self) -> None:
        self.configure(
            dependency_count=7,
            affected_count=11,
            risk="HIGH",
        )

        result = self.engine.collect("modules.example")

        self.assertIn(
            "Risk classification: HIGH",
            result.evidence,
        )

    def test_evidence_contains_exactly_three_items(self) -> None:
        self.configure(
            dependency_count=7,
            affected_count=11,
            risk="HIGH",
        )

        result = self.engine.collect("modules.example")

        self.assertEqual(
            len(result.evidence),
            3,
        )

    def test_evidence_messages_are_in_expected_order(self) -> None:
        self.configure(
            dependency_count=7,
            affected_count=11,
            risk="HIGH",
        )

        result = self.engine.collect("modules.example")

        self.assertEqual(
            result.evidence,
            [
                "Direct dependencies: 7",
                "Affected modules: 11",
                "Risk classification: HIGH",
            ],
        )

    # ==========================================================
    # Engine integration
    # ==========================================================

    def test_graph_is_called_with_module_name(self) -> None:
        self.configure(
            dependency_count=5,
            affected_count=3,
        )

        self.engine.collect("modules.example")

        self.graph.get_node.assert_called_once_with(
            "modules.example"
        )

    def test_predictor_is_called_with_module_name(self) -> None:
        self.configure(
            dependency_count=5,
            affected_count=3,
        )

        self.engine.collect("modules.example")

        self.predictor.predict.assert_called_once_with(
            "modules.example"
        )

    def test_risk_engine_is_called_with_module_name(self) -> None:
        self.configure(
            dependency_count=5,
            affected_count=3,
        )

        self.engine.collect("modules.example")

        self.risk_engine.analyze.assert_called_once_with(
            "modules.example"
        )

    def test_all_engines_are_called_once(self) -> None:
        self.configure(
            dependency_count=5,
            affected_count=3,
        )

        self.engine.collect("modules.example")

        self.assertEqual(
            self.graph.get_node.call_count,
            1,
        )
        self.assertEqual(
            self.predictor.predict.call_count,
            1,
        )
        self.assertEqual(
            self.risk_engine.analyze.call_count,
            1,
        )

    # ==========================================================
    # Different module names
    # ==========================================================

    def test_collect_supports_different_module_names(self) -> None:
        module_names = [
            "modules.simple",
            "modules.engineering_score",
            "modules.engineering_runtime",
        ]

        for module_name in module_names:
            with self.subTest(module=module_name):
                self.configure(
                    dependency_count=5,
                    affected_count=3,
                )

                result = self.engine.collect(module_name)

                self.assertEqual(
                    result.module,
                    module_name,
                )

                self.graph.get_node.assert_called_with(
                    module_name
                )

                self.predictor.predict.assert_called_with(
                    module_name
                )

                self.risk_engine.analyze.assert_called_with(
                    module_name
                )

    # ==========================================================
    # Combined evidence scenarios
    # ==========================================================

    def test_high_dependency_high_risk_scenario(self) -> None:
        self.configure(
            dependency_count=20,
            affected_count=15,
            risk="HIGH",
        )

        result = self.engine.collect("modules.high_risk")

        self.assertEqual(
            result.module,
            "modules.high_risk",
        )
        self.assertEqual(
            result.dependency_count,
            20,
        )
        self.assertEqual(
            result.affected_modules,
            15,
        )
        self.assertEqual(
            result.risk,
            "HIGH",
        )
        self.assertEqual(
            result.evidence,
            [
                "Direct dependencies: 20",
                "Affected modules: 15",
                "Risk classification: HIGH",
            ],
        )

    def test_medium_dependency_medium_risk_scenario(self) -> None:
        self.configure(
            dependency_count=10,
            affected_count=8,
            risk="MEDIUM",
        )

        result = self.engine.collect("modules.coupled")

        self.assertEqual(
            result.module,
            "modules.coupled",
        )
        self.assertEqual(
            result.dependency_count,
            10,
        )
        self.assertEqual(
            result.affected_modules,
            8,
        )
        self.assertEqual(
            result.risk,
            "MEDIUM",
        )

    def test_healthy_module_scenario(self) -> None:
        self.configure(
            dependency_count=2,
            affected_count=1,
            risk="LOW",
        )

        result = self.engine.collect("modules.healthy")

        self.assertEqual(
            result.module,
            "modules.healthy",
        )
        self.assertEqual(
            result.dependency_count,
            2,
        )
        self.assertEqual(
            result.affected_modules,
            1,
        )
        self.assertEqual(
            result.risk,
            "LOW",
        )
        self.assertEqual(
            result.evidence,
            [
                "Direct dependencies: 2",
                "Affected modules: 1",
                "Risk classification: LOW",
            ],
        )


if __name__ == "__main__":
    unittest.main()