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
        """Generates dynamic engineering insights."""

        analytics = self.analytics_engine.analytics()
        milestones = self.milestone_engine.milestone_progress()
        roadmap = self.planner.generate()

        completion = analytics["completion"]

        if completion < 25:
            phase = "Foundation Phase"
        elif completion < 60:
            phase = "Engineering Phase"
        else:
            phase = "Optimization Phase"

        next_module = (
            roadmap[0].module
            if roadmap
            else "None"
        )

        # Determine the current milestone
        current_milestone = "Complete"

        for milestone in milestones:
            if milestone["completed"] < milestone["total"]:
                current_milestone = milestone["name"]
                break

        # Generate a recommendation based on actual project state
        if not roadmap:
            recommendation = (
                "All roadmap modules are complete. "
                "Review the architecture and prepare the next engineering cycle."
            )
        elif completion < 25:
            recommendation = (
                f"Focus on the Foundation milestone by completing "
                f"{next_module} before expanding the system."
            )
        elif completion < 60:
            recommendation = (
                f"Continue Engineering Intelligence work, prioritizing "
                f"{next_module}."
            )
        else:
            recommendation = (
                f"Prioritize optimization and automation, starting with "
                f"{next_module}."
            )

        return {
            "phase": phase,
            "current_milestone": current_milestone,
            "completion": completion,
            "velocity": analytics["velocity"],
            "remaining": analytics["remaining"],
            "next_module": next_module,
            "sessions": analytics["remaining"],
            "recommendation": recommendation,
        }

    def format_report(self) -> str:
        """Formats dynamic engineering insights into a CLI report."""

        report = self.generate()

        return f"""
============================================================
ENGINEERING INSIGHTS
============================================================

Current Phase

{report['phase']}

Current Milestone

{report['current_milestone']}

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

{report['recommendation']}

============================================================
"""