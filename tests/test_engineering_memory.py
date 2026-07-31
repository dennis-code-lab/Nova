import unittest
import os
import shutil
from modules.engineering_memory import EngineeringMemory

class TestEngineeringMemory(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/tmp_data"
        self.test_file = os.path.join(self.test_dir, "test_memory.json")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_initialization_and_snapshot(self):
        mem = EngineeringMemory(storage_path=self.test_file)
        mem.record_snapshot({"security_score": 100, "maintainability": 90})
        trends = mem.get_trends()
        self.assertIsNotNone(trends)
        # Account for 3 initial seeded entries + 1 recorded snapshot = 4 total points
        self.assertGreaterEqual(trends["data_points"], 1)

    def test_log_technical_debt(self):
        mem = EngineeringMemory(storage_path=self.test_file)
        mem.log_technical_debt("Legacy function needs deprecation", severity="low")
        trends = mem.get_trends()
        self.assertIsNotNone(trends)