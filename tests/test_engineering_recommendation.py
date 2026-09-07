"""
Nova Engine v136
Engineering Recommendation Engine Tests

Verifies Recommendation construction and
EngineeringRecommendation candidate ranking,
score integration, filtering, limits, and
empty-graph behavior.
"""

import unittest
from unittest.mock import Mock

from modules.engineering_recommendation import (
    EngineeringRecommendation,
    Recommendation,
)


class TestRecommendation(unittest.TestCase):

    def test_recommendation_stores_all_fields(self):
        recommendation = Recommendation(
            module="modules.engineering_health",
            risk="HIGH",
            dependencies=8,
            engineering_score=3.5,
        )

        self.assertEqual(
            recommendation.module,
            "modules.engineering_health",
        )
        self.assertEqual(
            recommendation.risk,
            "HIGH",
        )
        self.assertEqual(
            recommendation.dependencies,
            8,
        )
        self.assertEqual(
            recommendation.engineering_score,
            3.5,
        )

    def test_recommendation_is_dataclass(self):
        recommendation = Recommendation(
            "module",
            "LOW",
            2,
            7.5,
        )

        self.assertEqual(
            recommendation.__dataclass_fields__.keys(),
            {
                "module",
                "risk",
                "dependencies",
                "engineering_score",
            },
        )


