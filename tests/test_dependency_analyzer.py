"""
Nova Engine v84
Dependency Intelligence Layer - Test Suite

test_dependency_analyzer.py
"""

import unittest
import tempfile
from pathlib import Path

from modules.dependency_analyzer import DependencyAnalyzer


class TestDependencyAnalyzer(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)

        (self.workspace / "main.py").write_text(
            "import os\n"
            "import sys\n"
            "from modules import memory\n",
            encoding="utf-8",
        )

        (self.workspace / "helper.py").write_text(
            "import json\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_analyze_workspace(self):
        analyzer = DependencyAnalyzer(self.workspace)
        graph = analyzer.analyze()

        self.assertEqual(graph.total_modules(), 2)

        self.assertIn("main", graph.graph)
        self.assertIn("helper", graph.graph)

    def test_detect_imports(self):
        analyzer = DependencyAnalyzer(self.workspace)
        graph = analyzer.analyze()

        deps = graph.dependencies_of("main")

        self.assertIn("os", deps)
        self.assertIn("sys", deps)
        self.assertIn("modules", deps)

    def test_helper_import(self):
        analyzer = DependencyAnalyzer(self.workspace)
        graph = analyzer.analyze()

        deps = graph.dependencies_of("helper")

        self.assertEqual(deps, {"json"})


if __name__ == "__main__":
    unittest.main()