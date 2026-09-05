"""
Nova Engine v133
Engineering Controller Tests

Verifies EngineeringController Git automation,
release metadata, dependency intelligence, and
legacy compatibility behavior.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from modules.analysis_report import AnalysisReport
from modules.dependency_analyzer import DependencyGraph
from modules.engineering_controller import EngineeringController
from modules.engineering_graph import EngineeringGraph


class TestEngineeringController(unittest.TestCase):

    def setUp(self):
        self.controller = EngineeringController()

    # =====================================================
    # Initialization
    # =====================================================

    def test_controller_can_be_created(self):
        self.assertIsInstance(
            self.controller,
            EngineeringController,
        )

    # =====================================================
    # Git Automation
    # =====================================================

    @patch("modules.engineering_controller.subprocess.run")
    def test_git_commit_patch_success(self, mock_run):
        add_result = Mock()
        commit_result = Mock()
        commit_result.stdout = "[develop abc123] test commit\n"

        mock_run.side_effect = [
            add_result,
            commit_result,
        ]

        result = self.controller.git_commit_patch("test commit")

        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)

    @patch("modules.engineering_controller.subprocess.run")
    def test_git_commit_patch_stages_all_changes(self, mock_run):
        mock_run.side_effect = [
            Mock(),
            Mock(stdout="[develop abc123] test commit\n"),
        ]

        self.controller.git_commit_patch("test commit")

        first_call = mock_run.call_args_list[0]
        self.assertEqual(
            first_call.args[0],
            ("git", "add", "."),
        )

    @patch("modules.engineering_controller.subprocess.run")
    def test_git_commit_patch_uses_commit_message(self, mock_run):
        mock_run.side_effect = [
            Mock(),
            Mock(stdout="[develop abc123] test commit\n"),
        ]

        self.controller.git_commit_patch("my message")

        second_call = mock_run.call_args_list[1]
        self.assertEqual(
            second_call.args[0],
            (
                "git",
                "commit",
                "-m",
                "[v84] my message",
            ),
        )

    @patch("modules.engineering_controller.subprocess.run")
    def test_git_commit_patch_returns_false_on_git_error(self, mock_run):
        import subprocess

        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=("git", "add", "."),
            stderr="git failure",
        )

        result = self.controller.git_commit_patch("test commit")

        self.assertFalse(result)

    @patch("modules.engineering_controller.subprocess.run")
    def test_git_commit_patch_handles_empty_stderr(self, mock_run):
        import subprocess

        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=("git", "commit", "-m", "[v84] test"),
            stderr="",
        )

        result = self.controller.git_commit_patch("test")

        self.assertFalse(result)

    @patch("modules.engineering_controller.subprocess.run")
    def test_git_commit_patch_executes_add_before_commit(self, mock_run):
        mock_run.side_effect = [
            Mock(),
            Mock(stdout="commit created\n"),
        ]

        self.controller.git_commit_patch("ordered")

        self.assertEqual(
            mock_run.call_args_list[0].args[0][0:2],
            ("git", "add"),
        )
        self.assertEqual(
            mock_run.call_args_list[1].args[0][0:2],
            ("git", "commit"),
        )

    # =====================================================
    # Release Management
    # =====================================================

    def test_generate_release_notes_returns_string(self):
        result = self.controller.generate_release_notes()

        self.assertIsInstance(result, str)

    def test_generate_release_notes_is_non_empty(self):
        result = self.controller.generate_release_notes()

        self.assertTrue(result)

    def test_generate_release_notes_contains_version(self):
        result = self.controller.generate_release_notes()

        self.assertIn("v84", result)

    def test_generate_release_notes_contains_dependency_intelligence(self):
        result = self.controller.generate_release_notes()

        self.assertIn(
            "Dependency Intelligence",
            result,
        )

    def test_generate_release_notes_exact_value(self):
        self.assertEqual(
            self.controller.generate_release_notes(),
            "Nova Engine v84 - Dependency Intelligence Layer",
        )

    # =====================================================
    # Dependency Intelligence Pipeline
    # =====================================================

    @patch("modules.engineering_controller.AnalysisReport")
    @patch("modules.engineering_controller.EngineeringGraphBuilder")
    @patch("modules.engineering_controller.ImpactEngine")
    @patch("modules.engineering_controller.DependencyAnalyzer")
    def test_analyze_dependencies_returns_report(
        self,
        mock_analyzer,
        mock_impact,
        mock_builder,
        mock_report,
    ):
        dependency_graph = Mock()
        dependency_graph.modules.return_value = []

        mock_analyzer.return_value.analyze.return_value = (
            dependency_graph
        )

        engineering_graph = Mock()
        mock_builder.return_value.build.return_value = (
            engineering_graph
        )

        mock_report.return_value.generate.return_value = (
            "engineering report"
        )

        result = self.controller.analyze_dependencies("workspace")

        self.assertEqual(result, "engineering report")

    @patch("modules.engineering_controller.AnalysisReport")
    @patch("modules.engineering_controller.EngineeringGraphBuilder")
    @patch("modules.engineering_controller.ImpactEngine")
    @patch("modules.engineering_controller.DependencyAnalyzer")
    def test_analyze_dependencies_creates_analyzer_with_workspace(
        self,
        mock_analyzer,
        mock_impact,
        mock_builder,
        mock_report,
    ):
        dependency_graph = Mock()
        dependency_graph.modules.return_value = []
        mock_analyzer.return_value.analyze.return_value = (
            dependency_graph
        )

        self.controller.analyze_dependencies("custom_workspace")

        mock_analyzer.assert_called_once_with(
            Path("custom_workspace")
        )

    @patch("modules.engineering_controller.AnalysisReport")
    @patch("modules.engineering_controller.EngineeringGraphBuilder")
    @patch("modules.engineering_controller.ImpactEngine")
    @patch("modules.engineering_controller.DependencyAnalyzer")
    def test_analyze_dependencies_calls_analyzer(
        self,
        mock_analyzer,
        mock_impact,
        mock_builder,
        mock_report,
    ):
        dependency_graph = Mock()
        dependency_graph.modules.return_value = []
        analyzer_instance = mock_analyzer.return_value
        analyzer_instance.analyze.return_value = dependency_graph

        self.controller.analyze_dependencies()

        analyzer_instance.analyze.assert_called_once_with()

    @patch("modules.engineering_controller.AnalysisReport")
    @patch("modules.engineering_controller.EngineeringGraphBuilder")
    @patch("modules.engineering_controller.ImpactEngine")
    @patch("modules.engineering_controller.DependencyAnalyzer")
    def test_analyze_dependencies_iterates_over_modules(
        self,
        mock_analyzer,
        mock_impact,
        mock_builder,
        mock_report,
    ):
        dependency_graph = Mock()
        dependency_graph.modules.return_value = [
            "modules.alpha",
            "modules.beta",
            "modules.gamma",
        ]
        mock_analyzer.return_value.analyze.return_value = (
            dependency_graph
        )

        self.controller.analyze_dependencies()

        self.assertEqual(
            mock_impact.call_count,
            3,
        )

    @patch("modules.engineering_controller.AnalysisReport")
    @patch("modules.engineering_controller.EngineeringGraphBuilder")
    @patch("modules.engineering_controller.ImpactEngine")
    @patch("modules.engineering_controller.DependencyAnalyzer")
    def test_analyze_dependencies_analyzes_each_module(
        self,
        mock_analyzer,
        mock_impact,
        mock_builder,
        mock_report,
    ):
        dependency_graph = Mock()
        modules = [
            "modules.alpha",
            "modules.beta",
        ]
        dependency_graph.modules.return_value = modules
        mock_analyzer.return_value.analyze.return_value = (
            dependency_graph
        )

        impact_instances = [
            Mock(),
            Mock(),
        ]
        mock_impact.side_effect = impact_instances

        self.controller.analyze_dependencies()

        impact_instances[0].analyze.assert_called_once_with(
            "modules.alpha"
        )
        impact_instances[1].analyze.assert_called_once_with(
            "modules.beta"
        )

    @patch("modules.engineering_controller.AnalysisReport")
    @patch("modules.engineering_controller.EngineeringGraphBuilder")
    @patch("modules.engineering_controller.ImpactEngine")
    @patch("modules.engineering_controller.DependencyAnalyzer")
    def test_analyze_dependencies_builds_engineering_graph(
        self,
        mock_analyzer,
        mock_impact,
        mock_builder,
        mock_report,
    ):
        dependency_graph = Mock()
        dependency_graph.modules.return_value = []
        mock_analyzer.return_value.analyze.return_value = (
            dependency_graph
        )

        self.controller.analyze_dependencies()

        mock_builder.assert_called_once()
        mock_builder.return_value.build.assert_called_once_with(
            {}
        )

    @patch("modules.engineering_controller.AnalysisReport")
    @patch("modules.engineering_controller.EngineeringGraphBuilder")
    @patch("modules.engineering_controller.ImpactEngine")
    @patch("modules.engineering_controller.DependencyAnalyzer")
    def test_analyze_dependencies_passes_dependency_graph_to_builder(
        self,
        mock_analyzer,
        mock_impact,
        mock_builder,
        mock_report,
    ):
        dependency_graph = Mock()
        dependency_graph.modules.return_value = []
        mock_analyzer.return_value.analyze.return_value = (
            dependency_graph
        )

        self.controller.analyze_dependencies()

        mock_builder.assert_called_once_with(
            dependency_graph
        )

    @patch("modules.engineering_controller.AnalysisReport")
    @patch("modules.engineering_controller.EngineeringGraphBuilder")
    @patch("modules.engineering_controller.ImpactEngine")
    @patch("modules.engineering_controller.DependencyAnalyzer")
    def test_analyze_dependencies_creates_report(
        self,
        mock_analyzer,
        mock_impact,
        mock_builder,
        mock_report,
    ):
        dependency_graph = Mock()
        dependency_graph.modules.return_value = []
        mock_analyzer.return_value.analyze.return_value = (
            dependency_graph
        )

        engineering_graph = Mock()
        mock_builder.return_value.build.return_value = (
            engineering_graph
        )

        self.controller.analyze_dependencies()

        mock_report.assert_called_once_with(
            engineering_graph
        )

    @patch("modules.engineering_controller.AnalysisReport")
    @patch("modules.engineering_controller.EngineeringGraphBuilder")
    @patch("modules.engineering_controller.ImpactEngine")
    @patch("modules.engineering_controller.DependencyAnalyzer")
    def test_analyze_dependencies_generates_report(
        self,
        mock_analyzer,
        mock_impact,
        mock_builder,
        mock_report,
    ):
        dependency_graph = Mock()
        dependency_graph.modules.return_value = []
        mock_analyzer.return_value.analyze.return_value = (
            dependency_graph
        )

        mock_report.return_value.generate.return_value = (
            "generated report"
        )

        result = self.controller.analyze_dependencies()

        mock_report.return_value.generate.assert_called_once_with()
        self.assertEqual(result, "generated report")

    @patch("modules.engineering_controller.AnalysisReport")
    @patch("modules.engineering_controller.EngineeringGraphBuilder")
    @patch("modules.engineering_controller.ImpactEngine")
    @patch("modules.engineering_controller.DependencyAnalyzer")
    def test_analyze_dependencies_preserves_analysis_results(
        self,
        mock_analyzer,
        mock_impact,
        mock_builder,
        mock_report,
    ):
        dependency_graph = Mock()
        modules = [
            "modules.alpha",
            "modules.beta",
        ]
        dependency_graph.modules.return_value = modules
        mock_analyzer.return_value.analyze.return_value = (
            dependency_graph
        )

        alpha_analysis = Mock()
        beta_analysis = Mock()

        first_impact = Mock()
        first_impact.analyze.return_value = alpha_analysis

        second_impact = Mock()
        second_impact.analyze.return_value = beta_analysis

        mock_impact.side_effect = [
            first_impact,
            second_impact,
        ]

        self.controller.analyze_dependencies()

        mock_builder.return_value.build.assert_called_once_with(
            {
                "modules.alpha": alpha_analysis,
                "modules.beta": beta_analysis,
            }
        )

    # =====================================================
    # Legacy Compatibility
    # =====================================================

    def test_improve_target_raises_for_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            self.controller.improve_target(
                "missing-file-does-not-exist.py"
            )

    def test_improve_target_no_change_when_no_bare_except(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "example.py"
            original = (
                "def add(a, b):\n"
                "    return a + b\n"
            )
            target.write_text(
                original,
                encoding="utf-8",
            )

            result = self.controller.improve_target(
                str(target)
            )

            self.assertTrue(result["success"])
            self.assertFalse(result["applied"])
            self.assertEqual(
                target.read_text(encoding="utf-8"),
                original,
            )

    def test_improve_target_replaces_bare_except(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "example.py"
            target.write_text(
                "try:\n"
                "    pass\n"
                "except:\n"
                "    pass\n",
                encoding="utf-8",
            )

            result = self.controller.improve_target(
                str(target)
            )

            self.assertTrue(result["success"])
            self.assertTrue(result["applied"])
            self.assertIn(
                "except Exception:",
                target.read_text(encoding="utf-8"),
            )

    def test_improve_target_replaces_multiple_bare_excepts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "example.py"
            target.write_text(
                "try:\n"
                "    pass\n"
                "except:\n"
                "    pass\n"
                "\n"
                "try:\n"
                "    pass\n"
                "except:\n"
                "    pass\n",
                encoding="utf-8",
            )

            result = self.controller.improve_target(
                str(target)
            )

            updated = target.read_text(
                encoding="utf-8"
            )

            self.assertTrue(result["applied"])
            self.assertEqual(
                updated.count("except Exception:"),
                2,
            )

    def test_improve_target_preserves_auto_approve_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "example.py"
            target.write_text(
                "try:\n"
                "    pass\n"
                "except:\n"
                "    pass\n",
                encoding="utf-8",
            )

            result = self.controller.improve_target(
                str(target),
                auto_approve=False,
            )

            self.assertFalse(result["auto_approved"])

    def test_improve_target_preserves_auto_approve_true(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "example.py"
            target.write_text(
                "try:\n"
                "    pass\n"
                "except:\n"
                "    pass\n",
                encoding="utf-8",
            )

            result = self.controller.improve_target(
                str(target),
                auto_approve=True,
            )

            self.assertTrue(result["auto_approved"])

    def test_improve_target_returns_expected_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "example.py"
            target.write_text(
                "def add(a, b):\n"
                "    return a + b\n",
                encoding="utf-8",
            )

            result = self.controller.improve_target(
                str(target)
            )

            self.assertEqual(
                result["status"],
                "completed",
            )

    def test_improve_target_returns_target_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "example.py"
            target.write_text(
                "def add(a, b):\n"
                "    return a + b\n",
                encoding="utf-8",
            )

            result = self.controller.improve_target(
                str(target)
            )

            self.assertEqual(
                result["target"],
                str(target),
            )

    def test_improve_target_returns_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "example.py"
            target.write_text(
                "def add(a, b):\n"
                "    return a + b\n",
                encoding="utf-8",
            )

            result = self.controller.improve_target(
                str(target)
            )

            self.assertTrue(result["success"])

    def test_improve_target_returns_message(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "example.py"
            target.write_text(
                "def add(a, b):\n"
                "    return a + b\n",
                encoding="utf-8",
            )

            result = self.controller.improve_target(
                str(target)
            )

            self.assertEqual(
                result["message"],
                "Legacy compatibility execution completed.",
            )


if __name__ == "__main__":
    unittest.main()