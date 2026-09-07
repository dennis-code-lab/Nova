"""
Nova Engine v135
Autonomous Engineering Planner Tests

Verifies RoadmapItem construction and AutonomousEngineeringPlanner
roadmap generation, filtering, prioritization, runtime handling,
and formatted roadmap output.
"""

import unittest
from unittest.mock import Mock

from modules.engineering_planner_v2 import (
    AutonomousEngineeringPlanner,
    RoadmapItem,
)


class TestRoadmapItem(unittest.TestCase):

    def test_roadmap_item_stores_all_fields(self):
        item = RoadmapItem(
            module="modules.engineering_health",
            priority="HIGH",
            engineering_score=3.5,
            estimated_effort="4-6 hours",
            recommendation="Refactor module.",
        )

        self.assertEqual(
            item.module,
            "modules.engineering_health",
        )
        self.assertEqual(item.priority, "HIGH")
        self.assertEqual(item.engineering_score, 3.5)
        self.assertEqual(
            item.estimated_effort,
            "4-6 hours",
        )
        self.assertEqual(
            item.recommendation,
            "Refactor module.",
        )

    def test_roadmap_item_is_dataclass(self):
        item = RoadmapItem(
            "module",
            "LOW",
            8.0,
            "1 hour",
            "Monitor.",
        )

        self.assertEqual(
            item.__dataclass_fields__.keys(),
            {
                "module",
                "priority",
                "engineering_score",
                "estimated_effort",
                "recommendation",
            },
        )


