"""
Nova Engine v84
Engineering Orchestrator

Coordinates Nova's engineering intelligence pipeline.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from modules.change_predictor import ChangePredictor
from modules.refactor_planner import RefactorPlanner
from modules.risk_engine import RiskEngine


# ==========================================================
# Data Model
# ==========================================================

@dataclass
class EngineeringReport:
    target: str
    risk: str
    affected_modules: List[str]
    estimated_minutes: int
    execution_steps: List[str]


# ==========================================================
# Engineering Orchestrator
# ==========================================================

class EngineeringOrchestrator:
    """
    Coordinates the engineering workflow.
    """

    def __init__(
        self,
        predictor: ChangePredictor,
        risk_engine: RiskEngine,
        planner: RefactorPlanner,
    ) -> None:
        self.predictor = predictor
        self.risk_engine = risk_engine
        self.planner = planner

    # ------------------------------------------------------

    def analyze_request(self, module_name: str) -> EngineeringReport:
        """
        Execute the engineering pipeline for a module.
        """
        plan = self.planner.create_plan(module_name)

        return EngineeringReport(
            target=plan.target,
            risk=plan.risk,
            affected_modules=plan.affected_modules,
            estimated_minutes=plan.estimated_minutes,
            execution_steps=plan.execution_steps,
        )

    # ------------------------------------------------------

    def format_report(self, module_name: str) -> str:
        """
        Produce a readable engineering report.
        """
        report = self.analyze_request(module_name)

        lines = [
            "=" * 55,
            "NOVA ENGINEERING REPORT",
            "=" * 55,
            "",
            f"Target Module : {report.target}",
            f"Risk Level    : {report.risk}",
            f"Estimated Time: {report.estimated_minutes} minutes",
            "",
            "Affected Modules:",
        ]

        if report.affected_modules:
            for module in report.affected_modules:
                lines.append(f"  • {module}")
        else:
            lines.append("  None")

        lines.extend([
            "",
            "Execution Workflow",
            "-" * 55,
        ])

        for index, step in enumerate(report.execution_steps, start=1):
            lines.append(f"{index}. {step}")

        lines.extend([
            "",
            "=" * 55,
            "Engineering analysis complete.",
            "=" * 55,
        ])

        return "\n".join(lines)