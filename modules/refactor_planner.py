"""
Nova Engine v84
Refactor Planner

Generates safe engineering plans for modifying modules.

Author:
    Nova Engine
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from modules.change_predictor import ChangePredictor
from modules.risk_engine import RiskEngine


# ==========================================================
# Data Model
# ==========================================================

@dataclass
class RefactorPlan:
    target: str
    risk: str
    affected_modules: List[str] = field(default_factory=list)
    estimated_minutes: int = 0
    execution_steps: List[str] = field(default_factory=list)


# ==========================================================
# Planner
# ==========================================================

class RefactorPlanner:
    """
    Produces safe engineering execution plans.
    """

    def __init__(
        self,
        predictor: ChangePredictor,
        risk_engine: RiskEngine,
    ) -> None:
        self.predictor = predictor
        self.risk_engine = risk_engine

    # ------------------------------------------------------

    def create_plan(self, module_name: str) -> RefactorPlan:
        prediction = self.predictor.predict(module_name)

        if not prediction["found"]:
            raise ValueError(f"Unknown module: {module_name}")

        assessment = self.risk_engine.analyze(module_name)
        affected = prediction["affected_modules"]
        estimated = 3 + len(affected)

        steps = [
            "Create backup",
            f"Modify {module_name}",
            "Run dependency verification",
            "Run Change Predictor",
            "Run Risk Engine",
            "Run regression tests",
            "Commit changes",
        ]

        return RefactorPlan(
            target=module_name,
            risk=assessment.risk,
            affected_modules=affected,
            estimated_minutes=estimated,
            execution_steps=steps,
        )

    # ------------------------------------------------------

    def format_plan(self, module_name: str) -> str:
        plan = self.create_plan(module_name)

        lines = [
            "=" * 50,
            "SAFE REFACTOR PLAN",
            "=" * 50,
            "",
            f"Target : {plan.target}",
            f"Risk   : {plan.risk}",
            f"Estimated Time : {plan.estimated_minutes} minutes",
            "",
            "Affected Modules:",
        ]

        if plan.affected_modules:
            for module in plan.affected_modules:
                lines.append(f"  • {module}")
        else:
            lines.append("  None")

        lines.extend(
            [
                "",
                "Execution Plan",
                "-" * 50,
            ]
        )

        for i, step in enumerate(plan.execution_steps, start=1):
            lines.append(f"{i}. {step}")

        return "\n".join(lines)