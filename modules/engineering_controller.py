"""
Nova Engine v84
Engineering Controller

Orchestrates automated Git operations, release metadata generation,
and the v84 Dependency Intelligence pipeline.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from modules.analysis_report import AnalysisReport
from modules.dependency_analyzer import DependencyAnalyzer
from modules.engineering_graph import EngineeringGraphBuilder
from modules.impact_engine import ImpactEngine


class EngineeringController:

    def __init__(self) -> None:
        pass

    # =====================================================
    # Git Automation
    # =====================================================

    def git_commit_patch(self, commit_message: str) -> bool:
        """
        Stage all changes and execute a standardized Git commit.
        """
        try:
            subprocess.run(
                ("git", "add", "."),
                check=True,
                capture_output=True,
            )

            result = subprocess.run(
                (
                    "git",
                    "commit",
                    "-m",
                    f"[v84] {commit_message}",
                ),
                check=True,
                capture_output=True,
                text=True,
            )

            lines = result.stdout.splitlines()
            first_line = lines[0] if lines else "Commit completed"

            print(f"[OK] Git Commit Created: {first_line}")
            return True

        except subprocess.CalledProcessError as e:
            out = (
                e.stderr.strip()
                if e.stderr
                else "No changes to commit"
            )
            print(f"[WARNING] Git commit skipped: {out}")
            return False

    # =====================================================
    # Release Management
    # =====================================================

    def generate_release_notes(self) -> str:
        """
        Return active release notes summary for v84.
        """
        return "Nova Engine v84 - Dependency Intelligence Layer"

    # =====================================================
    # v84 Dependency Intelligence Pipeline
    # =====================================================

    def analyze_dependencies(self, workspace: str = ".") -> str:
        """
        Execute the complete Dependency Intelligence pipeline across the target workspace.
        """
        analyzer = DependencyAnalyzer(Path(workspace))
        dependency_graph = analyzer.analyze()

        analyses = {}
        for module in dependency_graph.modules():
            engine = ImpactEngine(dependency_graph)
            analyses[module] = engine.analyze(module)

        engineering_graph = EngineeringGraphBuilder(
            dependency_graph
        ).build(analyses)

        report = AnalysisReport(engineering_graph)
        return report.generate()

    # =====================================================
    # Legacy Compatibility (v82 Regression Suite)
    # =====================================================

    def improve_target(self, target: str, auto_approve: bool = False) -> Dict[str, Any]:
        """
        Legacy compatibility implementation used by the v82 regression
        suite.

        Performs one safe automated refactor:
        - replaces bare 'except:' with 'except Exception:'
        """
        target_path = Path(target)

        if not target_path.exists():
            raise FileNotFoundError(target)

        original = target_path.read_text(encoding="utf-8")

        updated = original.replace(
            "except:",
            "except Exception:"
        )

        applied = updated != original

        if applied:
            target_path.write_text(updated, encoding="utf-8")

        return {
            "success": True,
            "applied": applied,
            "target": str(target_path),
            "auto_approved": auto_approve,
            "status": "completed",
            "message": "Legacy compatibility execution completed.",
        }