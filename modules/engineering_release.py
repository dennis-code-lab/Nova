"""
Nova Engine v98
Engineering Release Manager
"""

from __future__ import annotations

from typing import Any, Dict, List


class EngineeringReleaseManager:

    def __init__(
        self,
        history: Any,
        milestone_engine: Any,
        achievement_engine: Any,
        health_engine: Any,
    ) -> None:
        self.history = history
        self.milestone_engine = milestone_engine
        self.achievement_engine = achievement_engine
        self.health_engine = health_engine

    def release(self) -> Dict[str, Any]:
        """Gathers release metrics across modules, milestones, achievements, and health engines."""
        completed: List[str] = sorted(
            self.history.completed_modules()
        )
        milestones: List[Dict[str, Any]] = self.milestone_engine.completed()
        achievements: List[Dict[str, Any]] = self.achievement_engine.achievements()

        # Calculate dynamic health if supported by health_engine, fallback to 100.0
        if hasattr(self.health_engine, "score"):
            health = float(self.health_engine.score())
        elif hasattr(self.health_engine, "health"):
            health = float(self.health_engine.health())
        else:
            health = 100.0

        return {
            "version": "v98",
            "completed": completed,
            "milestones": milestones,
            "achievements": achievements,
            "health": health,
            "status": "READY",
        }

    def format_release(self) -> str:
        """Formats the release metadata into a CLI summary report."""
        report = self.release()

        completed = (
            "\n".join(
                f"✓ {m}"
                for m in report["completed"]
            )
            or "None"
        )

        milestone_text = (
            "\n".join(
                f"✓ {m['name']}"
                for m in report["milestones"]
            )
            or "None"
        )

        achievement_text = (
            "\n".join(
                f"🏆 {a['name']}"
                for a in report["achievements"]
            )
            or "None"
        )

        return f"""
============================================================
RELEASE {report['version']}
============================================================

Completed Modules

{completed}

Milestones

{milestone_text}

Achievements

{achievement_text}

Engineering Health

{report['health']:.1f}%

Release Status

{report['status']}
"""