class TestEngineeringRecommendation(unittest.TestCase):

    def make_engine(
        self,
        modules=None,
        nodes=None,
        scores=None,
    ):
        graph = Mock()

        graph.modules.return_value = (
            modules if modules is not None else []
        )

        nodes = nodes or {}
        scores = scores or {}

        def get_node(module):
            return nodes.get(module, Mock())

        graph.get_node.side_effect = get_node

        score_engine = Mock()

        def calculate(module):
            score_data = scores.get(
                module,
                {
                    "risk": "MEDIUM",
                    "dependency_count": 2,
                    "score": 5.0,
                },
            )

            result = Mock()
            result.risk = score_data["risk"]
            result.dependency_count = score_data[
                "dependency_count"
            ]
            result.score = score_data["score"]

            return result

        score_engine.calculate.side_effect = calculate

        engine = EngineeringRecommendation(
            graph,
            score_engine,
        )

        return (
            engine,
            graph,
            score_engine,
        )

    def test_initialization_stores_graph(self):
        engine, graph, score_engine = (
            self.make_engine()
        )

        self.assertIs(
            engine.graph,
            graph,
        )

    def test_initialization_stores_score_engine(self):
        engine, graph, score_engine = (
            self.make_engine()
        )

        self.assertIs(
            engine.score_engine,
            score_engine,
        )

    def test_top_candidates_returns_list(self):
        engine, _, _ = self.make_engine(
            modules=[
                "modules.engineering_health",
            ],
        )

        result = engine.top_candidates()

        self.assertIsInstance(
            result,
            list,
        )

    def test_top_candidates_returns_recommendation_objects(self):
        engine, _, _ = self.make_engine(
            modules=[
                "modules.engineering_health",
                "modules.engineering_graph",
            ],
        )

        result = engine.top_candidates()

        self.assertTrue(result)

        for item in result:
            self.assertIsInstance(
                item,
                Recommendation,
            )

    def test_module_name_is_preserved(self):
        module = "modules.engineering_health"

        engine, _, _ = self.make_engine(
            modules=[module],
        )

        result = engine.top_candidates()

        self.assertEqual(
            result[0].module,
            module,
        )

    def test_risk_is_taken_from_score(self):
        module = "modules.engineering_health"

        engine, _, _ = self.make_engine(
            modules=[module],
            scores={
                module: {
                    "risk": "CRITICAL",
                    "dependency_count": 4,
                    "score": 2.5,
                },
            },
        )

        result = engine.top_candidates()

        self.assertEqual(
            result[0].risk,
            "CRITICAL",
        )

    def test_dependency_count_is_taken_from_score(self):
        module = "modules.engineering_health"

        engine, _, _ = self.make_engine(
            modules=[module],
            scores={
                module: {
                    "risk": "HIGH",
                    "dependency_count": 11,
                    "score": 4.0,
                },
            },
        )

        result = engine.top_candidates()

        self.assertEqual(
            result[0].dependencies,
            11,
        )

    def test_engineering_score_is_taken_from_score(self):
        module = "modules.engineering_health"

        engine, _, _ = self.make_engine(
            modules=[module],
            scores={
                module: {
                    "risk": "MEDIUM",
                    "dependency_count": 3,
                    "score": 6.75,
                },
            },
        )

        result = engine.top_candidates()

        self.assertEqual(
            result[0].engineering_score,
            6.75,
        )

    def test_score_engine_calculate_is_called_for_valid_module(
        self,
    ):
        module = "modules.engineering_health"

        engine, _, score_engine = self.make_engine(
            modules=[module],
        )

        engine.top_candidates()

        score_engine.calculate.assert_called_once_with(
            module
        )

    def test_graph_get_node_is_called_for_each_module(self):
        modules = [
            "modules.engineering_health",
            "modules.engineering_graph",
            "modules.engineering_score",
        ]

        engine, graph, _ = self.make_engine(
            modules=modules,
        )

        engine.top_candidates()

        self.assertEqual(
            graph.get_node.call_count,
            len(modules),
        )

        graph.get_node.assert_any_call(
            "modules.engineering_health"
        )
        graph.get_node.assert_any_call(
            "modules.engineering_graph"
        )
        graph.get_node.assert_any_call(
            "modules.engineering_score"
        )

    def test_modules_with_missing_nodes_are_skipped(self):
        module = "modules.engineering_health"

        engine, graph, score_engine = self.make_engine(
            modules=[module],
            nodes={module: None},
        )

        result = engine.top_candidates()

        self.assertEqual(result, [])

        score_engine.calculate.assert_not_called()

    def test_valid_modules_are_not_skipped(self):
        module = "modules.engineering_health"

        engine, graph, score_engine = self.make_engine(
            modules=[module],
            nodes={module: object()},
        )

        result = engine.top_candidates()

        self.assertEqual(len(result), 1)

        score_engine.calculate.assert_called_once_with(
            module
        )

    def test_highest_dependency_count_ranks_first(self):
        first = "modules.engineering_first"
        second = "modules.engineering_second"

        engine, _, _ = self.make_engine(
            modules=[second, first],
            scores={
                first: {
                    "risk": "HIGH",
                    "dependency_count": 10,
                    "score": 8.0,
                },
                second: {
                    "risk": "MEDIUM",
                    "dependency_count": 3,
                    "score": 1.0,
                },
            },
        )

        result = engine.top_candidates()

        self.assertEqual(
            result[0].module,
            first,
        )
        self.assertEqual(
            result[1].module,
            second,
        )

    def test_lower_score_wins_when_dependencies_are_equal(
        self,
    ):
        first = "modules.engineering_first"
        second = "modules.engineering_second"

        engine, _, _ = self.make_engine(
            modules=[first, second],
            scores={
                first: {
                    "risk": "HIGH",
                    "dependency_count": 5,
                    "score": 8.0,
                },
                second: {
                    "risk": "MEDIUM",
                    "dependency_count": 5,
                    "score": 2.0,
                },
            },
        )

        result = engine.top_candidates()

        self.assertEqual(
            result[0].module,
            second,
        )
        self.assertEqual(
            result[1].module,
            first,
        )

    def test_dependency_count_takes_precedence_over_score(self):
        first = "modules.engineering_first"
        second = "modules.engineering_second"

        engine, _, _ = self.make_engine(
            modules=[first, second],
            scores={
                first: {
                    "risk": "HIGH",
                    "dependency_count": 6,
                    "score": 9.0,
                },
                second: {
                    "risk": "LOW",
                    "dependency_count": 5,
                    "score": 1.0,
                },
            },
        )

        result = engine.top_candidates()

        self.assertEqual(
            result[0].module,
            first,
        )

    def test_three_candidates_are_sorted_correctly(self):
        modules = [
            "modules.engineering_a",
            "modules.engineering_b",
            "modules.engineering_c",
        ]

        engine, _, _ = self.make_engine(
            modules=modules,
            scores={
                "modules.engineering_a": {
                    "risk": "LOW",
                    "dependency_count": 2,
                    "score": 1.0,
                },
                "modules.engineering_b": {
                    "risk": "HIGH",
                    "dependency_count": 7,
                    "score": 9.0,
                },
                "modules.engineering_c": {
                    "risk": "MEDIUM",
                    "dependency_count": 7,
                    "score": 3.0,
                },
            },
        )

        result = engine.top_candidates()

        self.assertEqual(
            [item.module for item in result],
            [
                "modules.engineering_c",
                "modules.engineering_b",
                "modules.engineering_a",
            ],
        )

    def test_default_limit_is_five(self):
        modules = [
            "modules.engineering_1",
            "modules.engineering_2",
            "modules.engineering_3",
            "modules.engineering_4",
            "modules.engineering_5",
            "modules.engineering_6",
            "modules.engineering_7",
        ]

        engine, _, _ = self.make_engine(
            modules=modules,
        )

        result = engine.top_candidates()

        self.assertEqual(
            len(result),
            5,
        )

    def test_custom_limit_is_respected(self):
        modules = [
            "modules.engineering_1",
            "modules.engineering_2",
            "modules.engineering_3",
            "modules.engineering_4",
        ]

        engine, _, _ = self.make_engine(
            modules=modules,
        )

        result = engine.top_candidates(
            limit=2,
        )

        self.assertEqual(
            len(result),
            2,
        )

    def test_limit_one_returns_one_candidate(self):
        modules = [
            "modules.engineering_1",
            "modules.engineering_2",
            "modules.engineering_3",
        ]

        engine, _, _ = self.make_engine(
            modules=modules,
        )

        result = engine.top_candidates(
            limit=1,
        )

        self.assertEqual(
            len(result),
            1,
        )

    def test_limit_zero_returns_empty_list(self):
        modules = [
            "modules.engineering_1",
            "modules.engineering_2",
        ]

        engine, _, _ = self.make_engine(
            modules=modules,
        )

        result = engine.top_candidates(
            limit=0,
        )

        self.assertEqual(
            result,
            [],
        )

    def test_large_limit_returns_all_candidates(self):
        modules = [
            "modules.engineering_1",
            "modules.engineering_2",
        ]

        engine, _, _ = self.make_engine(
            modules=modules,
        )

        result = engine.top_candidates(
            limit=100,
        )

        self.assertEqual(
            len(result),
            2,
        )

    def test_empty_graph_returns_empty_list(self):
        engine, _, score_engine = (
            self.make_engine(
                modules=[],
            )
        )

        result = engine.top_candidates()

        self.assertEqual(
            result,
            [],
        )

        score_engine.calculate.assert_not_called()

    def test_graph_with_only_missing_nodes_returns_empty_list(
        self,
    ):
        modules = [
            "modules.engineering_missing_a",
            "modules.engineering_missing_b",
        ]

        engine, _, score_engine = self.make_engine(
            modules=modules,
            nodes={
                modules[0]: None,
                modules[1]: None,
            },
        )

        result = engine.top_candidates()

        self.assertEqual(
            result,
            [],
        )

        score_engine.calculate.assert_not_called()

    def test_all_valid_modules_are_processed(self):
        modules = [
            "modules.engineering_a",
            "modules.engineering_b",
            "modules.engineering_c",
        ]

        engine, _, score_engine = self.make_engine(
            modules=modules,
        )

        engine.top_candidates()

        self.assertEqual(
            score_engine.calculate.call_count,
            len(modules),
        )

        for module in modules:
            score_engine.calculate.assert_any_call(
                module
            )

    def test_graph_order_does_not_determine_ranking(self):
        first = "modules.engineering_first"
        second = "modules.engineering_second"

        engine, _, _ = self.make_engine(
            modules=[second, first],
            scores={
                first: {
                    "risk": "HIGH",
                    "dependency_count": 10,
                    "score": 2.0,
                },
                second: {
                    "risk": "LOW",
                    "dependency_count": 1,
                    "score": 9.0,
                },
            },
        )

        result = engine.top_candidates()

        self.assertEqual(
            result[0].module,
            first,
        )

    def test_multiple_missing_nodes_do_not_affect_valid_candidates(
        self,
    ):
        valid = "modules.engineering_valid"
        missing = "modules.engineering_missing"

        engine, _, _ = self.make_engine(
            modules=[missing, valid],
            nodes={
                missing: None,
                valid: object(),
            },
            scores={
                valid: {
                    "risk": "HIGH",
                    "dependency_count": 4,
                    "score": 3.0,
                },
            },
        )

        result = engine.top_candidates()

        self.assertEqual(
            len(result),
            1,
        )
        self.assertEqual(
            result[0].module,
            valid,
        )

    def test_recommendation_values_remain_consistent_after_sorting(
        self,
    ):
        first = "modules.engineering_first"
        second = "modules.engineering_second"

        engine, _, _ = self.make_engine(
            modules=[first, second],
            scores={
                first: {
                    "risk": "HIGH",
                    "dependency_count": 10,
                    "score": 8.0,
                },
                second: {
                    "risk": "LOW",
                    "dependency_count": 4,
                    "score": 2.0,
                },
            },
        )

        result = engine.top_candidates()

        self.assertEqual(
            result[0].module,
            first,
        )
        self.assertEqual(
            result[0].risk,
            "HIGH",
        )
        self.assertEqual(
            result[0].dependencies,
            10,
        )
        self.assertEqual(
            result[0].engineering_score,
            8.0,
        )

        self.assertEqual(
            result[1].module,
            second,
        )
        self.assertEqual(
            result[1].risk,
            "LOW",
        )
        self.assertEqual(
            result[1].dependencies,
            4,
        )
        self.assertEqual(
            result[1].engineering_score,
            2.0,
        )


if __name__ == "__main__":
    unittest.main()