class TestAutonomousEngineeringPlanner(unittest.TestCase):

    def make_planner(
        self,
        modules=None,
        completed=None,
        scores=None,
        advice=None,
    ):
        graph = Mock()
        graph.modules.return_value = (
            modules if modules is not None else []
        )

        score_engine = Mock()

        def calculate(module):
            score = (scores or {}).get(module, 5.0)

            result = Mock()
            result.score = score
            return result

        score_engine.calculate.side_effect = calculate

        advisor = Mock()

        def advise(module):
            result = Mock()
            module_advice = (advice or {}).get(module, {})

            result.priority = module_advice.get(
                "priority",
                "MEDIUM",
            )
            result.estimated_effort = module_advice.get(
                "estimated_effort",
                "4-6 engineering hours",
            )
            result.recommendation = module_advice.get(
                "recommendation",
                "Review engineering complexity.",
            )

            return result

        advisor.advise.side_effect = advise

        history = Mock()
        history.completed_modules.return_value = (
            completed if completed is not None else []
        )

        planner = AutonomousEngineeringPlanner(
            graph,
            score_engine,
            advisor,
            history,
        )

        return planner, graph, score_engine, advisor, history

    # =====================================================
    # Initialization
    # =====================================================

    def test_init_stores_graph(self):
        planner, graph, score_engine, advisor, history = (
            self.make_planner()
        )

        self.assertIs(planner.graph, graph)

    def test_init_stores_score_engine(self):
        planner, graph, score_engine, advisor, history = (
            self.make_planner()
        )

        self.assertIs(
            planner.score_engine,
            score_engine,
        )

    def test_init_stores_advisor(self):
        planner, graph, score_engine, advisor, history = (
            self.make_planner()
        )

        self.assertIs(
            planner.advisor,
            advisor,
        )

    def test_init_stores_history(self):
        planner, graph, score_engine, advisor, history = (
            self.make_planner()
        )

        self.assertIs(
            planner.history,
            history,
        )

    # =====================================================
    # Basic Generation
    # =====================================================

    def test_generate_returns_list(self):
        planner, *_ = self.make_planner(
            modules=[],
            completed=["modules.engineering_health"],
        )

        result = planner.generate()

        self.assertIsInstance(result, list)

    def test_generate_returns_roadmap_items(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_health",
            ],
            scores={
                "modules.engineering_health": 4.0,
            },
            advice={
                "modules.engineering_health": {
                    "priority": "HIGH",
                    "estimated_effort": "8 hours",
                    "recommendation": "Refactor.",
                }
            },
        )

        result = planner.generate()

        self.assertTrue(
            all(
                isinstance(item, RoadmapItem)
                for item in result
            )
        )

    def test_generate_includes_engineering_module(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_health",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertIn(
            "modules.engineering_health",
            modules,
        )

    def test_generate_uses_score_engine(self):
        planner, _, score_engine, _, _ = (
            self.make_planner(
                modules=[
                    "modules.engineering_health",
                ],
                completed=[
                    "modules.engineering_runtime",
                ],
            )
        )

        planner.generate()

        score_engine.calculate.assert_called_once_with(
            "modules.engineering_health"
        )

    def test_generate_uses_advisor(self):
        planner, _, _, advisor, _ = (
            self.make_planner(
                modules=[
                    "modules.engineering_health",
                ],
                completed=[
                    "modules.engineering_runtime",
                ],
            )
        )

        planner.generate()

        advisor.advise.assert_called_once_with(
            "modules.engineering_health"
        )

    def test_generate_copies_score_into_roadmap_item(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_health",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
            scores={
                "modules.engineering_health": 2.75,
            },
        )

        result = planner.generate()

        item = result[0]

        self.assertEqual(
            item.engineering_score,
            2.75,
        )

    def test_generate_copies_advisor_fields(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_health",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
            advice={
                "modules.engineering_health": {
                    "priority": "LOW",
                    "estimated_effort": "1-2 hours",
                    "recommendation": "Monitor module.",
                }
            },
        )

        result = planner.generate()

        item = result[0]

        self.assertEqual(item.priority, "LOW")
        self.assertEqual(
            item.estimated_effort,
            "1-2 hours",
        )
        self.assertEqual(
            item.recommendation,
            "Monitor module.",
        )

    # =====================================================
    # Completed Module Filtering
    # =====================================================

    def test_generate_skips_completed_modules(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_health",
                "modules.engineering_score",
            ],
            completed=[
                "modules.engineering_health",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertNotIn(
            "modules.engineering_health",
            modules,
        )

    def test_generate_keeps_incomplete_modules(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_health",
                "modules.engineering_score",
            ],
            completed=[
                "modules.engineering_health",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertIn(
            "modules.engineering_score",
            modules,
        )

    def test_generate_does_not_score_completed_module(self):
        planner, _, score_engine, _, _ = (
            self.make_planner(
                modules=[
                    "modules.engineering_health",
                    "modules.engineering_score",
                ],
                completed=[
                    "modules.engineering_health",
                    "modules.engineering_runtime",
                ],
            )
        )

        planner.generate()

        called_modules = [
            call.args[0]
            for call in score_engine.calculate.call_args_list
        ]

        self.assertNotIn(
            "modules.engineering_health",
            called_modules,
        )

    # =====================================================
    # Module Prefix Filtering
    # =====================================================

    def test_generate_skips_non_engineering_module(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.random_feature",
                "modules.engineering_health",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertNotIn(
            "modules.random_feature",
            modules,
        )

    def test_generate_accepts_risk_engine_module(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.risk_engine",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertIn(
            "modules.risk_engine",
            modules,
        )

    def test_generate_accepts_change_predictor_module(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.change_predictor",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertIn(
            "modules.change_predictor",
            modules,
        )

    def test_generate_accepts_dependency_analyzer_module(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.dependency_analyzer",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertIn(
            "modules.dependency_analyzer",
            modules,
        )

    def test_generate_accepts_impact_engine_module(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.impact_engine",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertIn(
            "modules.impact_engine",
            modules,
        )

    def test_generate_accepts_refactor_planner_module(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.refactor_planner",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertIn(
            "modules.refactor_planner",
            modules,
        )

    def test_generate_accepts_logger_module(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.logger",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertIn(
            "modules.logger",
            modules,
        )

    def test_generate_accepts_orchestrator_module(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.orchestrator",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertIn(
            "modules.orchestrator",
            modules,
        )

    # =====================================================
    # Foundation Runtime Handling
    # =====================================================

    def test_generate_includes_runtime_explicitly(self):
        planner, *_ = self.make_planner(
            modules=[],
            completed=[],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertIn(
            "modules.engineering_runtime",
            modules,
        )

    def test_generate_runtime_has_high_priority(self):
        planner, *_ = self.make_planner(
            modules=[],
            completed=[],
        )

        result = planner.generate()

        runtime = next(
            item
            for item in result
            if item.module == "modules.engineering_runtime"
        )

        self.assertEqual(
            runtime.priority,
            "HIGH",
        )

    def test_generate_runtime_has_zero_score(self):
        planner, *_ = self.make_planner(
            modules=[],
            completed=[],
        )

        result = planner.generate()

        runtime = next(
            item
            for item in result
            if item.module == "modules.engineering_runtime"
        )

        self.assertEqual(
            runtime.engineering_score,
            0.0,
        )

    def test_generate_runtime_has_expected_effort(self):
        planner, *_ = self.make_planner(
            modules=[],
            completed=[],
        )

        result = planner.generate()

        runtime = next(
            item
            for item in result
            if item.module == "modules.engineering_runtime"
        )

        self.assertEqual(
            runtime.estimated_effort,
            "2-3 engineering hours",
        )

    def test_generate_runtime_has_expected_recommendation(self):
        planner, *_ = self.make_planner(
            modules=[],
            completed=[],
        )

        result = planner.generate()

        runtime = next(
            item
            for item in result
            if item.module == "modules.engineering_runtime"
        )

        self.assertEqual(
            runtime.recommendation,
            "Split this module into smaller feature-specific modules.",
        )

    def test_generate_skips_completed_runtime(self):
        planner, *_ = self.make_planner(
            modules=[],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertNotIn(
            "modules.engineering_runtime",
            modules,
        )

    def test_generate_skips_runtime_when_already_in_graph(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_runtime",
            ],
            completed=[],
        )

        result = planner.generate()

        runtime_items = [
            item
            for item in result
            if item.module == "modules.engineering_runtime"
        ]

        self.assertEqual(
            len(runtime_items),
            1,
        )

    # =====================================================
    # Priority Ordering
    # =====================================================

    def test_generate_sorts_high_before_medium(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_medium",
                "modules.engineering_high",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
            scores={
                "modules.engineering_medium": 1.0,
                "modules.engineering_high": 9.0,
            },
            advice={
                "modules.engineering_medium": {
                    "priority": "MEDIUM",
                },
                "modules.engineering_high": {
                    "priority": "HIGH",
                },
            },
        )

        result = planner.generate()

        self.assertEqual(
            result[0].module,
            "modules.engineering_high",
        )

    def test_generate_sorts_medium_before_low(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_low",
                "modules.engineering_medium",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
            scores={
                "modules.engineering_low": 1.0,
                "modules.engineering_medium": 9.0,
            },
            advice={
                "modules.engineering_low": {
                    "priority": "LOW",
                },
                "modules.engineering_medium": {
                    "priority": "MEDIUM",
                },
            },
        )

        result = planner.generate()

        self.assertEqual(
            result[0].module,
            "modules.engineering_medium",
        )

    def test_generate_sorts_low_last(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_low",
                "modules.engineering_high",
                "modules.engineering_medium",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
            advice={
                "modules.engineering_low": {
                    "priority": "LOW",
                },
                "modules.engineering_high": {
                    "priority": "HIGH",
                },
                "modules.engineering_medium": {
                    "priority": "MEDIUM",
                },
            },
        )

        result = planner.generate()

        self.assertEqual(
            [item.priority for item in result],
            [
                "HIGH",
                "MEDIUM",
                "LOW",
            ],
        )

    def test_generate_sorts_unknown_priority_after_known_priorities(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_unknown",
                "modules.engineering_high",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
            advice={
                "modules.engineering_unknown": {
                    "priority": "CRITICAL",
                },
                "modules.engineering_high": {
                    "priority": "HIGH",
                },
            },
        )

        result = planner.generate()

        self.assertEqual(
            result[0].module,
            "modules.engineering_high",
        )
        self.assertEqual(
            result[1].module,
            "modules.engineering_unknown",
        )

    def test_generate_sorts_lower_score_first_with_same_priority(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_high_score",
                "modules.engineering_low_score",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
            scores={
                "modules.engineering_high_score": 9.0,
                "modules.engineering_low_score": 2.0,
            },
            advice={
                "modules.engineering_high_score": {
                    "priority": "HIGH",
                },
                "modules.engineering_low_score": {
                    "priority": "HIGH",
                },
            },
        )

        result = planner.generate()

        self.assertEqual(
            result[0].module,
            "modules.engineering_low_score",
        )
        self.assertEqual(
            result[1].module,
            "modules.engineering_high_score",
        )

    def test_generate_runtime_can_sort_before_other_high_priority_items(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_high",
            ],
            completed=[],
            scores={
                "modules.engineering_high": 5.0,
            },
            advice={
                "modules.engineering_high": {
                    "priority": "HIGH",
                }
            },
        )

        result = planner.generate()

        self.assertEqual(
            result[0].module,
            "modules.engineering_runtime",
        )

    # =====================================================
    # Empty and Mixed Inputs
    # =====================================================

    def test_generate_empty_graph_returns_runtime(self):
        planner, *_ = self.make_planner(
            modules=[],
            completed=[],
        )

        result = planner.generate()

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0].module,
            "modules.engineering_runtime",
        )

    def test_generate_empty_graph_with_completed_runtime_returns_empty(self):
        planner, *_ = self.make_planner(
            modules=[],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.generate()

        self.assertEqual(result, [])

    def test_generate_mixed_graph_filters_correctly(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_health",
                "modules.random_module",
                "modules.risk_engine",
                "modules.engineering_runtime",
            ],
            completed=[
                "modules.risk_engine",
            ],
        )

        result = planner.generate()

        modules = [item.module for item in result]

        self.assertIn(
            "modules.engineering_health",
            modules,
        )
        self.assertIn(
            "modules.engineering_runtime",
            modules,
        )
        self.assertNotIn(
            "modules.random_module",
            modules,
        )
        self.assertNotIn(
            "modules.risk_engine",
            modules,
        )

    # =====================================================
    # Formatting
    # =====================================================

    def test_format_roadmap_contains_header(self):
        planner, *_ = self.make_planner(
            modules=[],
            completed=[],
        )

        result = planner.format_roadmap()

        self.assertIn(
            "AUTONOMOUS ENGINEERING ROADMAP",
            result,
        )

    def test_format_roadmap_contains_separator(self):
        planner, *_ = self.make_planner(
            modules=[],
            completed=[],
        )

        result = planner.format_roadmap()

        self.assertIn(
            "=" * 60,
            result,
        )

    def test_format_roadmap_contains_module_details(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_health",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
            scores={
                "modules.engineering_health": 3.5,
            },
            advice={
                "modules.engineering_health": {
                    "priority": "HIGH",
                    "estimated_effort": "8 hours",
                    "recommendation": "Refactor module.",
                }
            },
        )

        result = planner.format_roadmap()

        self.assertIn(
            "modules.engineering_health",
            result,
        )
        self.assertIn(
            "Priority : HIGH",
            result,
        )
        self.assertIn(
            "Score    : 3.5/10",
            result,
        )
        self.assertIn(
            "Effort   : 8 hours",
            result,
        )
        self.assertIn(
            "Action   : Refactor module.",
            result,
        )

    def test_format_roadmap_limit_zero_returns_header_only(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_health",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.format_roadmap(limit=0)

        self.assertIn(
            "AUTONOMOUS ENGINEERING ROADMAP",
            result,
        )
        self.assertNotIn(
            "modules.engineering_health",
            result,
        )

    def test_format_roadmap_limit_one_returns_one_item(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_one",
                "modules.engineering_two",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.format_roadmap(limit=1)

        self.assertIn(
            "1. modules.engineering_one",
            result,
        )
        self.assertNotIn(
            "2. modules.engineering_two",
            result,
        )

    def test_format_roadmap_large_limit_returns_all_items(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_one",
                "modules.engineering_two",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.format_roadmap(limit=100)

        self.assertIn(
            "modules.engineering_one",
            result,
        )
        self.assertIn(
            "modules.engineering_two",
            result,
        )

    def test_format_roadmap_numbering_starts_at_one(self):
        planner, *_ = self.make_planner(
            modules=[
                "modules.engineering_health",
            ],
            completed=[
                "modules.engineering_runtime",
            ],
        )

        result = planner.format_roadmap()

        self.assertIn(
            "1. modules.engineering_health",
            result,
        )


if __name__ == "__main__":
    unittest.main()