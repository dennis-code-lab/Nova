"""
Nova Engine v122
Engineering Command Router Tests

Verifies that EngineeringCommandRouter:
- routes exact engineering commands correctly,
- passes module names to the correct runtime methods,
- records completion through the runtime,
- returns runtime results unchanged,
- handles case-insensitive commands,
- returns None for unsupported commands.
"""

from __future__ import annotations

import unittest

from modules.engineering_command_router import EngineeringCommandRouter


class MockRuntime:

    def __init__(self):
        self.calls = []

    def dashboard(self):
        self.calls.append(("dashboard",))
        return "dashboard-result"

    def progress(self):
        self.calls.append(("progress",))
        return "progress-result"

    def roadmap(self):
        self.calls.append(("roadmap",))
        return "roadmap-result"

    def overview(self):
        self.calls.append(("overview",))
        return "overview-result"

    def forecast(self):
        self.calls.append(("forecast",))
        return "forecast-result"

    def decision(self):
        self.calls.append(("decision",))
        return "decision-result"

    def simulate(self, module):
        self.calls.append(("simulate", module))
        return "simulate-result"

    def report(self, module=None):
        self.calls.append(("report", module))
        return "report-result"

    def plan(self, module):
        self.calls.append(("plan", module))
        return "plan-result"

    def predict(self, module):
        self.calls.append(("predict", module))
        return "predict-result"

    def risk(self, module):
        self.calls.append(("risk", module))
        return "risk-result"

    def explain(self, module):
        self.calls.append(("explain", module))
        return "explain-result"

    def advise(self, module):
        self.calls.append(("advise", module))
        return "advise-result"

    def complete(self, module):
        self.calls.append(("complete", module))


class TestEngineeringCommandRouter(unittest.TestCase):

    def setUp(self):
        self.runtime = MockRuntime()
        self.router = EngineeringCommandRouter(self.runtime)

    # ------------------------------------------------------
    # Exact command routing
    # ------------------------------------------------------

    def test_dashboard_routes_to_runtime(self):
        result = self.router.execute("engineering dashboard")

        self.assertEqual(result, "dashboard-result")
        self.assertEqual(
            self.runtime.calls,
            [("dashboard",)],
        )

    def test_progress_routes_to_runtime(self):
        result = self.router.execute("engineering progress")

        self.assertEqual(result, "progress-result")
        self.assertEqual(
            self.runtime.calls,
            [("progress",)],
        )

    def test_roadmap_routes_to_runtime(self):
        result = self.router.execute("engineering roadmap")

        self.assertEqual(result, "roadmap-result")
        self.assertEqual(
            self.runtime.calls,
            [("roadmap",)],
        )

    def test_overview_routes_to_runtime(self):
        result = self.router.execute("engineering overview")

        self.assertEqual(result, "overview-result")
        self.assertEqual(
            self.runtime.calls,
            [("overview",)],
        )

    def test_forecast_routes_to_runtime(self):
        result = self.router.execute("engineering forecast")

        self.assertEqual(result, "forecast-result")
        self.assertEqual(
            self.runtime.calls,
            [("forecast",)],
        )

    def test_decision_routes_to_runtime(self):
        result = self.router.execute("engineering decision")

        self.assertEqual(result, "decision-result")
        self.assertEqual(
            self.runtime.calls,
            [("decision",)],
        )

    # ------------------------------------------------------
    # Parameterized commands
    # ------------------------------------------------------

    def test_simulate_passes_module(self):
        result = self.router.execute(
            "engineering simulate modules.example"
        )

        self.assertEqual(result, "simulate-result")
        self.assertEqual(
            self.runtime.calls,
            [("simulate", "modules.example")],
        )

    def test_report_passes_module(self):
        result = self.router.execute(
            "engineering report modules.example"
        )

        self.assertEqual(result, "report-result")
        self.assertEqual(
            self.runtime.calls,
            [("report", "modules.example")],
        )

    def test_plan_passes_module(self):
        result = self.router.execute(
            "engineering plan modules.example"
        )

        self.assertEqual(result, "plan-result")
        self.assertEqual(
            self.runtime.calls,
            [("plan", "modules.example")],
        )

    def test_predict_passes_module(self):
        result = self.router.execute(
            "engineering predict modules.example"
        )

        self.assertEqual(result, "predict-result")
        self.assertEqual(
            self.runtime.calls,
            [("predict", "modules.example")],
        )

    def test_risk_passes_module(self):
        result = self.router.execute(
            "engineering risk modules.example"
        )

        self.assertEqual(result, "risk-result")
        self.assertEqual(
            self.runtime.calls,
            [("risk", "modules.example")],
        )

    def test_explain_passes_module(self):
        result = self.router.execute(
            "engineering explain modules.example"
        )

        self.assertEqual(result, "explain-result")
        self.assertEqual(
            self.runtime.calls,
            [("explain", "modules.example")],
        )

    def test_advise_passes_module(self):
        result = self.router.execute(
            "engineering advise modules.example"
        )

        self.assertEqual(result, "advise-result")
        self.assertEqual(
            self.runtime.calls,
            [("advise", "modules.example")],
        )

    # ------------------------------------------------------
    # Completion
    # ------------------------------------------------------

    def test_complete_marks_module_through_runtime(self):
        result = self.router.execute(
            "engineering complete modules.example"
        )

        self.assertEqual(
            result,
            "Marked 'modules.example' as completed.",
        )

        self.assertEqual(
            self.runtime.calls,
            [("complete", "modules.example")],
        )

    # ------------------------------------------------------
    # Case normalization
    # ------------------------------------------------------

    def test_exact_command_is_case_insensitive(self):
        result = self.router.execute(
            "ENGINEERING DASHBOARD"
        )

        self.assertEqual(result, "dashboard-result")
        self.assertEqual(
            self.runtime.calls,
            [("dashboard",)],
        )

    def test_parameterized_command_prefix_is_case_insensitive(self):
        result = self.router.execute(
            "ENGINEERING SIMULATE modules.example"
        )

        self.assertEqual(result, "simulate-result")
        self.assertEqual(
            self.runtime.calls,
            [("simulate", "modules.example")],
        )

    # ------------------------------------------------------
    # Whitespace normalization
    # ------------------------------------------------------

    def test_exact_command_strips_surrounding_whitespace(self):
        result = self.router.execute(
            "   engineering dashboard   "
        )

        self.assertEqual(result, "dashboard-result")
        self.assertEqual(
            self.runtime.calls,
            [("dashboard",)],
        )

    def test_parameterized_command_strips_module_whitespace(self):
        result = self.router.execute(
            "engineering simulate   modules.example   "
        )

        self.assertEqual(result, "simulate-result")
        self.assertEqual(
            self.runtime.calls,
            [("simulate", "modules.example")],
        )

    # ------------------------------------------------------
    # Unsupported commands
    # ------------------------------------------------------

    def test_unknown_command_returns_none(self):
        result = self.router.execute(
            "engineering unknown"
        )

        self.assertIsNone(result)
        self.assertEqual(
            self.runtime.calls,
            [],
        )

    def test_similar_but_invalid_command_returns_none(self):
        result = self.router.execute(
            "engineering dashboard extra"
        )

        self.assertIsNone(result)
        self.assertEqual(
            self.runtime.calls,
            [],
        )


if __name__ == "__main__":
    unittest.main()