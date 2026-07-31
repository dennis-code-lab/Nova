"""
Nova Engine v84
Integration Tests - Change Predictor

Validates end-to-end impact prediction against dynamic workspace files created via DependencyAnalyzer.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from modules.change_predictor import ChangePredictor
from modules.dependency_analyzer import DependencyAnalyzer
from modules.engineering_graph import EngineeringGraphBuilder
from modules.impact_engine import ImpactEngine


class TestChangePredictorIntegration(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)

        modules = root / "modules"
        modules.mkdir()

        (modules / "ai.py").write_text("", encoding="utf-8")

        (modules / "dialogue.py").write_text(
            "import modules.ai", encoding="utf-8"
        )

        (root / "nova_gui.py").write_text(
            "import modules.ai", encoding="utf-8"
        )

        analyzer = DependencyAnalyzer(root)
        dependency_graph = analyzer.analyze()

        analyses = {}
        engine = ImpactEngine(dependency_graph)

        for module in dependency_graph.modules():
            analyses[module] = engine.analyze(module)

        engineering_graph = EngineeringGraphBuilder(
            dependency_graph
        ).build(analyses)

        self.predictor = ChangePredictor(engineering_graph)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_existing_module(self) -> None:
        result = self.predictor.predict("modules.ai")

        self.assertTrue(result["found"])
        self.assertGreaterEqual(result["affected_count"], 2)

    def test_missing_module(self) -> None:
        result = self.predictor.predict("modules.fake")

        self.assertFalse(result["found"])
        self.assertEqual(result["affected_count"], 0)


if __name__ == "__main__":
    unittest.main()