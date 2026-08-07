"""
Nova Engine v100
Engineering Insights Engine

Generates intelligent engineering observations based on
analytics, milestones, roadmap and sprint progress.
"""

from __future__ import annotations

from typing import Any, Dict


class EngineeringInsights:

    def __init__(
        self,
        analytics_engine: Any,
        milestone_engine: Any,
        planner: Any,
    ) -> None:
        self.analytics_engine = analytics_engine
        self.milestone_engine = milestone_engine
        self.planner = planner

    def generate(self) -> Dict[str, Any]:
        """Generates engineering insights including current project phase, next module, and estimated remaining sessions."""
        analytics = self.analytics_engine.analytics()

        milestones = self.milestone_engine.milestone_progress()

        roadmap = self.planner.generate()

        if analytics["completion"] < 25:
            phase = "Foundation Phase"
        elif analytics["completion"] < 60:
            phase = "Engineering Phase"
        else:
            phase = "Optimization Phase"

        next_module = (
            roadmap[0].module
            if roadmap
            else "None"
        )

        sessions_remaining = analytics["remaining"]

        return {
            "phase": phase,
            "completion": analytics["completion"],
            "velocity": analytics["velocity"],
            "remaining": analytics["remaining"],
            "next_module": next_module,
            "sessions": sessions_remaining,
        }

    def format_report(self) -> str:
        """Formats the generated insights into a CLI summary report."""
        report = self.generate()

        return f"""
============================================================
ENGINEERING INSIGHTS
============================================================

Current Phase

{report['phase']}

Completion

{report['completion']:.1f}%

Engineering Velocity

{report['velocity']} module(s)

Remaining Modules

{report['remaining']}

Recommended Next Module

{report['next_module']}

Estimated Sessions Remaining

{report['sessions']}

Recommendation

Complete the current highest-priority module before
moving to lower-priority engineering work.
"""