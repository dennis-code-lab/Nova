import unittest
import os
import json
from modules.engineering_planner import EngineeringPlanner
from modules.decision_engine import DecisionEngine
from modules.engineering_controller import EngineeringController

class TestNovaV83Suite(unittest.TestCase):
    def setUp(self):
        self.planner = EngineeringPlanner(roadmap_path='data/test_roadmap.json')
        self.adr = DecisionEngine(data_path='data/test_decisions.json')
        self.controller = EngineeringController()

    def tearDown(self):
        for path in ['data/test_roadmap.json', 'data/test_decisions.json']:
            if os.path.exists(path):
                os.remove(path)

    def test_planner_add_and_complete_task(self):
        task = self.planner.add_task("Test Integration Pipeline")
        self.assertEqual(task["title"], "Test Integration Pipeline")
        self.assertEqual(task["status"], "BACKLOG")

        next_t = self.planner.get_next_task()
        self.assertIsNotNone(next_t)

    def test_decision_record_lifecycle(self):
        record = self.adr.create_decision("Test Architecture", "Use JSON", "Zero dependencies", "Low scalability")
        self.assertEqual(record["id"], "ADR-001")
        fetched = self.adr.get_decision("ADR-001")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["decision"], "Use JSON")

    def test_controller_release_notes(self):
        notes = self.controller.generate_release_notes()
        self.assertIn("Nova Engine", notes)

if __name__ == '__main__':
    unittest.main()
