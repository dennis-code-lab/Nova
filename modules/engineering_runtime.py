"""
Nova Engine v90
Engineering Runtime

Central runtime responsible for initializing and exposing
Nova's Engineering Intelligence subsystem.

Author:
    Nova Engine
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from modules.change_predictor import ChangePredictor
from modules.dependency_analyzer import DependencyAnalyzer
from modules.engineering_advisor import EngineeringAdvisor
from modules.engineering_decision_engine import EngineeringDecisionEngine
from modules.engineering_evidence import EngineeringEvidenceEngine
from modules.engineering_explainer import EngineeringExplainer
from modules.engineering_forecast import EngineeringForecastEngine
from modules.engineering_graph import EngineeringGraphBuilder
from modules.engineering_health import EngineeringHealth
from modules.engineering_history import EngineeringHistory
from modules.engineering_memory import EngineeringMemory
from modules.engineering_orchestrator import EngineeringOrchestrator
from modules.engineering_overview import EngineeringOverview
from modules.engineering_planner_v2 import AutonomousEngineeringPlanner
from modules.engineering_score import EngineeringScoreEngine
from modules.engineering_simulator import EngineeringSimulator
from modules.impact_engine import ImpactEngine
from modules.refactor_planner import RefactorPlanner
from modules.risk_engine import RiskAssessment, RiskEngine


class EngineeringRuntime:
    """
    Initializes the Engineering Intelligence stack once and
    provides access to all engineering services.
    """

    def __init__(self, workspace: str | Path = ".") -> None:
        self.workspace = Path(workspace)

        # ---------------------------------------------
        # Persistent Storage & Memory (Dependency Injection)
        # ---------------------------------------------
        memory_file = str(self.workspace / "data" / "engineering_memory.json")
        self.memory = EngineeringMemory(storage_path=memory_file)
        self.history = EngineeringHistory(self.memory)

        # ---------------------------------------------
        # Build Dependency Graph
        # ---------------------------------------------
        analyzer = DependencyAnalyzer(self.workspace)
        dependency_graph = analyzer.analyze()

        analyses = {}
        impact_engine = ImpactEngine(dependency_graph)

        for module in dependency_graph.modules():
            analyses[module] = impact_engine.analyze(module)

        engineering_graph = EngineeringGraphBuilder(
            dependency_graph
        ).build(analyses)

        # ---------------------------------------------
        # Core Services
        # ---------------------------------------------
        self.predictor = ChangePredictor(engineering_graph)

        self.risk_engine = RiskEngine(engineering_graph)

        self.score_engine = EngineeringScoreEngine(
            engineering_graph,
            self.risk_engine,
        )

        self.evidence_engine = EngineeringEvidenceEngine(
            engineering_graph,
            self.predictor,
            self.risk_engine,
        )

        self.explainer = EngineeringExplainer(
            self.score_engine,
            self.risk_engine,
            self.evidence_engine,
        )

        self.advisor = EngineeringAdvisor(
            self.score_engine,
            self.evidence_engine,
        )

        self.autonomous_planner = AutonomousEngineeringPlanner(
            engineering_graph,
            self.score_engine,
            self.advisor,
        )

        self.health_engine = EngineeringHealth(
            engineering_graph,
            self.risk_engine,
        )

        self.forecast_engine = EngineeringForecastEngine(
            self.autonomous_planner,
            self.health_engine,
        )

        self.simulator = EngineeringSimulator(
            self.score_engine,
            self.risk_engine,
            self.forecast_engine,
        )

        self.decision_engine = EngineeringDecisionEngine(
            self.autonomous_planner,
            self.advisor,
            self.simulator,
            self.forecast_engine,
            self.history,
        )

        self.refactor_planner = RefactorPlanner(
            self.predictor,
            self.risk_engine,
        )

        self.orchestrator = EngineeringOrchestrator(
            self.predictor,
            self.risk_engine,
            self.refactor_planner,
        )

        self.overview_engine = EngineeringOverview(
            engineering_graph,
            self.risk_engine,
        )

    # -------------------------------------------------

    def report(self, module: str) -> str:
        return self.orchestrator.format_report(module)

    def plan(self, module: str) -> str:
        return self.refactor_planner.format_plan(module)

    def predict(self, module: str) -> Dict[str, Any]:
        return self.predictor.predict(module)

    def risk(self, module: str) -> RiskAssessment:
        return self.risk_engine.analyze(module)

    def overview(self) -> str:
        """Generate a project-wide engineering overview."""
        return self.overview_engine.generate()

    def explain(self, module: str) -> str:
        """Generate a human-readable engineering explanation for a module."""
        return self.explainer.explain(module)

    def advise(self, module: str) -> str:
        return self.advisor.format_advice(module)

    def roadmap(self) -> str:
        return self.autonomous_planner.format_roadmap()

    def forecast(self) -> str:
        return self.forecast_engine.format_forecast()

    def simulate(self, module: str) -> str:
        return self.simulator.format_simulation(module)

    def decision(self) -> str:
        return self.decision_engine.format_decision()

    def complete(self, module: str) -> None:
        self.history.complete(module)