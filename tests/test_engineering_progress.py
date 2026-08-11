import unittest

from modules.engineering_progress import EngineeringProgressEngine


class MockPlanner:
    def generate(self):
        return [
            type("RoadmapItem", (), {
                "module": "modules.engineering_runtime"
            })(),
            type("RoadmapItem", (), {
                "module": "modules.engineering_memory"
            })(),
        ]


class MockHistory:
    def is_completed(self, module: str) -> bool:
        return module == "modules.engineering_runtime"


class TestEngineeringProgress(unittest.TestCase):

    def test_completed_runtime_module_is_counted(self):
        engine = EngineeringProgressEngine(
            MockPlanner(),
            MockHistory(),
        )

        progress = engine.calculate()

        self.assertEqual(progress.total_modules, 2)
        self.assertEqual(progress.completed_modules, 1)
        self.assertEqual(progress.remaining_modules, 1)
        self.assertEqual(progress.progress_percent, 50.0)


if __name__ == "__main__":
    unittest.main()